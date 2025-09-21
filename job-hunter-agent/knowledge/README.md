# CrewAI `knowledge/` 폴더 가이드 (README)

이 문서는 CrewAI에서 **Knowledge 기능**과 프로젝트 루트의 **`knowledge/` 폴더**가 담당하는 역할을 실무 중심으로 요약·정리한 README입니다. 초심자도 바로 적용할 수 있도록 개념 → 설치/구성 → 사용법 → 고급 기능 → 트러블슈팅 순으로 정리했습니다.

---

## 1) Knowledge란?

**Knowledge**는 에이전트가 작업 중 **외부 정보원(문서/웹/데이터 파일 등)**을 참고할 수 있게 하는 시스템입니다. 쉽게 말해, **에이전트에게 참조용 도서관**을 붙여주는 개념입니다.

**주요 이점**

- 도메인 지식 보강: 특정 분야 자료를 사전에 로드해 정답률 향상
- 현실 데이터 기반 의사결정: 문헌/파일/웹 자료를 근거로 답변 생성
- 컨텍스트 유지: 대화 흐름과 함께 지식 기반 유지
- 환각 감소: **사실적 근거**에 기반한 응답 유도

---

## 2) `knowledge/` 폴더의 역할

- 프로젝트 루트에 **`knowledge/`** 디렉터리를 만들고, 참고할 **텍스트/문서/데이터 파일**을 여기에 모아두면 CrewAI가 이를 벡터화하여 검색합니다.
- **경로 표기 주의**: Knowledge Source 생성 시, **`knowledge/` 기준의 상대경로**를 사용합니다.
- 저장소(ChromaDB) 메타데이터와 임베딩은 OS별 **플랫폼 경로**에 보관되며(자세한 경로는 아래 7장), 필요 시 환경변수로 **커스텀 저장 위치**를 지정할 수 있습니다.

> 요약: **문서는 `knowledge/`에**, **저장·색인은 ChromaDB에**. 문서의 원본과 임베딩 저장은 분리됩니다.

---

## 3) 빠른 시작 (Quickstart)

### (1) 폴더 준비

```bash
# 프로젝트 루트에서
mkdir -p knowledge
# 여기에 .txt/.pdf/.csv/.xlsx/.json 등 파일을 넣습니다.
```

### (2) 기본 예시 – 문자열 지식 로드

```python
from crewai import Agent, Task, Crew, Process, LLM
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

content = "Users name is John. He is 30 years old and lives in San Francisco."
string_source = StringKnowledgeSource(content=content)

llm = LLM(model="gpt-4o-mini", temperature=0)

agent = Agent(
    role="About User",
    goal="You know everything about the user.",
    backstory="You are a master at understanding people and their preferences.",
    verbose=True,
    allow_delegation=False,
    llm=llm,
)

task = Task(
    description="Answer the following questions about the user: {question}",
    expected_output="An answer to the question.",
    agent=agent,
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True,
    process=Process.sequential,
    knowledge_sources=[string_source],  # ← 지식 활성화
)

result = crew.kickoff(inputs={"question": "What city does John live in and how old is he?"})
```

### (3) 웹 문서 로드(※ docling 필요)

```bash
uv add docling
```

```python
from crewai import LLM, Agent, Crew, Process, Task
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource

content_source = CrewDoclingSource(
    file_paths=[
        "https://lilianweng.github.io/posts/2024-11-28-reward-hacking",
        "https://lilianweng.github.io/posts/2024-07-07-hallucination",
    ],
)

llm = LLM(model="gpt-4o-mini", temperature=0)

agent = Agent(
    role="About papers",
    goal="You know everything about the papers.",
    backstory="You are a master at understanding papers and their content.",
    verbose=True,
    allow_delegation=False,
    llm=llm,
)

task = Task(
    description="Answer the following questions about the papers: {question}",
    expected_output="An answer to the question.",
    agent=agent,
)

crew = Crew(
    agents=[agent],
    tasks=[task],
    verbose=True,
    process=Process.sequential,
    knowledge_sources=[content_source],
)

result = crew.kickoff(inputs={"question": "What is the reward hacking paper about? Be sure to provide sources."})
```

---

## 4) 지원되는 Knowledge 소스 종류

- **텍스트 계열**: Raw String, `.txt`, PDF
- **구조적 데이터**: CSV, Excel(`.xlsx`), JSON

