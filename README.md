# 🧠 AI Agent Compilation — 실사용 중심 멀티 에이전트 컬렉션

실제 업무/학습 환경에서 바로 쓸 수 있는 에이전트들을 모았습니다. 목적별로 최적화되어 있으며, 설치와 실행이 간단합니다.

포함된 에이전트: `content-pipline-agent`, `job-hunter-agent`, `news-reader-agent`

---

## 🚀 공통 사양

- 런타임: Python >= 3.13
- 프레임워크: crewai[tools]
- 패키지 관리자: uv 또는 pip
- 환경 변수: `.env`에 다음 값을 설정하세요

(.env):

```bash
OPENAI_API_KEY=sk-...
SERPER_API_KEY=serper_...
FIRECRAWL_API_KEY=fc_...
```

설치/실행 공통 예시:

```bash
# uv (권장)
cd <agent-folder>
uv sync
uv run python main.py  # 또는 main_reference.py

# pip
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
python main.py  # 또는 main_reference.py
```

Playwright 사용 에이전트는 브라우저 바이너리가 필요합니다:

```bash
uv run playwright install  # 또는: python -m playwright install
```

---

## ✍️ 프로젝트 참여자

- 프로젝트 소유/메인터너: 정재현

---

## 📦 content-pipline-agent

- 프로젝트명: "content-pipline-agent"
- 설명: Firecrawl 기반의 신뢰도 높은 웹 검색/스크랩 툴을 갖춘 콘텐츠 리서치 파이프라인. 마크다운을 정제해 요약/분류 등 후속 태스크에 적합한 입력으로 제공합니다.

### 설치 및 실행

```bash
cd content-pipline-agent
uv sync  # 또는 pip install -e .
touch .env  # 환경 변수 작성
uv run python main.py
```

필요 변수: `OPENAI_API_KEY`, `FIRECRAWL_API_KEY`

### 중요한 코드

Firecrawl 검색 결과를 정제하는 도구:

```python
@tool
def web_search_tool(query: str):
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    response = app.search(query=query, limit=5, scrape_options=ScrapeOptions(formats=["markdown"]))
    if not response.success:
        return "Error using tool."

    cleaned_chunks = []
    for result in response.data:
        cleaned = re.sub(r"\\+|\n+", "", result["markdown"]).strip()
        cleaned = re.sub(r"\[[^\]]+\]\([^\)]+\)|https?://[^\s]+", "", cleaned)
        cleaned_chunks.append({
            "title": result["title"],
            "url": result["url"],
            "markdown": cleaned,
        })
    return cleaned_chunks
```

요점

- 검색+스크랩 결과에서 개행/링크/URL을 제거해 모델 친화 텍스트로 정제합니다.
- CrewAI 태스크에서 곧바로 호출 가능한 `@tool` 형태로 제공됩니다.

---

## 💼 job-hunter-agent

- 프로젝트명: "job-hunter-agent"
- 설명: 공고 수집 → 매칭 점수화 → 포지션 선택 → 이력서 리라이트 → 기업 분석 → 면접 준비까지 이어지는 풀 파이프라인 멀티 에이전트. `pydantic` 스키마로 출력 구조를 엄격히 보장합니다.

### 설치 및 실행

```bash
cd job-hunter-agent
uv sync  # 또는 pip install -e .
touch .env  # 환경 변수 작성
uv run python main_reference.py
```

필요 변수: `OPENAI_API_KEY`, `FIRECRAWL_API_KEY`

### 파이프라인 개요

1. job_search_agent: Firecrawl 도구로 공고 수집
2. job_matching_agent: 정합성 점수(1~5)와 사유 부여
3. job_selection_task: 최적 공고 선택
4. resume_optimization_agent: 공고 맞춤 이력서 리라이트
5. company_research_agent: 회사 신호/핵심 주제 분석
6. interview_prep_agent: 질문/어필 포인트 브리핑

### 중요한 코드

강타입 출력 스키마:

```python
class Job(BaseModel):
    job_title: str
    company_name: str
    job_location: str
    job_posting_url: str
    job_summary: str

class JobList(BaseModel):
    jobs: List[Job]

class RankedJob(BaseModel):
    job: Job
    match_score: int
    reason: str

class RankedJobList(BaseModel):
    ranked_jobs: List[RankedJob]

class ChosenJob(BaseModel):
    job: Job
    selected: bool
    reason: str
```

요점

- 각 단계 출력이 스키마로 검증되어 다운스트림 오류를 줄입니다.
- 원본 필드를 보존하고 `match_score`, `reason`만 추가해 투명성을 확보합니다.

---

## 📰 news-reader-agent

- 프로젝트명: "news-reader-agent"
- 설명: 주제 기반 뉴스 수집 → 3단계 요약(Headline/Executive/Comprehensive) → 에디토리얼 큐레이션 자동화. Serper 검색 + Playwright 스크랩으로 폭넓고 신뢰도 높은 수집을 수행합니다.

### 설치 및 실행

```bash
cd news-reader-agent
uv sync  # 또는 pip install -e .
uv run playwright install
touch .env  # 환경 변수 작성
uv run python main.py
```

필요 변수: `OPENAI_API_KEY`, `SERPER_API_KEY`

### 중요한 코드

간결한 스크레이퍼:

```python
search_tool = SerperDevTool(n_results=30)

@tool
def scrape_tool(url: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        time.sleep(5)
        html = page.content()
        browser.close()
        soup = BeautifulSoup(html, 'html.parser')
        for tag in soup.find_all(["header","footer","nav","aside","script","style","noscript","iframe",
                                   "form","button","input","select","textarea","img","svg","canvas","audio",
                                   "video","embed","object"]):
            tag.decompose()
        content = soup.get_text(separator=" ")
        return content or "No content"
```

요점

- 본문 텍스트만 남기도록 불필요한 DOM 요소를 제거합니다.
- 후속 태스크에서 다단계 요약과 최종 리포트 편집을 진행합니다.

---

## 🙌 기여 방법

```bash
git checkout -b feat/<feature-name>
git commit -m "feat: <설명>"
git push origin feat/<feature-name>
```

이슈/PR 환영합니다!
