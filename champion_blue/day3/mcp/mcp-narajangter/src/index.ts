import "dotenv/config";
import axios from "axios";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const SERVICE_KEY = process.env.NARA_SERVICE_KEY;
if (!SERVICE_KEY) {
  console.error(
    "오류: NARA_SERVICE_KEY 환경변수가 설정되지 않았습니다. .env 파일에 인증키를 등록하세요."
  );
  process.exit(1);
}

const BASE_URL = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService";

const LIST_PATHS = {
  servc: "/getBidPblancListInfoServc",
  thng: "/getBidPblancListInfoThng",
  cnstwk: "/getBidPblancListInfoCnstwk",
  frgcpt: "/getBidPblancListInfoFrgcpt",
} as const;

const BID_CLSFC_TO_LIST_KEY: Record<string, keyof typeof LIST_PATHS> = {
  "01": "thng",
  "02": "cnstwk",
  "03": "servc",
};

const NO_RESULT_MESSAGE = "조건에 맞는 입찰공고가 없습니다.";

// 공공데이터포털 인증키는 "인코딩" 키와 "디코딩" 키 두 종류로 발급되는데,
// axios params에 그대로 넘기면 이미 인코딩된 키가 다시 인코딩되어(이중 인코딩) 인증 오류가 난다.
// 키에 %XX 패턴이 있으면 인코딩된 키로 보고 그대로 사용하고, 없으면 직접 인코딩한다.
function encodeServiceKey(key: string): string {
  return /%[0-9A-Fa-f]{2}/.test(key) ? key : encodeURIComponent(key);
}

function extractXmlErrorMessage(xml: string): string {
  const match =
    xml.match(/<returnAuthMsg>(.*?)<\/returnAuthMsg>/) ||
    xml.match(/<errMsg>(.*?)<\/errMsg>/) ||
    xml.match(/<msg>(.*?)<\/msg>/);
  return match ? match[1] : "알 수 없는 오류가 발생했습니다.";
}

function normalizeItems(items: unknown): Record<string, any>[] {
  if (!items) return [];
  if (Array.isArray(items)) return items;
  if (typeof items === "object") return [items as Record<string, any>];
  return [];
}

async function callBidApi(
  path: string,
  params: Record<string, string | number | undefined>
): Promise<{ items: Record<string, any>[]; totalCount: number }> {
  const qs = new URLSearchParams();
  qs.set("type", "json");
  for (const [key, value] of Object.entries(params)) {
    if (value !== undefined && value !== "") qs.set(key, String(value));
  }

  const url = `${BASE_URL}${path}?serviceKey=${encodeServiceKey(SERVICE_KEY as string)}&${qs.toString()}`;

  let res;
  try {
    res = await axios.get(url, { timeout: 15000, validateStatus: () => true });
  } catch (err) {
    throw new Error(`나라장터 API 호출 중 오류가 발생했습니다: ${(err as Error).message}`);
  }

  if (res.status !== 200) {
    throw new Error(`나라장터 API 호출 실패 (HTTP ${res.status})`);
  }

  if (typeof res.data === "string" && res.data.trim().startsWith("<")) {
    throw new Error(`나라장터 API 오류: ${extractXmlErrorMessage(res.data)}`);
  }

  const response = (res.data as any)?.response;
  if (!response?.header) {
    throw new Error("나라장터 API 응답 형식이 올바르지 않습니다.");
  }

  const resultCode = response.header.resultCode;
  if (resultCode !== "00") {
    throw new Error(`나라장터 API 오류 (코드 ${resultCode}): ${response.header.resultMsg ?? "알 수 없는 오류"}`);
  }

  return {
    items: normalizeItems(response.body?.items),
    totalCount: Number(response.body?.totalCount ?? 0),
  };
}

function pick(item: Record<string, any>, keys: string[]): string | undefined {
  for (const key of keys) {
    const value = item[key];
    if (value !== undefined && value !== null && String(value).trim() !== "") {
      return String(value);
    }
  }
  return undefined;
}

function formatAmount(value: string | undefined): string {
  if (!value) return "정보없음";
  const n = Number(value);
  if (Number.isNaN(n) || n <= 0) return "정보없음";
  return `${n.toLocaleString("ko-KR")}원`;
}

function formatDateTimeValue(value: string | undefined): string {
  if (!value) return "정보없음";
  const s = value.trim();

  let m = s.match(/^(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})$/);
  if (m) return `${m[1]}년 ${m[2]}월 ${m[3]}일 ${m[4]}:${m[5]}`;

  m = s.match(/^(\d{4})(\d{2})(\d{2})$/);
  if (m) return `${m[1]}년 ${m[2]}월 ${m[3]}일`;

  m = s.match(/^(\d{4})-(\d{2})-(\d{2})[ T](\d{2}):(\d{2})/);
  if (m) return `${m[1]}년 ${m[2]}월 ${m[3]}일 ${m[4]}:${m[5]}`;

  m = s.match(/^(\d{4})-(\d{2})-(\d{2})$/);
  if (m) return `${m[1]}년 ${m[2]}월 ${m[3]}일`;

  return s;
}

