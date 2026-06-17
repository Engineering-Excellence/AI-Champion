# 나라장터 입찰공고 MCP 서버 (mcp-narajangter)

조달청 "나라장터 입찰공고정보서비스" REST API를 Claude Desktop / Claude Code에서 사용할 수 있게 해주는
MCP(Model Context Protocol) 서버입니다. IT 소기업이 관심 있는 입찰공고를 자연어로 검색·조회할 수 있습니다.

## 사전 조건

- Node.js 18 이상
- 공공데이터포털(data.go.kr) 회원가입 및 "조달청_나라장터 입찰공고정보서비스" 인증키

## 인증키 발급 방법

1. [data.go.kr](https://www.data.go.kr) 에 로그인합니다.
2. 데이터셋 "조달청_나라장터 입찰공고정보서비스" (데이터셋 ID: 15129394)를 검색합니다.
3. "활용신청"을 눌러 API 사용 신청을 합니다. (보통 즉시 또는 1일 이내 승인)
4. 마이페이지 → "오픈API" → "활용신청 현황"에서 발급된 인증키를 확인합니다.
   - 인증키는 "Encoding"과 "Decoding" 두 종류로 제공됩니다. 이 서버는 둘 중 어떤 키를 넣어도
     자동으로 인코딩 여부를 판단해 처리하므로 아무 키나 사용해도 됩니다.

## 설치 방법

```bash
git clone <이 저장소 경로>
cd mcp-narajangter
npm install
cp .env.example .env
```

`.env` 파일을 열어 발급받은 인증키를 입력합니다.

```
NARA_SERVICE_KEY=발급받은_인증키
```

빌드:

```bash
npm run build
```

성공하면 `dist/index.js`가 생성됩니다.

> `@modelcontextprotocol/sdk`는 `1.28.0`으로 버전을 고정해 사용합니다. `1.29.0`은 패키지 내부
> self-import 경로에 `dist/esm`/`dist/cjs`가 중복으로 들어가는 배포 버그가 있어 서버가 기동되지
> 않습니다. `npm install` 시 이 버전이 자동으로 올라가지 않도록 `package.json`에 정확히
> `"1.28.0"`으로 명시되어 있습니다.

## 테스트 실행 방법

`.env`에 인증키를 설정한 뒤 아래 명령으로 서버가 정상적으로 기동되는지 확인합니다.

```bash
npm start
```

MCP 서버는 stdio로 통신하므로 터미널에서 바로 실행하면 응답 없이 대기 상태로 보이는 것이 정상입니다.
(JSON-RPC 요청을 받을 준비가 된 상태) `Ctrl+C`로 종료할 수 있습니다.

실제 동작 확인은 Claude Desktop이나 [MCP Inspector](https://github.com/modelcontextprotocol/inspector)를
연동해서 도구를 호출해보는 것을 권장합니다.

```bash
npx @modelcontextprotocol/inspector node dist/index.js
```

## Claude Desktop 연동 설정

`claude_desktop_config.json` (Windows: `%APPDATA%\Claude\claude_desktop_config.json`)에 아래 내용을 추가합니다.

```json
{
  "mcpServers": {
    "narajangter": {
      "command": "node",
      "args": ["/절대경로/mcp-narajangter/dist/index.js"],
      "env": {
        "NARA_SERVICE_KEY": "여기에_인증키_직접_입력_가능"
      }
    }
  }
}
```

인증키는 `.env` 파일 또는 위 `env` 블록 중 하나로 설정하면 됩니다. 둘 다 설정된 경우
**`env` 블록의 값이 우선**합니다 (Claude Desktop이 설정한 `env`가 `.env` 파일보다 먼저
`process.env`에 들어가고, `dotenv`는 기존 환경변수를 덮어쓰지 않기 때문입니다).

## 제공 도구 (Tools)

| 도구 | 설명 |
|---|---|
| `search_it_bids` | 키워드로 IT·소프트웨어 관련 용역 입찰공고 검색 |
| `get_bid_detail` | 입찰공고번호로 상세 정보 조회 |
| `get_recent_it_bids` | 최근 N일 이내 신규 용역 입찰공고 조회 |
| `search_bids_by_org` | 특정 발주기관의 입찰공고 검색 |
| `list_closing_soon_bids` | 마감이 N일 이내로 임박한 입찰공고 조회 |

## 사용 예시

Claude에게 다음과 같이 말하면 도구가 자동으로 호출됩니다.

- "최근 1주일간 올라온 IT 관련 입찰공고 알려줘"
- "소프트웨어 개발 관련 입찰공고 중 마감 3일 이내인 것 찾아줘"
- "행정안전부에서 발주한 정보화 사업 입찰공고 목록 보여줘"
- "공고번호 20240001234-00 상세 내용 알려줘"
- "이번 달 클라우드 관련 입찰공고 검색해줘"

## 주의사항

- 이 API는 공공데이터포털 문서에 응답 필드(item) 전체 목록이 공개되어 있지 않아, 일반적으로
  통용되는 필드명(`bidNtceNm`, `presmptPrce`, `bidClseDt` 등)을 기준으로 구현했습니다. 실제
  인증키로 5개 도구를 모두 호출해 본 결과 이 필드명들이 정상적으로 매칭됨을 확인했습니다.
  그래도 일부 필드가 "정보없음"으로 표시된다면, `src/index.ts`의 `pick(...)` 호출에 사용된
  후보 필드명 목록이나 `FIELD_LABELS` 테이블을 실제 응답 기준으로 보완하면 됩니다.
- `get_bid_detail`은 별도의 상세조회 오퍼레이션이 존재하지 않아, 목록 조회 오퍼레이션
  (`getBidPblancListInfoServc` 등)에 `inqryDiv=2`와 `bidNtceNo`/`bidNtceOrd`를 넘겨 단건
  조회하는 방식으로 구현했습니다. 응답에 포함된 모든 필드를 그대로 나열하므로, 도구 표에
  없는 필드라도 원본 필드명으로는 항상 표시됩니다.
- 목록 조회 오퍼레이션은 공고일시 조회 기간(`inqryBgnDt`~`inqryEndDt`)이 최대 31일로
  제한되어 있어, 이를 초과하면 `입력범위값 초과 에러`가 발생합니다. `search_bids_by_org`는
  최근 30일, `list_closing_soon_bids`는 `(31 - withinDays)`일 전부터 `withinDays`일 후까지로
  조회 범위를 맞춰 이 제한을 넘지 않도록 했습니다 (`withinDays`는 최대 30으로 제한).
- `list_closing_soon_bids`는 마감일시 전용 조회 파라미터가 공식적으로 확인되지 않아, 위
  범위로 공고된 건을 가져온 뒤 마감일시가 조건에 맞는 건만 클라이언트에서 걸러내는 방식으로
  구현했습니다.
- API 기본 URL은 `https://apis.data.go.kr/1230000/ad/BidPublicInfoService` 입니다
  (`BidPublicInfoService04`처럼 끝에 버전 숫자가 붙은 경로는 존재하지 않으며 404가 납니다).
