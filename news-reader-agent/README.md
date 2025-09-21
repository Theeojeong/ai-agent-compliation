**프로젝트 개요**
- **이름:** `news-reader-agent`
- **목표:** 특정 토픽에 대해 신뢰할 수 있는 최신 뉴스를 수집하고, 요약·편집해 읽기 좋은 리포트를 자동 생성.
- **구성:** 3개 에이전트(수집 → 요약 → 큐레이션)와 3개 태스크로 구성된 CrewAI 파이프라인.

**기술 스택**
- **CrewAI:** 다중 에이전트 오케스트레이션 프레임워크. 에이전트/태스크 구성과 도구 연결을 담당.
- `crewai_tools.SerperDevTool`: 검색 API 연동 도구. 뉴스/웹 검색 결과를 확보.
- **Playwright:** 동적 웹 페이지 렌더링과 HTML 수집. 크롬 기반 헤드리스 브라우징.
- **BeautifulSoup (bs4):** HTML 파싱과 불필요한 요소 제거 후 본문 텍스트 정제.
- **python-dotenv:** `.env` 로컬 환경변수 로딩.

**설치 및 실행**
- **필수:** Python `>=3.13`
- **설치 (uv 사용):**
  - `uv sync`
  - Playwright 브라우저 설치: `uv run playwright install chromium`
- **설치 (pip 사용):**
  - `pip install -e .` 또는 `pip install crewai[tools] python-dotenv`
  - Playwright 브라우저 설치: `playwright install chromium`
- **실행:** `python main.py`
  - 현재 `main.py` 하단에서 `kickoff({"topic": "..."})`로 토픽을 전달해 파이프라인을 시작함.

**환경 변수 (.env)**
- `OPENAI_API_KEY`: CrewAI의 LLM 호출에 사용.
- `SERPER_API_KEY`: `SerperDevTool` 검색 호출에 사용.
- 필요 시 Playwright 관련 설정(예: 프록시)이 있다면 추가 가능.

**검색: SerperDevTool을 왜/어떻게 썼는가**
- **왜:** 뉴스·웹 검색의 정확도와 최신성, 그리고 간편한 API 사용성을 고려해 Serper를 선택.
- **어떻게:** `tools.py`에서 `SerperDevTool(n_results=30)`로 초기화 후, 에이전트의 `tools` 리스트에 연결.
- **사용법 요약:**
  - 환경변수 `SERPER_API_KEY` 설정 → `SerperDevTool` 인스턴스 생성 → CrewAI 에이전트에 도구로 전달.
  - 에이전트는 태스크 수행 중 검색 질의(토픽·키워드)를 이 도구로 실행하여 관련 기사 링크를 확보.

**수집: Playwright를 왜/어떻게 썼는가**
- **왜:** 단순 `requests`로는 렌더링 전 DOM을 받는 경우가 많음. 동적 렌더링 페이지에서도 안정적으로 본문을 수집하려면 브라우저 자동화가 필요.
- **어떻게:**
  - `playwright.sync_api`의 Chromium을 헤드리스로 실행 → `page.goto(url)` → 잠시 대기 후 `page.content()`로 렌더링 완료 HTML 확보.
  - 동작상 핵심 단계: 브라우저 시작 → 새 페이지 → URL 방문 → 대기 → HTML 추출 → 브라우저 종료.
- **사용법 요약:**
  - 설치 후 최초 1회 `playwright install chromium` 필요.
  - 코드 상에서는 페이지 로드 안정성을 위해 짧은 대기(`time.sleep(5)`)를 사용해 렌더링을 보장.