function parseDateTimeValue(value: string | undefined): Date | undefined {
  if (!value) return undefined;
  const s = value.trim();

  let m = s.match(/^(\d{4})-(\d{2})-(\d{2})[ T]?(\d{2})?:?(\d{2})?/);
  if (m) {
    const [, y, mo, d, hh = "00", mi = "00"] = m;
    return new Date(Number(y), Number(mo) - 1, Number(d), Number(hh), Number(mi));
  }

  m = s.match(/^(\d{4})(\d{2})(\d{2})(\d{2})?(\d{2})?$/);
  if (m) {
    const [, y, mo, d, hh = "00", mi = "00"] = m;
    return new Date(Number(y), Number(mo) - 1, Number(d), Number(hh), Number(mi));
  }

  return undefined;
}

function formatRemaining(closeDt: Date, now: Date): string {
  const diffMs = closeDt.getTime() - now.getTime();
  if (diffMs <= 0) return "마감됨";
  const diffMin = Math.floor(diffMs / 60000);
  const days = Math.floor(diffMin / 1440);
  const hours = Math.floor((diffMin % 1440) / 60);
  const mins = diffMin % 60;
  const parts: string[] = [];
  if (days > 0) parts.push(`${days}일`);
  if (hours > 0) parts.push(`${hours}시간`);
  if (days === 0 && mins > 0) parts.push(`${mins}분`);
  return parts.length ? `${parts.join(" ")} 남음` : "곧 마감";
}

function todayYYYYMMDD(offsetDays = 0): string {
  const d = new Date();
  d.setDate(d.getDate() + offsetDays);
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${y}${m}${day}`;
}

function clampNumOfRows(n: number): number {
  return Math.min(100, Math.max(1, Math.floor(n)));
}

function formatBidListItem(item: Record<string, any>): string {
  const no = pick(item, ["bidNtceNo"]) ?? "정보없음";
  const ord = pick(item, ["bidNtceOrd"]) ?? "00";
  const name = pick(item, ["bidNtceNm"]) ?? "정보없음";
  const org = pick(item, ["ntceInsttNm"]) ?? "정보없음";
  const dminstt = pick(item, ["dminsttNm"]) ?? "정보없음";
  const amount = formatAmount(pick(item, ["presmptPrce", "asignBdgtAmt", "bssamt"]));
  const ntceDt = formatDateTimeValue(pick(item, ["bidNtceDate", "bidNtceDt", "rgstDt"]));
  const clseDt = formatDateTimeValue(pick(item, ["bidClseDt", "bidClseDate"]));
  const div = pick(item, ["ntceKindNm", "srvceDivNm", "prdctClsfcNoNm"]) ?? "-";
  const detailUrl = pick(item, ["bidNtceDtlUrl", "bidNtceUrl"]);

  const lines = [
    `### ${name}`,
    `- 입찰공고번호: ${no}-${ord}`,
    `- 발주기관: ${org}`,
    `- 수요기관: ${dminstt}`,
    `- 기초금액(추정가격): ${amount}`,
    `- 공고일: ${ntceDt}`,
    `- 입찰마감일시: ${clseDt}`,
    `- 업무구분: ${div}`,
  ];
  if (detailUrl) lines.push(`- 상세조회 링크: ${detailUrl}`);
  return lines.join("\n");
}

const FIELD_LABELS: Record<string, string> = {
  bidNtceNo: "입찰공고번호",
  bidNtceOrd: "공고차수",
  bidNtceNm: "입찰공고명",
  ntceInsttNm: "공고기관",
  dminsttNm: "수요기관",
  bidMethdNm: "입찰방식",
  cntrctCnclsMthdNm: "계약방법",
  ntceKindNm: "공고종류",
  presmptPrce: "추정가격",
  asignBdgtAmt: "배정예산금액",
  bidNtceDate: "공고일자",
  bidNtceDt: "공고일자",
  bidClseDt: "입찰마감일시",
  bidClseDate: "입찰마감일시",
  opengDt: "개찰일시",
  opengPlce: "개찰장소",
  ntceInsttOfclNm: "담당자명",
  ntceInsttOfclTelNo: "담당자 연락처",
  ntceInsttOfclEmailAdrs: "담당자 이메일",
  indstrytyLmtNm: "업종제한",
  indstrytyLmtYn: "업종제한 여부",
  regnLmtYn: "지역제한 여부",
  prtcptPsblRgnNm: "참가가능지역",
  bidPrtcptLmtYn: "참가자격 제한 여부",
  bidNtceDtlUrl: "상세페이지 URL",
  dlvryPlce: "납품장소",
  rgstDt: "등록일시",
};

