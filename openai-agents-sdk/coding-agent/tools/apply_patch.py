import hashlib
import os
from pathlib import Path
from dotenv import load_dotenv

from agents.editor import ApplyPatchOperation, ApplyPatchResult
from agents import (
    ApplyPatchTool,
)

load_dotenv()


class ApprovalTracker:
    """Tracks which apply_patch operations have already been approved."""

    def __init__(self) -> None:
        self._approved: set[str] = set()

    def fingerprint(self, operation: ApplyPatchOperation, relative_path: str) -> str:
        hasher = hashlib.sha256()
        hasher.update(operation.type.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(relative_path.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update((operation.diff or "").encode("utf-8"))
        return hasher.hexdigest()

    def remember(self, fingerprint: str) -> None:
        self._approved.add(fingerprint)

    def is_approved(self, fingerprint: str) -> bool:
        return fingerprint in self._approved


class WorkspaceEditor:
    """
    Minimal editor for the apply_patch tool:
    - keeps all edits under `root`
    - optional manual approval (APPLY_PATCH_AUTO_APPROVE=1 to skip prompts)
    """

    def __init__(
        self, root: Path, approvals: ApprovalTracker, auto_approve: bool = False
    ) -> None:
        self._root = root.resolve()
        self._approvals = approvals
        self._auto_approve = (
            auto_approve or os.environ.get("APPLY_PATCH_AUTO_APPROVE") == "1"
        )

    def create_file(self, operation: ApplyPatchOperation) -> ApplyPatchResult:
        relative = self._relative_path(operation.path)
        self._require_approval(operation, relative)
        target = self._resolve(operation.path, ensure_parent=True)
        diff = operation.diff or ""
        content = apply_unified_diff("", diff, create=True)
        target.write_text(content, encoding="utf-8")
        return ApplyPatchResult(output=f"Created {relative}")

    def update_file(self, operation: ApplyPatchOperation) -> ApplyPatchResult:
        relative = self._relative_path(operation.path)
        self._require_approval(operation, relative)
        target = self._resolve(operation.path)
        original = target.read_text(encoding="utf-8")
        diff = operation.diff or ""
        patched = apply_unified_diff(original, diff)
        target.write_text(patched, encoding="utf-8")
        return ApplyPatchResult(output=f"Updated {relative}")

    def delete_file(self, operation: ApplyPatchOperation) -> ApplyPatchResult:
        relative = self._relative_path(operation.path)
        self._require_approval(operation, relative)
        target = self._resolve(operation.path)
        target.unlink(missing_ok=True)
        return ApplyPatchResult(output=f"Deleted {relative}")

    def _relative_path(self, value: str) -> str:
        resolved = self._resolve(value)
        return resolved.relative_to(self._root).as_posix()

    def _resolve(self, relative: str, ensure_parent: bool = False) -> Path:
        candidate = Path(relative)
        target = candidate if candidate.is_absolute() else (self._root / candidate)
        target = target.resolve()
        try:
            target.relative_to(self._root)
        except ValueError:
            raise RuntimeError(f"Operation outside workspace: {relative}") from None
        if ensure_parent:
            target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def _require_approval(
        self, operation: ApplyPatchOperation, display_path: str
    ) -> None:
        fingerprint = self._approvals.fingerprint(operation, display_path)
        if self._auto_approve or self._approvals.is_approved(fingerprint):
            self._approvals.remember(fingerprint)
            return

        print("\n[apply_patch] approval required")
        print(f"- type: {operation.type}")
        print(f"- path: {display_path}")
        if operation.diff:
            preview = (
                operation.diff
                if len(operation.diff) < 400
                else f"{operation.diff[:400]}…"
            )
            print("- diff preview:\n", preview)
        answer = input("Proceed? [y/N] ").strip().lower()
        if answer not in {"y", "yes"}:
            raise RuntimeError("Apply patch operation rejected by user.")
        self._approvals.remember(fingerprint)


def apply_unified_diff(original: str, diff: str, create: bool = False) -> str:
    """
    Simple "diff" applier (adapt this based on your environment)

    - For create_file, the diff can be the full desired file contents,
      optionally with leading '+' on each line.
    - For update_file, we treat the diff as the new file contents:
      keep lines starting with ' ' or '+', drop '-' lines and diff headers.

    This avoids context/delete mismatch errors while still letting the model
    send familiar diff-like patches.
    """
    if not diff:
        return original

    lines = diff.splitlines()
    body: list[str] = []

    for line in lines:
        if not line:
            body.append("")
            continue

        # Skip typical unified diff headers / metadata
        if line.startswith("@@") or line.startswith("---") or line.startswith("+++"):
            continue

        prefix = line[0]
        content = line[1:]

        if prefix in ("+", " "):
            body.append(content)
        elif prefix in ("-", "\\"):
            # skip deletions and "\ No newline at end of file"
            continue
        else:
            # If it doesn't look like diff syntax, keep the full line
            body.append(line)

    text = "\n".join(body)
    if diff.endswith("\n"):
        text += "\n"
    return text


workspace_dir = Path("workspace_dir").resolve()
workspace_dir.mkdir(exist_ok=True)

approvals = ApprovalTracker()
editor = WorkspaceEditor(root=workspace_dir, approvals=approvals, auto_approve=True)

apply_patch_tool = ApplyPatchTool(editor=editor)


# Optional: set CONTEXT7_API_KEY in your environment for higher rate limits
CONTEXT7_API_KEY = os.getenv("CONTEXT7_API_KEY")


from agents import HostedMCPTool

context7_tool = HostedMCPTool(
    tool_config={
        "type": "mcp",
        "server_label": "context7",
        "server_url": "https://mcp.context7.com/mcp",
        # Basic usage works without auth; for higher rate limits, pass your key here.
        **({"authorization": f"Bearer {CONTEXT7_API_KEY}"} if CONTEXT7_API_KEY else {}),
        "require_approval": "never",
    },
)
