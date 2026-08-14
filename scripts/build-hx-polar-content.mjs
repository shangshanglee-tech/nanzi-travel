import { mkdir, readFile, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const raw = JSON.parse(await readFile(resolve("content/imports/hx-antarctica.json"), "utf8"));
const now = new Date().toISOString();

const vessels = [
  {
    slug: "roald-amundsen", name: "阿蒙森号", official_name: "MS Roald Amundsen", capacity: 490, year_built: 2019,
    summary: "HX 新一代混合动力探险船。它把面向极地的探险能力、开阔的公共空间与更完整的船上科学体验放在同一条船上，适合希望在舒适度与深度探索之间取得平衡的旅行者。",
    features: ["混合动力探险船", "船上科学中心", "全景公共空间", "探险队带领登陆与巡航"],
    source_url: "https://www.travelhx.com/ships/roald-amundsen/", review_status: "pending",
    cabins: [
      {name: "探险套房", category: "套房", summary: "适合重视私密空间与船上服务体验的旅客；部分房型配有阳台或更开阔的窗景。", highlights: ["更宽裕的起居空间", "部分房型带阳台", "套房礼遇以最终团期为准"]},
      {name: "北极高级舱", category: "高级舱", summary: "在舒适度、景观与预算之间取得平衡的主力选择。", highlights: ["自然采光", "适合双人入住", "房型细节以具体舱号为准"]},
      {name: "极地海景舱", category: "海景舱", summary: "希望保有窗景、同时控制整体预算的旅行者可优先关注。", highlights: ["设有窗景", "双人入住为主", "部分房型可选双床"]},
    ],
  },
  {
    slug: "fridtjof-nansen", name: "南森号", official_name: "MS Fridtjof Nansen", capacity: 490, year_built: 2020,
    summary: "HX 新一代混合动力探险船，以明亮的北欧风格公共空间、科学中心和高比例外舱体验见长。它适合第一次前往南极、同时希望船上体验更完整的旅行者。",
    features: ["混合动力探险船", "北欧风格内装", "科学中心与探险讲座", "全景观景与公共空间"],
    source_url: "https://www.travelhx.com/ships/fridtjof-nansen/", review_status: "pending",
    cabins: [
      {name: "探险套房", category: "套房", summary: "为希望在极地探险外获得更高私密度与服务感的旅客准备。", highlights: ["更大空间", "部分房型带阳台", "床型与礼遇以实际舱号为准"]},
      {name: "北极高级舱", category: "高级舱", summary: "兼顾空间感、自然光与整体预算的舒适型选择。", highlights: ["采光良好", "适合双人入住", "部分房型可灵活安排床型"]},
      {name: "极地海景舱", category: "海景舱", summary: "保留极地窗景体验的实用选择。", highlights: ["设有窗景", "双人入住为主", "具体视野以舱号为准"]},
    ],
  },
  {
    slug: "fram", name: "前进号", official_name: "MS Fram", capacity: 200, year_built: 2007,
    summary: "一艘为极地打造的紧凑型探险船，约 200 位宾客的规模让船上氛围更亲近；更新后的科学中心、探险休息区与公共空间，使它成为偏好小船感和远征气质的选择。",
    features: ["约200位宾客的小船体验", "为极地航行打造", "升级科学中心", "探险休息区与全景酒廊"],
    source_url: "https://www.travelhx.com/en-us/ships/fram/", review_status: "pending",
    cabins: [
      {name: "探险套房", category: "套房", summary: "前进号上空间更充裕的住宿选择，适合希望拥有更多起居空间的旅客。", highlights: ["部分房型带阳台", "更开阔的窗景", "套房礼遇以实际团期为准"]},
      {name: "北极高级舱", category: "高级舱", summary: "以更舒适的空间和自然采光提升长航段的居住体验。", highlights: ["窗景或更佳视野", "适合双人入住", "具体配置因舱号而异"]},
      {name: "极地海景舱", category: "海景舱", summary: "适合希望保有窗景、又重视预算效率的旅客。", highlights: ["设有窗景", "部分视野可能受限", "床型以实际舱号为准"]},
      {name: "极地内舱", category: "内舱", summary: "将预算更多放在目的地与探险体验上的实用选择。", highlights: ["无窗", "双人入住为主", "适合对白天船上活动投入更高的旅客"]},
    ],
  },
];

const routeCopy = {
  "life-returns-springtime-expedition-to-antarctica": ["23天南极春季三岛远征", "从福克兰、南乔治亚一路进入南极半岛的长线远征。晚春时节的冰景与繁殖季野生动物，让这条路线适合愿意为更完整南大洋体验投入时间的旅行者。", ["福克兰、南乔治亚与南极半岛三岛串联", "晚春冰景与繁殖季野生动物", "在南极停留多日，节奏更从容"]],
  "highlights-of-antarctica": ["12天南极半岛精华", "第一次去南极、又希望在时间与预算之间保持效率的经典选择。以南极半岛、登陆、小艇巡航与野生动物观察为核心，完整体验极地探险的入门精华。", ["5天左右南极半岛探索窗口", "登陆与小艇巡航结合", "适合首次前往南极"]],
  "iconic-antarctica-the-explorers-route": ["16天经典南极之旅", "比常规半岛行程多出更长的南极探索时间，向威德尔海及南极半岛更偏远的海峡延伸。适合希望把重点放在南极本身、而非只完成一次打卡的旅行者。", ["约9天南极探索", "威德尔海与偏远海峡", "深度体验型经典路线"]],
  "in-depth-antarctica-falklands-south-georgia-expedition": ["23天南极三岛深度探险", "一条把福克兰、南乔治亚和南极半岛真正串起来的远征路线。时间足够时，野生动物、岛屿生态与南极冰原会构成层次更完整的南大洋体验。", ["三岛深度串联", "南乔治亚野生动物", "适合时间充裕的深度旅行者"]],
  "antarctica-falklands-expedition": ["16天南极与福克兰探险", "在南极半岛之外加入福克兰群岛，让这趟旅程同时拥有冰原、海鸟、企鹅与海岛生活的不同层次。", ["南极半岛与福克兰双区域", "野生动物观察层次丰富", "适合希望延展经典半岛体验的旅行者"]],
  "antarctic-circle-expedition": ["16天南极圈探险", "在更长的南极探索窗口中，争取向南极圈以南航行。是否穿越取决于冰况与天气，正是它比常规路线更具探险感的原因。", ["尝试穿越南极圈", "约9天南极探索", "天气与冰况决定最终航线"]],
  "south-georgia-and-falklands-from-punta-arenas-to-montevideo": ["18天南乔治亚与福克兰", "以南乔治亚和福克兰为主角的野生动物远征。它把重点放在偏远岛屿生态、海鸟与企鹅繁殖地，适合对南极三岛有明确兴趣的旅行者。", ["南乔治亚深度停留", "福克兰群岛生态体验", "偏重野生动物与海岛远征"]],
  "antarctica-and-falklands-expedition-2027": ["19天南极与福克兰北向航线", "从南极出发一路向北连接福克兰群岛，在冰原之外加入更丰富的岛屿生态与航海层次。", ["南极与福克兰双区域", "北向航线", "兼顾冰原与岛屿野生动物"]],
  "life-returns-springtime-expedition-to-antarctica-2027": ["23天南极春季三岛远征（2027）", "与春季三岛远征相同的核心逻辑：从福克兰、南乔治亚进入南极，在晚春的纯净冰景和繁殖季生态中完成一次长线远征。", ["三岛长线远征", "晚春冰景", "野生动物繁殖季"]],
  "antarctica-patagonia-expedition": ["18天南极与巴塔哥尼亚", "将南极探险与巴塔哥尼亚风景串联，是希望一次旅行同时感受南美大陆与南极冰原的长线选择。", ["南极与巴塔哥尼亚组合", "南美大陆与极地双体验", "适合长假深度旅行"]],
  "antarctica-falklands-northbound-expedition-2028": ["17天南极与福克兰北向航线", "从南极向北延伸至福克兰群岛，用更长的时间感受冰原、海峡与岛屿野生动物之间的变化。", ["南极与福克兰串联", "北向航线", "冰原与岛屿生态兼得"]],
};

function segmentCopy(title) {
  const text = title.toLowerCase();
  if (text.includes("drake") || text.includes("passage")) return ["穿越德雷克海峡", "在前往或离开南极的航程中，探险队会通过讲座、装备说明和科学中心活动帮助你进入探险状态；海况与天气将决定航行节奏。"];
  if (text.includes("antarctica") || text.includes("ice") || text.includes("wonder")) return ["南极探索日", "在天气、冰况和野生动物状况允许的前提下，探险队会安排登陆、小艇巡航、徒步或自然观察。每天的具体地点由当日条件决定，这正是极地探险最真实的部分。"];
  if (text.includes("falkland") || text.includes("island life")) return ["福克兰群岛探索", "根据海况选择适合登陆的岛屿，观察海鸟、企鹅与开阔的海岛地貌；具体登陆点以探险队当天安排为准。"];
  if (text.includes("south georgia") || text.includes("serengeti")) return ["南乔治亚岛探索", "这里以企鹅、海豹和海鸟繁殖地闻名。探险队会在许可与天气允许时安排登陆和自然观察。"];
  if (text.includes("buenos") || text.includes("ushuaia") || text.includes("arrival")) return ["抵达与登船", "抵达南美出发城市，完成行前集合或转机，并在指定港口登上探险船，正式开启南极航程。"];
  if (text.includes("atlantic") || text.includes("bound") || text.includes("sea")) return ["海上航行与准备", "在海上航段休整、参加探险队讲座，并为下一段目的地做好准备。"];
  return ["探险航程", "跟随探险队在当天条件允许的范围内继续航行、观察与探索；具体安排以船长和探险队决定为准。"];
}

function nextData(html) {
  const match = html.match(/<script id="__NEXT_DATA__" type="application\/json">([\s\S]*?)<\/script>/);
  if (!match) throw new Error("HX 页面缺少路线数据");
  return JSON.parse(match[1]).props.pageProps.voyage;
}

function vesselSlug(packageCode, allowed) {
  if (packageCode.startsWith("RA")) return "roald-amundsen";
  if (packageCode.startsWith("FN")) return "fridtjof-nansen";
  if (packageCode.startsWith("FR")) return "fram";
  if (allowed.length === 1) return allowed[0];
  throw new Error(`无法从航次编号判断执行船：${packageCode}`);
}

const products = [];
for (const rawProduct of raw.products) {
  const copy = routeCopy[rawProduct.id];
  if (!copy) throw new Error(`缺少中文文案：${rawProduct.id}`);
  const voyage = nextData(await (await fetch(rawProduct.sourceUrl)).text());
  const allowed = rawProduct.shipIds;
  const departures = (voyage.availability?.availabilityData?.voyages || []).map((item) => ({
    start_date: item.date,
    label: `${item.date} 出发`,
    vessel_slug: vesselSlug(item.packageCode || "", allowed),
  })).filter((item) => item.start_date);
  products.push({
    slug: rawProduct.id,
    subtitle: copy[0], summary: copy[1], highlights: copy[2],
    season: "2026–2028 南极航季", departure_city: "以具体团期为准",
    tags: [rawProduct.group, "HX Expeditions", "南极探险"],
    suitable_for: ["希望深入了解南极自然与野生动物的旅行者"],
    notices: ["极地行程受天气、冰况、野生动物和船长决定影响，具体安排以当日探险队通知为准。"],
    vessel_slugs: allowed,
    departures,
    itinerary_segments: rawProduct.itinerary.map((segment) => {
      const [title, description] = segmentCopy(segment.title);
      return {source_range: segment.day, title, description};
    }),
    source_url: rawProduct.sourceUrl, source_fetched_at: now, review_status: "pending",
  });
}

await mkdir(resolve("content/imports"), {recursive: true});
await writeFile(resolve("content/imports/hx-polar-content.json"), `${JSON.stringify({source: "HX official pages", imported_at: now, vessels, products}, null, 2)}\n`);
console.log(`已生成 ${products.length} 条中文路线、${vessels.length} 艘船与 ${products.reduce((total, item) => total + item.departures.length, 0)} 个团期。`);