function formatBidDetail(item: Record<string, any>): string {
  const title = pick(item, ["bidNtceNm"]) ?? "입찰공고";
  const lines = [`## ${title} 상세정보`];
  for (const [key, value] of Object.entries(item)) {
    if (value === undefined || value === null || String(value).trim() === "") continue;
    const label = FIELD_LABELS[key] ?? key;
    lines.push(`- ${label}: ${value}`);
  }
  return lines.join("\n");
}

const server = new McpServer({
  name: "narajangter-bid-mcp",
  version: "1.0.0",
});

function toResult(text: string) {
  return { content: [{ type: "text" as const, text }] };
}

function toErrorResult(err: unknown) {
  const message = err instanceof Error ? err.message : String(err);
  return { content: [{ type: "text" as const, text: `오류: ${message}` }], isError: true };
}

server.registerTool(
  "search_it_bids",
  {
    title: "IT 입찰공고 검색",
    description: "IT·소프트웨어·정보화 관련 용역 입찰공고를 키워드로 검색합니다.",
    inputSchema: {
      keyword: z.string().describe("검색 키워드 (예: 소프트웨어, SI, 정보화, 시스템 구축)"),
      pageNo: z.number().int().min(1).default(1).describe("페이지 번호"),
      numOfRows: z.number().int().min(1).max(100).default(10).describe("한 페이지 결과 수"),
      startDate: z.string().regex(/^\d{8}$/).optional().describe("입찰공고일 시작 (YYYYMMDD)"),
      endDate: z.string().regex(/^\d{8}$/).optional().describe("입찰공고일 종료 (YYYYMMDD)"),
    },
  },
  async ({ keyword, pageNo, numOfRows, startDate, endDate }) => {
    try {
      const bgn = startDate ?? todayYYYYMMDD(-30);
      const end = endDate ?? todayYYYYMMDD(0);
      const { items, totalCount } = await callBidApi(LIST_PATHS.servc, {
        inqryDiv: 1,
        inqryBgnDt: `${bgn}0000`,
        inqryEndDt: `${end}2359`,
        bidNtceNm: keyword,
        pageNo,
        numOfRows: clampNumOfRows(numOfRows),
      });

      if (items.length === 0) return toResult(NO_RESULT_MESSAGE);

      const header = `## "${keyword}" 검색 결과 (전체 ${totalCount}건)`;
      const body = items.map(formatBidListItem).join("\n\n");
      return toResult(`${header}\n\n${body}`);
    } catch (err) {
      return toErrorResult(err);
    }
  }
);

server.registerTool(
  "get_bid_detail",
  {
    title: "입찰공고 상세 조회",
    description: "입찰공고번호로 상세 정보를 조회합니다.",
    inputSchema: {
      bidNtceNo: z.string().describe("입찰공고번호"),
      bidNtceOrd: z.string().default("00").describe("공고차수"),
      bidClsfcNo: z
        .enum(["01", "02", "03", "04"])
        .describe("업무구분번호: 01=물품, 02=공사, 03=용역, 04=외자"),
    },
  },
  async ({ bidNtceNo, bidNtceOrd, bidClsfcNo }) => {
    try {
      if (bidClsfcNo === "04") {
        return toResult("오류: 외자 입찰공고 상세 조회는 현재 지원되지 않습니다.");
      }
      const path = LIST_PATHS[BID_CLSFC_TO_LIST_KEY[bidClsfcNo]];
      const { items } = await callBidApi(path, {
        inqryDiv: 2,
        bidNtceNo,
        bidNtceOrd,
        pageNo: 1,
        numOfRows: 1,
      });

      if (items.length === 0) return toResult(NO_RESULT_MESSAGE);
      return toResult(formatBidDetail(items[0]));
    } catch (err) {
      return toErrorResult(err);
    }
  }
);

server.registerTool(
  "get_recent_it_bids",
  {
    title: "최신 IT 입찰공고 조회",
    description: "오늘 기준 최근 N일 이내 IT 관련(용역) 신규 입찰공고 목록을 가져옵니다.",
    inputSchema: {
      days: z.number().int().min(1).default(7).describe("최근 며칠"),
      numOfRows: z.number().int().min(1).max(100).default(20).describe("결과 수"),
    },
  },
  async ({ days, numOfRows }) => {
    try {
      const bgn = todayYYYYMMDD(-days);
      const end = todayYYYYMMDD(0);
      const { items, totalCount } = await callBidApi(LIST_PATHS.servc, {
        inqryDiv: 1,
        inqryBgnDt: `${bgn}0000`,
        inqryEndDt: `${end}2359`,
        pageNo: 1,
        numOfRows: clampNumOfRows(numOfRows),
      });

      if (items.length === 0) return toResult(NO_RESULT_MESSAGE);

      const header = `## 최근 ${days}일 IT 관련 입찰공고 (전체 ${totalCount}건)`;
      const body = items.map(formatBidListItem).join("\n\n");
      return toResult(`${header}\n\n${body}`);
    } catch (err) {
      return toErrorResult(err);
    }
  }
);

