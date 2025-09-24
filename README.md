```
# 🧠 AI Agent Compilation — 실사용 중심 멀티 에이전트 컬렉션

이 저장소는 실제 업무/학습 시나리오에 바로 투입 가능한 에이전트들을 모아둔 컬렉션입니다.
각 에이전트는 목적에 맞게 설계되어 있으며, 설치부터 실행까지 즉시 따라 할 수 있도록 정리했습니다.

> 포함된 에이전트: `content-pipline-agent`, `job-hunter-agent`, `news-reader-agent`

---

## 🚀 공통 사양
- **런타임**: Python `>= 3.13`
- **핵심 프레임워크**: `crewai[tools]`
- **권장 패키지 관리자**: `uv` 또는 `pip`
- **환경변수**: 필요 시 `.env` 파일에 키를 설정합니다 (키 값은 보안상 공개하지 않습니다).
  - `OPENAI_API_KEY`, `SERPER_API_KEY`, `FIRECRAWL_API_KEY` 등

설치/실행 기본 예시:

```

```bash
# uv 사용 시 (권장)
cd <agent-folder>
uv sync
uv run python main.py  # 또는 main_reference.py

# pip 사용 시
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
python main.py  # 또는 main_reference.py
```

```

Playwright를 사용하는 에이전트의 경우 브라우저 바이너리 설치가 추가로 필요합니다:

```

```bash
uv run playwright install  # 또는: python -m playwright install
```

```

---

## ✍️ 프로젝트 참여자
- 프로젝트 소유/메인터너: 정재현

---

## 📦 content-pipline-agent
- **프로젝트명**: "content-pipline-agent"
- **설명**: Firecrawl 기반의 고신뢰 웹 검색/스크래핑 툴을 탑재한 콘텐츠 리서치 파이프라인의 토대입니다. 수집된 마크다운을 정규식으로 정제해 다운스트림 태스크(요약/분류/집계)에 적합한 입력을 제공합니다.

### 설치 및 실행
```

```bash
cd content-pipline-agent
uv sync  # 또는 pip install -e .
cp .env.example .env  # 없다면 .env를 생성하고 필요한 키를 설정하세요
uv run python main.py
```

```

필요한 환경변수: `OPENAI_API_KEY`, `FIRECRAWL_API_KEY`

### 중요한 코드
Firecrawl 검색 결과를 안전하게 정제해 반환하는 툴:

```

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

```

설명:
```

```text
- Firecrawl의 검색+스크랩 결과를 받아 불필요한 개행/링크/URL을 제거해 모델 친화적인 텍스트로 정제합니다.
- 도구(@tool)는 CrewAI 태스크에서 즉시 호출 가능하도록 래핑되어 있습니다.
```

```

---

## 💼 job-hunter-agent
- **프로젝트명**: "job-hunter-agent"
- **설명**: 구인 공고 수집 → 매칭 점수화 → 포지션 선택 → 이력서 리라이트 → 기업 분석 → 면접 준비까지 한 번에 처리하는 풀 파이프라인형 멀티 에이전트. `pydantic` 스키마를 통해 출력 구조를 엄격히 보장합니다.

### 설치 및 실행
```

```bash
cd job-hunter-agent
uv sync  # 또는 pip install -e .
cp .env.example .env  # 없다면 .env 생성 후 키 설정
uv run python main_reference.py  # 데모 파이프라인 진입점
```

```

필요한 환경변수(예): `OPENAI_API_KEY`, `FIRECRAWL_API_KEY`

### 파이프라인 개요
```

```text
1) job_search_agent: Firecrawl 기반 웹 검색 도구로 공고 수집
2) job_matching_agent: 후보자 프로필과 공고의 정합성을 점수화(1~5) 및 사유 기록
3) job_selection_task: 최적 공고 1건 선택
4) resume_optimization_agent: 공고 정합형 이력서 리라이트
5) company_research_agent: 회사 신호/핵심 주제 분석
6) interview_prep_agent: 면접 질문, 어필 포인트 브리핑 구성
```

```

### 중요한 코드
강타입 출력으로 안정성을 확보하는 모델 정의:

```

```python
class Job(BaseModel):
    job_title: str
    company_name: str
    job_location: str
    job_posting_url: str
    job_summary: str
    # ...선택 필드들(benefits, skills 등)

class JobList(BaseModel):
    jobs: List[Job]

class RankedJob(BaseModel):
    job: Job
    match_score: int  # 1~5
    reason: str

class RankedJobList(BaseModel):
    ranked_jobs: List[RankedJob]

class ChosenJob(BaseModel):
    job: Job
    selected: bool
    reason: str
```

```

설명:
```

```text
- 각 태스크의 출력은 상호 합의된 pydantic 스키마로 엄격히 검증되어, 다운스트림 단계에서 파싱/검증 오류를 최소화합니다.
- 매칭 단계에서 원본 필드를 보존하고 `match_score`, `reason`만 추가하여 투명성을 유지합니다.
```

```

---

## 📰 news-reader-agent
- **프로젝트명**: "news-reader-agent"
- **설명**: 트렌딩/주제 기반 뉴스 수집 → 다단계 요약(Headline/Executive/Comprehensive) → 에디토리얼 큐레이션까지 자동화. 검색엔진(Serper) + Playwright 스크레이퍼로 신뢰도와 커버리지를 동시에 확보합니다.

### 설치 및 실행
```

```bash
cd news-reader-agent
uv sync  # 또는 pip install -e .
uv run playwright install  # 스크랩용 브라우저 설치
cp .env.example .env  # 없다면 .env 생성 후 키 설정
uv run python main.py  # topic 파라미터는 main.py에서 설정 가능
```

```

필요한 환경변수(예): `OPENAI_API_KEY`, `SERPER_API_KEY`

### 중요한 코드
Serper 검색 + Playwright 스크레이퍼 조합:

```

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
        return content if content else "No content"
```

```

설명:
```

```text
- 검색 결과에서 실제 본문이 있는 아티클 페이지만 선별하고, 불필요한 DOM 요소를 제거하여 순수 텍스트를 추출합니다.
- 이후 태스크에서 Headline/Executive/Comprehensive 3단계 요약과 최종 리포트 편집을 수행합니다.
```

```

---

## 🙌 기여 방법
```

```bash
# 이 저장소를 포크/클론 후 브랜치에서 작업해주세요
git checkout -b feat/<feature-name>
git commit -m "feat: <설명>"
git push origin feat/<feature-name>
```

```

이슈/PR 환영합니다.
```