```python
from crewai.knowledge.source.text_file_knowledge_source import TextFileKnowledgeSource
text_source = TextFileKnowledgeSource(file_paths=["document.txt", "another.txt"])

from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
pdf_source = PDFKnowledgeSource(file_paths=["document.pdf", "another.pdf"])

from crewai.knowledge.source.csv_knowledge_source import CSVKnowledgeSource
csv_source = CSVKnowledgeSource(file_paths=["data.csv"])

from crewai.knowledge.source.excel_knowledge_source import ExcelKnowledgeSource
excel_source = ExcelKnowledgeSource(file_paths=["spreadsheet.xlsx"])

from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource
json_source = JSONKnowledgeSource(file_paths=["data.json"])
```

> **Tip**: 모든 파일은 **`./knowledge`** 폴더에 배치해 중앙관리하세요.

---

## 5) Agent 지식 vs Crew 지식

**레벨 구분**

- **에이전트 레벨**: 특정 에이전트만 사용하는 전용 지식
- **크루 레벨**: 모든 에이전트가 공유하는 공용 지식

**초기화 흐름**

- `crew.kickoff()` 시 각 에이전트가 크루 참조를 받고, 에이전트 지식이 초기화됩니다. (Crew 지식이 없어도 **에이전트 지식 단독**으로 작동 가능)

**스토리지 분리**

- 동일한 ChromaDB 인스턴스 내에서 **컬렉션**으로 분리 저장

  - 예: `crew/`, `Technical Specialist/`, `General Assistant/` 등

**패턴 예시**

- _Agent Only_

  - 특정 전문가형 에이전트에만 전용 지식 부여

- _Agent + Crew_

  - 모든 에이전트가 공통 정책/가이드(crew-level)를 공유 + 전문 에이전트는 전용(agency-level) 지식을 추가로 사용

- _Multi-Agent_

  - 세일즈/기술/지원 등 역할별 상이한 지식을 개별 부여 (임베더도 역할별로 다르게 설정 가능)

---

## 6) Knowledge 설정값 (검색 파라미터)

```python
from crewai.knowledge.knowledge_config import KnowledgeConfig

knowledge_config = KnowledgeConfig(results_limit=10, score_threshold=0.5)

agent = Agent(
    ...,
    knowledge_config=knowledge_config,
)
```

- `results_limit` (기본 3): 검색 시 반환할 문서 개수 상한
- `score_threshold` (기본 0.35): 관련 문서로 인정할 최소 점수

---

## 7) 저장소(ChromaDB) 경로와 관리

**기본 저장 위치(플랫폼별)**

- **macOS**: `~/Library/Application Support/CrewAI/{project_name}/knowledge/`
- **Linux**: `~/.local/share/CrewAI/{project_name}/knowledge/`
- **Windows**: `C:\\Users\\{username}\\AppData\\Local\\CrewAI\\{project_name}\\knowledge\\`

**현재 경로 확인**

```python
from crewai.utilities.paths import db_storage_path
import os

knowledge_path = os.path.join(db_storage_path(), "knowledge")
print("Knowledge storage:", knowledge_path)
```

**커스텀 저장 위치 지정(권장)**

```python
import os
from crewai import Crew

os.environ["CREWAI_STORAGE_DIR"] = "./my_project_storage"  # 루트 상대경로 가능
# 이후 모든 Knowledge는 ./my_project_storage/knowledge/ 아래에 저장
```

**고급: 개별 KnowledgeSource에 커스텀 스토리지 지정**

```python
from crewai.knowledge.storage.knowledge_storage import KnowledgeStorage
from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource

custom_storage = KnowledgeStorage(
    embedder={"provider": "ollama", "config": {"model": "mxbai-embed-large"}},
    collection_name="my_custom_knowledge",
)

source = StringKnowledgeSource(content="Your knowledge content here")
source.storage = custom_storage
```

---

## 8) 임베딩 프로바이더(기본/커스터마이즈)

- **기본값**: Knowledge 저장 시 **OpenAI 임베딩**(`text-embedding-3-small`) 사용
- **LLM과 무관**: LLM이 Claude/Google/Ollama여도 임베딩은 기본 OpenAI를 사용 (원하면 변경 가능)

**Crew 레벨에서 변경**