server.registerTool(
  "search_bids_by_org",
  {
    title: "발주기관별 입찰공고 검색",
    description: "특정 발주기관의 입찰공고를 조회합니다.",
    inputSchema: {
      orgName: z.string().describe("발주기관명 (예: 행정안전부, 교육부)"),
      bidType: z
        .enum(["servc", "thng", "cnstwk"])
        .default("servc")
        .describe("업무구분: servc=용역, thng=물품, cnstwk=공사"),
      pageNo: z.number().int().min(1).default(1).describe("페이지 번호"),
      numOfRows: z.number().int().min(1).max(100).default(10).describe("결과 수"),
    },
  },
  async ({ orgName, bidType, pageNo, numOfRows }) => {
    try {
      const bgn = todayYYYYMMDD(-30);
      const end = todayYYYYMMDD(0);
      const path = LIST_PATHS[bidType];

      let result = await callBidApi(path, {
        inqryDiv: 1,
        inqryBgnDt: `${bgn}0000`,
        inqryEndDt: `${end}2359`,
        dminsttNm: orgName,
        pageNo,
        numOfRows: clampNumOfRows(numOfRows),
      });

      if (result.items.length === 0) {
        result = await callBidApi(path, {
          inqryDiv: 1,
          inqryBgnDt: `${bgn}0000`,
          inqryEndDt: `${end}2359`,
          ntceInsttNm: orgName,
          pageNo,
          numOfRows: clampNumOfRows(numOfRows),
        });
      }

      if (result.items.length === 0) return toResult(NO_RESULT_MESSAGE);

      const header = `## "${orgName}" 입찰공고 검색 결과 (전체 ${result.totalCount}건)`;
      const body = result.items.map(formatBidListItem).join("\n\n");
      return toResult(`${header}\n\n${body}`);
    } catch (err) {
      return toErrorResult(err);
    }
  }
);

server.registerTool(
  "list_closing_soon_bids",
  {
    title: "마감 임박 IT 입찰공고",
    description: "입찰 마감이 N일 이내로 임박한 용역 입찰공고를 조회합니다.",
    inputSchema: {
      withinDays: z.number().int().min(1).max(30).default(3).describe("몇 일 이내 마감 (최대 30일)"),
      numOfRows: z.number().int().min(1).max(100).default(20).describe("결과 수"),
    },
  },
  async ({ withinDays, numOfRows }) => {
    try {
      // 조회 가능한 공고일 범위는 최대 31일이므로, 마감 기준일(withinDays)만큼 앞당겨 시작일을 잡는다.
      const bgn = todayYYYYMMDD(-(31 - withinDays));
      const end = todayYYYYMMDD(withinDays);
      const { items } = await callBidApi(LIST_PATHS.servc, {
        inqryDiv: 1,
        inqryBgnDt: `${bgn}0000`,
        inqryEndDt: `${end}2359`,
        pageNo: 1,
        numOfRows: 100,
      });

      const now = new Date();
      const deadline = new Date();
      deadline.setDate(deadline.getDate() + withinDays);

      const closingSoon = items
        .map((item) => {
          const closeDt = parseDateTimeValue(pick(item, ["bidClseDt", "bidClseDate"]));
          return { item, closeDt };
        })
        .filter(
          (entry): entry is { item: Record<string, any>; closeDt: Date } =>
            entry.closeDt !== undefined && entry.closeDt >= now && entry.closeDt <= deadline
        )
        .sort((a, b) => a.closeDt.getTime() - b.closeDt.getTime())
        .slice(0, clampNumOfRows(numOfRows));

      if (closingSoon.length === 0) return toResult(NO_RESULT_MESSAGE);

      const header = `## 마감 ${withinDays}일 이내 입찰공고 (${closingSoon.length}건)`;
      const body = closingSoon
        .map(({ item, closeDt }) => {
          const base = formatBidListItem(item);
          return `${base}\n- 남은 시간: ${formatRemaining(closeDt, now)}`;
        })
        .join("\n\n");
      return toResult(`${header}\n\n${body}`);
    } catch (err) {
      return toErrorResult(err);
    }
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((err) => {
  console.error("MCP 서버 시작 중 오류가 발생했습니다:", err);
  process.exit(1);
});