**파싱: BeautifulSoup을 왜/어떻게 썼는가**
- **왜:** 수집한 HTML에서 광고/네비게이션/폼 등 비본문 요소를 제거하고 순수 텍스트만 추출해 요약 품질을 높이기 위함.
- **어떻게:**
  - `BeautifulSoup(html, 'html.parser')`로 파싱 후, `header`, `footer`, `nav`, `aside`, `script`, `style`, `noscript`, `iframe`, `form`, `button`, `input`, `select`, `textarea`, `img`, `svg`, `canvas`, `audio`, `video`, `embed`, `object` 등 불필요 태그를 일괄 제거.
  - 최종적으로 `soup.get_text(separator=" ")`로 본문 텍스트를 추출. 비어 있으면 `"No content"` 반환.
- **효과:** 요약 대상 텍스트가 잡음 없이 정리되어 LLM 요약 품질과 안정성이 향상.

**에이전트/프롬프트 설계 의도 (config/agents.yaml)**
- `news_hunter_agent` (Senior News Intelligence Specialist)
  - **의도:** 광범위한 출처에서 신뢰 가능한 기사를 빠르게 선별·수집.
  - **프롬프트 방향:** 신뢰성, 소스 다변화, 교차 검증, 최신성 강조. `inject_date: true`로 시점 민감도를 확보.
  - **도구:** `search_tool`(Serper) + `scrape_tool`(Playwright+BS4)로 “링크 찾기 → 본문 수집”을 원스톱 수행.
- `summarizer_agent` (Expert News Analyst and Content Synthesizer)
  - **의도:** 핵심 맥락과 함의를 보존한 압축 요약. 과도한 단순화 방지.
  - **프롬프트 방향:** 객관성·정확성·맥락화 강조. 다양한 주제(정치/기술/경제/국제) 대응을 명시하여 일반화된 요약 성능 개선.
  - **도구:** 본문 추가 파싱이 필요할 경우를 대비해 `scrape_tool`을 유지.
- `curator_agent` (Senior News Editor and Editorial Curator)
  - **의도:** 요약 결과를 독자가 읽기 좋은 큐레이션 형태로 재구성(우선순위, 섹션 구분, 헤드라인화).
  - **프롬프트 방향:** 편집적 판단(무엇이 중요한가, 어떻게 묶을 것인가)을 전면에. 리듬감 있는 읽기 흐름과 맥락 제공을 강조.
- 공통
  - `verbose: true`: 내부 추론과 진행 로그를 풍부하게 하여 디버깅/재현성 확보.
  - `llm: openai/o4-mini-2025-04-16`: 적절한 비용·성능 균형 모델을 선택(요약·편집 중심 작업에 충분).

**동작 흐름**
- 입력 토픽 설정 → `news_hunter_agent`가 검색·수집 → `summarizer_agent`가 핵심 요약 → `curator_agent`가 읽기 좋은 형태로 편집 → 최종 리포트 출력.

**내가 남기는 회고 포인트**
- 검색 품질은 `SerperDevTool` 파라미터(`n_results`)와 프롬프트에서의 키워드 지시(예: 소스 다양성, 최신성)에 큰 영향을 받음.
- 수집 안정성은 Playwright 대기 시간/네트워크 상태에 민감. 필요 시 명시적 `wait_for_selector` 같은 조건 대기를 고려.
- 파싱 품질은 제거 태그 목록에 좌우. 매체별 불필요 블록(예: 추천/코멘트)을 추가 식별해 더 깔끔한 본문을 얻을 수 있음.
- 프롬프트는 역할·목표·톤을 명료히 분리할수록 에이전트 간 간섭이 줄고 결과 일관성이 좋아짐.

**자주 쓰는 명령**
- 의존성 설치(uv): `uv sync`
- 브라우저 설치: `uv run playwright install chromium` 또는 `playwright install chromium`
- 실행: `python main.py`

이 문서는 내가 CrewAI로 첫 에이전트를 직접 설계·구현하며 배운 선택과 의도를 빠르게 회상하기 위한 기록이다. 검색(Serper) → 수집(Playwright) → 정제(BeautifulSoup) → 요약/큐레이션(CrewAI) 흐름을 유지하면 재사용과 확장이 수월하다.