```python
crew = Crew(
    agents=[...], tasks=[...], knowledge_sources=[...],
    embedder={
        "provider": "voyageai",  # 예: Claude 사용자에게 권장
        "config": {"api_key": "...", "model": "voyage-3"}
    }
)
```

**로컬 임베딩(Ollama) 사용**

```python
embedder={
  "provider": "ollama",
  "config": {"model": "mxbai-embed-large", "url": "http://localhost:11434/api/embeddings"}
}
```

**에이전트 레벨에서 개별 지정**

```python
agent = Agent(
  role="Researcher",
  knowledge_sources=[...],
  embedder={"provider": "google", "config": {"model": "models/text-embedding-004", "api_key": "..."}}
)
```

**Azure OpenAI 사용 시**

```python
agent = Agent(
  role="Researcher",
  knowledge_sources=[...],
  embedder={
    "provider": "azure",
    "config": {
      "api_key": "...",
      "model": "text-embedding-ada-002",  # 배포된 모델명으로 교체
      "api_base": "https://your-azure-endpoint.openai.azure.com/",
      "api_version": "2024-02-01"
    }
  }
)
```

---

## 9) RAG 클라이언트(벡터 스토어) 별도 사용

CrewAI는 **Provider-중립 RAG 클라이언트**를 제공합니다. Knowledge의 내장 스토리지와 **별개**로, 직접 컬렉션 생성/검색이 필요할 때 사용합니다.

```python
from crewai.rag.config.utils import set_rag_config, get_rag_client, clear_rag_config
from crewai.rag.chromadb.config import ChromaDBConfig
from crewai.rag.qdrant.config import QdrantConfig

set_rag_config(ChromaDBConfig())  # 기본 ChromaDB
# set_rag_config(QdrantConfig())   # Qdrant로 전환
client = get_rag_client()

client.create_collection(collection_name="docs")
client.add_documents(collection_name="docs", documents=[{"id": "1", "content": "CrewAI enables collaborative AI agents."}])
results = client.search(collection_name="docs", query="collaborative agents", limit=3)

clear_rag_config()
```

> 사용처: **커스텀 리트리벌 파이프라인**을 만들거나 Knowledge 외부에서 벡터DB를 직접 제어해야 할 때.

---

## 10) 고급 기능

### (1) **Query Rewriting** (자동 질의 최적화)

- 에이전트가 지식을 조회하면, 원본 태스크 프롬프트를 **검색 친화 쿼리**로 자동 변환합니다.
- 불필요한 지시문 제거, 핵심 키워드 중심으로 재작성하여 **정확도 향상**.

### (2) **Knowledge Events** (관측/디버깅)

- `KnowledgeRetrievalStartedEvent`, `KnowledgeRetrievalCompletedEvent`, `KnowledgeQueryStartedEvent`, `KnowledgeQueryCompletedEvent`, `KnowledgeQueryFailedEvent`, `KnowledgeSearchQueryFailedEvent` 등 이벤트로 **검색 과정 모니터링**이 가능합니다.

---

## 11) 디버깅 & 트러블슈팅 체크리스트

1. **초기화 확인**: `crew.kickoff()` 전후 에이전트 Knowledge 상태 확인

```python
print(getattr(agent, 'knowledge', None))  # kickoff 전
crew.kickoff()
print(agent.knowledge)  # kickoff 후
```

2. **스토리지 경로 검증**: `db_storage_path()`로 Knowledge 저장 경로와 컬렉션 구조 확인

3. **임베딩 차원 불일치**: 프로바이더 변경 시 기존 임베딩과 차원이 안 맞아 에러 발생 →

```python
crew.reset_memories(command_type='knowledge')
```

4. **권한 오류(ChromaDB permission denied)**: 저장 경로 권한 수정

```bash
chmod -R 755 ~/.local/share/CrewAI/
```

5. **파일 경로/누락**: 실제 `knowledge/`에 파일이 있는지, CWD가 맞는지 점검

6. **지식 미지속**: 런 간 저장 위치가 달라지지 않았는지 `CREWAI_STORAGE_DIR`/`db_storage_path()`로 확인

**컬렉션 내용 점검(선택)**

```python
import chromadb, os
from crewai.utilities.paths import db_storage_path
client = chromadb.PersistentClient(path=os.path.join(db_storage_path(), "knowledge"))
for c in client.list_collections():
    print(c.name, c.count())
```

**Knowledge 초기화/리셋 명령**

```python
crew.reset_memories(command_type='agent_knowledge')  # 에이전트 지식만
crew.reset_memories(command_type='knowledge')        # 크루+에이전트 지식 모두
# CLI
# crewai reset-memories --agent-knowledge
# crewai reset-memories --knowledge
```

---

## 12) 베스트 프랙티스

- **파일 단위/토픽 단위로 정리**: `knowledge/` 안을 서브폴더로 분류하면 관리가 쉬움
- **메타데이터 포함**: 문서 제목/출처/날짜를 본문에 함께 넣으면 요약·출처표기에 유리
- **임베더 일관성 유지**: 자주 바꾸면 임베딩 재생성 필요 → 비용/시간 증가
- **민감정보 주의**: PII/비밀 데이터는 암호화·접근권한 관리
- **검색 파라미터 튜닝**: `results_limit`, `score_threshold`로 과소/과대 회수 방지

---

## 13) 자주 묻는 질문(FAQ)

**Q1. 크루 지식 없이 에이전트 지식만으로 동작 가능한가요?**
A. 네. 에이전트 레벨 지식은 **독립적으로** 초기화·검색됩니다.

**Q2. LLM과 임베딩 프로바이더는 꼭 같아야 하나요?**
A. 아닙니다. 기본은 OpenAI 임베딩이며, 필요 시 VoyageAI/Google/Ollama/Azure 등으로 교체 가능합니다.

**Q3. 웹 페이지도 Knowledge로 넣을 수 있나요?**
A. 네. `CrewDoclingSource`로 URL을 지정해 로드할 수 있습니다(docling 설치 필요).

**Q4. RAG 클라이언트와 Knowledge의 차이는?**
A. Knowledge는 **CrewAI 내장 스토리지** 기반의 간편한 참조 시스템이고, RAG 클라이언트는 **벡터DB 직접 제어**(컬렉션 생성/검색) 용도입니다.

---

## 14) 체크리스트 (최소 설정)

- [ ] 프로젝트 루트에 `knowledge/` 폴더 생성
- [ ] 파일 배치(예: `knowledge/policies.pdf`, `knowledge/data.csv`)
- [ ] Knowledge Source 생성 시 **상대경로** 사용
- [ ] 필요 시 `CREWAI_STORAGE_DIR`로 저장 위치 고정
- [ ] `KnowledgeConfig(results_limit, score_threshold)`로 검색 품질 튜닝
- [ ] 첫 실행 전후 경로/권한/프로바이더 확인

---

## 15) 예시: 커스텀 KnowledgeSource (API 호출)

```python
from crewai import Agent, Task, Crew, Process, LLM
from crewai.knowledge.source.base_knowledge_source import BaseKnowledgeSource
import requests
from pydantic import Field

class SpaceNewsKnowledgeSource(BaseKnowledgeSource):
    api_endpoint: str = Field(description="API endpoint URL")
    limit: int = Field(default=10, description="Number of articles to fetch")

    def load_content(self):
        resp = requests.get(f"{self.api_endpoint}?limit={self.limit}")
        resp.raise_for_status()
        data = resp.json().get('results', [])
        # 문자열로 포맷팅 후 chunking
        formatted = "Space News Articles:\n\n" + "\n".join([
            f"Title: {a['title']}\nPublished: {a['published_at']}\nSummary: {a['summary']}\nNews Site: {a['news_site']}\nURL: {a['url']}\n---" for a in data
        ])
        return {self.api_endpoint: formatted}

    def add(self) -> None:
        content = self.load_content()
        for _, text in content.items():
            self.chunks.extend(self._chunk_text(text))
        self._save_documents()

# 사용 예시
recent_news = SpaceNewsKnowledgeSource(api_endpoint="https://api.spaceflightnewsapi.net/v4/articles", limit=10)
agent = Agent(role="Space News Analyst", goal="Answer questions about space news", knowledge_sources=[recent_news], llm=LLM(model="gpt-4", temperature=0))
crew = Crew(agents=[agent], tasks=[Task(description="{user_question}", agent=agent)], process=Process.sequential)
# crew.kickoff(inputs={"user_question": "What are the latest developments in space exploration?"})
```

---

### 끝. 이 README만 따라도 `knowledge/` 기반 RAG 설정을 빠르게 적용할 수 있습니다.
