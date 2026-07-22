"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

type Page =
  | "home"
  | "create"
  | "search"
  | "messages"
  | "profile"
  | "product"
  | "buddy"
  | "collection";

type ProductId = "explorer-trail" | "antarctica-circle" | "antarctica-peninsula" | "antarctica-three-islands";

type ProductPreview = {
  id: ProductId;
  title: string;
  kicker: string;
  caption: string;
  tag: string;
  hero: string;
  duration: string;
  vessel: string;
  departure: string;
  overview: string;
  highlights: string[];
  itinerary: Array<{ day: string; title: string }>;
};

const productPreviews: Record<ProductId, ProductPreview> = {
  "explorer-trail": {
    id: "explorer-trail", title: "16天经典南极之旅", kicker: "2026—2027 航季 · HX 海达路德", caption: "探险家之路 · 深入威德尔海", tag: "产品推荐", hero: "/products/explorers-trail/hero.webp", duration: "16天", vessel: "阿蒙森号", departure: "团期待补", overview: "从布宜诺斯艾利斯出发，飞往乌斯怀亚登船，深入南极半岛东侧与威德尔海区域。", highlights: ["9天探索南极洲", "南设得兰群岛与威德尔海", "登陆、冲锋艇巡航与探险活动"], itinerary: [{ day: "DAY 1", title: "抵达布宜诺斯艾利斯" }, { day: "DAY 2", title: "飞往乌斯怀亚，登船" }, { day: "DAY 3—4", title: "穿越德雷克海峡" }, { day: "DAY 5—13", title: "探索南极洲" }, { day: "DAY 14—16", title: "返航并回到布宜诺斯艾利斯" }],
  },
  "antarctica-circle": {
    id: "antarctica-circle", title: "16天南极洲—南极圈深度探险", kicker: "时间更充裕的深度南极", caption: "争取穿越南极圈 · 探索玛格丽特湾", tag: "深度探索", hero: "/products/antarctica-circle/hero.webp", duration: "16天", vessel: "阿蒙森号", departure: "团期待补", overview: "在南极洲探索九天；天气和冰况允许时，尝试航行至南极圈以南的海域。", highlights: ["9天南极探索", "天气允许时穿越南极圈", "冰上巡航、登陆与野生动物观察"], itinerary: [{ day: "DAY 1", title: "抵达布宜诺斯艾利斯" }, { day: "DAY 2", title: "飞往乌斯怀亚，登上阿蒙森号" }, { day: "DAY 3—4", title: "穿越德雷克海峡" }, { day: "DAY 5—13", title: "南极洲与南极圈方向探索" }, { day: "DAY 14—16", title: "返航并回到布宜诺斯艾利斯" }],
  },
  "antarctica-peninsula": {
    id: "antarctica-peninsula", title: "12天南极半岛精华", kicker: "第一次去南极的经典路线", caption: "5天南极探索 · 14个出发团期", tag: "经典路线", hero: "/products/antarctica-peninsula/hero.webp", duration: "12天", vessel: "南森号", departure: "14个出发日", overview: "适合时间和预算相对有限、希望完整感受南极半岛的旅行者。", highlights: ["5天南极半岛探索", "登陆与冲锋艇巡航", "企鹅、鲸鱼与海豹的季节性观察"], itinerary: [{ day: "DAY 1", title: "抵达布宜诺斯艾利斯" }, { day: "DAY 2", title: "飞往乌斯怀亚，登上南森号" }, { day: "DAY 3—4", title: "穿越德雷克海峡" }, { day: "DAY 5—9", title: "南极半岛探索" }, { day: "DAY 10—12", title: "返航并回到布宜诺斯艾利斯" }],
  },
  "antarctica-three-islands": {
    id: "antarctica-three-islands", title: "23天南极三岛深度探险", kicker: "马尔维纳斯、南乔治亚与南极半岛", caption: "23天极致深度 · 6个出发团期", tag: "老板精选", hero: "/products/antarctica-three-islands/hero.webp", duration: "23天", vessel: "前进号", departure: "6个出发日", overview: "横跨马尔维纳斯群岛、南乔治亚岛与南极半岛，聚焦偏远群岛生态和野生动物。", highlights: ["3天马尔维纳斯群岛", "4天南乔治亚岛", "5天南极半岛探索"], itinerary: [{ day: "DAY 1—2", title: "圣地亚哥与蓬塔阿雷纳斯登船" }, { day: "DAY 3—6", title: "驶向并探索马尔维纳斯群岛" }, { day: "DAY 7—12", title: "航向并探索南乔治亚岛" }, { day: "DAY 13—19", title: "驶向并探索南极洲" }, { day: "DAY 20—23", title: "穿越德雷克海峡返航" }],
  },
};

const pageTitles: Record<Page, string> = {
  home: "首页",
  create: "发起搭子",
  search: "AI 搜索",
  messages: "消息",
  profile: "我的",
  product: "旅行产品",
  buddy: "搭子邀约",
  collection: "专题合集",
};

export default function Home() {
  const [page, setPage] = useState<Page>("home");
  const [selectedProductId, setSelectedProductId] = useState<ProductId>("explorer-trail");
  const [searchMode, setSearchMode] = useState<"product" | "buddy">("product");
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const contentRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    window.history.replaceState({ page: "home" }, "", "#home");
    const onPopState = (event: PopStateEvent) => {
      setPage((event.state?.page as Page) || "home");
    };
    window.addEventListener("popstate", onPopState);
    return () => window.removeEventListener("popstate", onPopState);
  }, []);

  const navigate = (next: Page) => {
    if (next === page) return;
    window.history.pushState({ page: next }, "", `#${next}`);
    setPage(next);
    contentRef.current?.scrollTo({ top: 0, behavior: "smooth" });
  };

  const goBack = () => {
    if (window.history.length > 1) window.history.back();
    else navigate("home");
  };

  const openProduct = (productId: ProductId) => {
    setSelectedProductId(productId);
    navigate("product");
  };

  const sendQuery = (event: FormEvent) => {
    event.preventDefault();
    if (!query.trim()) return;
    setAnswer(
      searchMode === "product"
        ? `我理解你想找“${query.trim()}”相关的旅行产品。这里先展示一个产品结果入口。`
        : `我理解你想找“${query.trim()}”相关的同行伙伴。这里先展示一个搭子结果入口。`,
    );
  };

  const showBack = !["home", "messages", "profile"].includes(page);

  return (
    <main className="app-shell">
      <header className="topbar">
        <div className="topbar-side">
          {showBack ? (
            <button className="icon-button" onClick={goBack} aria-label="返回上一页">
              ‹
            </button>
          ) : null}
        </div>
        <div className="topbar-title">{pageTitles[page]}</div>
        <div className="topbar-side topbar-side-right" />
      </header>

      <section className="page-content" ref={contentRef} key={page}>
        {page === "home" ? <HomePage navigate={navigate} openProduct={openProduct} /> : null}
        {page === "product" ? (
          selectedProductId === "explorer-trail" ? <ProductPage navigate={navigate} /> : <BasicProductPage product={productPreviews[selectedProductId]} navigate={navigate} />
        ) : null}
        {page === "buddy" ? <BuddyPage /> : null}
        {page === "collection" ? <CollectionPage navigate={navigate} /> : null}
        {page === "create" ? <CreatePage navigate={navigate} /> : null}
        {page === "search" ? (
          <SearchPage
            mode={searchMode}
            setMode={setSearchMode}
            query={query}
            setQuery={setQuery}
            answer={answer}
            sendQuery={sendQuery}
            navigate={navigate}
          />
        ) : null}
        {page === "messages" ? <MessagesPage navigate={navigate} /> : null}
        {page === "profile" ? <ProfilePage /> : null}
      </section>

      <nav className="bottom-nav" aria-label="主导航">
        <NavButton
          active={page === "home" || ["product", "buddy", "collection"].includes(page)}
          label="首页"
          icon="⌂"
          onClick={() => navigate("home")}
        />
        <NavButton
          active={page === "messages"}
          label="消息"
          icon="◉"
          onClick={() => navigate("messages")}
        />
        <NavButton
          active={page === "profile"}
          label="我的"
          icon="◎"
          onClick={() => navigate("profile")}
        />
      </nav>
    </main>
  );
}

function NavButton({
  active,
  label,
  icon,
  onClick,
}: {
  active: boolean;
  label: string;
  icon: string;
  onClick: () => void;
}) {
  return (
    <button className={`nav-button ${active ? "is-active" : ""}`} onClick={onClick}>
      <span className="nav-icon" aria-hidden="true">
        {icon}
      </span>
      <span>{label}</span>
    </button>
  );
}

function BuddyInviteButton({
  variant = "inline",
  className = "",
  onClick,
}: {
  variant?: "floating" | "inline" | "route";
  className?: string;
  onClick: () => void;
}) {
  return (
    <button
      className={`buddy-invite buddy-invite-${variant} ${className}`}
      style={variant === "floating" ? { width: "118px", maxWidth: "118px" } : undefined}
      onClick={onClick}
      aria-label="发起找搭子"
    >
      <span className="buddy-invite-mark" aria-hidden="true">
        <i>你</i><i>伴</i><b>＋</b>
      </span>
      <span className="buddy-invite-copy">
        <small>同行计划</small>
        <strong>{variant === "route" ? "为这条路线找同行者" : variant === "floating" ? "发起搭子" : "发起找搭子"}</strong>
      </span>
      <span className="buddy-invite-arrow" aria-hidden="true">↗</span>
    </button>
  );
}

function HomePage({ navigate, openProduct }: { navigate: (page: Page) => void; openProduct: (productId: ProductId) => void }) {
  return (
    <>
      <div className="eyebrow">TODAY · 编辑精选</div>
      <h1>这是首页</h1>
      <p className="lead">像浏览一本旅行杂志一样，发现产品、团期和同行伙伴。</p>

      <button
        className="story-card story-card-hero"
        onClick={() => openProduct("explorer-trail")}
        style={{
          backgroundImage:
            "linear-gradient(180deg, rgba(9, 30, 29, 0.08) 18%, rgba(9, 30, 29, 0.82) 100%), url('/products/explorers-trail/hero.webp')",
        }}
      >
        <span className="story-tag">产品推荐</span>
        <span className="story-spacer" />
        <span className="story-kicker">2026—2027 航季 · HX 海达路德</span>
        <strong>16天经典南极之旅</strong>
        <span>探险家之路 · 深入威德尔海</span>
      </button>

      <ProductHomeCard product={productPreviews["antarctica-circle"]} onClick={() => openProduct("antarctica-circle")} className="story-card-collection" />

      <ProductHomeCard product={productPreviews["antarctica-peninsula"]} onClick={() => openProduct("antarctica-peninsula")} className="story-card-peninsula" />

      <ProductHomeCard product={productPreviews["antarctica-three-islands"]} onClick={() => openProduct("antarctica-three-islands")} className="story-card-three-islands" />

      <button className="buddy-card" onClick={() => navigate("buddy")}>
        <span className="buddy-avatar">林</span>
        <span className="buddy-copy">
          <span className="story-tag dark">搭子招募</span>
          <strong>想找一位同行者去南极</strong>
          <span>北京 · 58岁 · 偏爱自然摄影</span>
          <span className="buddy-note">意向：2027年1月，愿意拼房</span>
        </span>
      </button>

      <button className="ai-entry-card" onClick={() => navigate("search")}>
        <span className="ai-entry-mark" aria-hidden="true">✦</span>
        <span className="ai-entry-copy">
          <span className="story-tag dark">AI 旅行顾问</span>
          <strong>说说你想去哪里</strong>
          <span>用自然语言寻找产品或同行搭子</span>
        </span>
        <span className="ai-entry-arrow" aria-hidden="true">›</span>
      </button>

      <button className="story-card story-card-month" onClick={() => navigate("collection")}>
        <span className="story-tag">按月份发现</span>
        <span className="story-spacer" />
        <span className="story-kicker">一月正值南极盛夏</span>
        <strong>1月出发的精选行程</strong>
        <span>查看全部相关产品和团期</span>
      </button>

      <button className="buddy-card buddy-card-alt" onClick={() => navigate("buddy")}>
        <span className="buddy-avatar">周</span>
        <span className="buddy-copy">
          <span className="story-tag dark">搭子招募</span>
          <strong>春节出发，时间可以商量</strong>
          <span>成都 · 43岁 · 轻松旅行节奏</span>
          <span className="buddy-note">已选择2个备选产品</span>
        </span>
      </button>
    </>
  );
}

function ProductHomeCard({ product, onClick, className }: { product: ProductPreview; onClick: () => void; className: string }) {
  return (
    <button
      className={`story-card ${className}`}
      onClick={onClick}
      style={{ backgroundImage: `linear-gradient(180deg, rgba(9, 30, 29, 0.08) 18%, rgba(9, 30, 29, 0.82) 100%), url('${product.hero}')` }}
    >
      <span className="story-tag">{product.tag}</span>
      <span className="story-spacer" />
      <span className="story-kicker">{product.kicker}</span>
      <strong>{product.title}</strong>
      <span>{product.caption}</span>
    </button>
  );
}

function MessagesPage({ navigate }: { navigate: (page: Page) => void }) {
  return (
    <>
      <div className="eyebrow">UPDATES</div>
      <h1>这是消息页面</h1>
      <p className="lead">集中查看公开留言、邀约进展和平台通知。</p>
      <div className="message-list">
        <button onClick={() => navigate("buddy")}>
          <span className="message-symbol interaction">言</span>
          <span><strong>新的公开留言</strong><small>有人回复了你的南极搭子邀约</small></span>
          <i />
        </button>
        <button onClick={() => navigate("buddy")}>
          <span className="message-symbol progress">伴</span>
          <span><strong>邀约进展</strong><small>你参与的邀约更新了候选行程</small></span>
          <i />
        </button>
        <button>
          <span className="message-symbol system">旅</span>
          <span><strong>平台通知</strong><small>行前咨询将由旅行顾问人工跟进</small></span>
        </button>
      </div>
    </>
  );
}

function BasicProductPage({ product, navigate }: { product: ProductPreview; navigate: (page: Page) => void }) {
  return (
    <>
      <div className="eyebrow">2026—2027 航季 · HX 海达路德</div>
      <h1>{product.title}</h1>
      <p className="lead">{product.overview}</p>
      <img className="product-hero-image" src={product.hero} alt={product.title} />
      <div className="product-stat-grid">
        <div><strong>{product.duration.replace("天", "")}</strong><span>天行程</span></div>
        <div><strong>{product.vessel}</strong><span>使用船只</span></div>
        <div><strong>{product.departure.includes("个") ? product.departure.split("个")[0] : "—"}</strong><span>{product.departure.includes("个") ? "个出发日" : "团期待补"}</span></div>
      </div>
      <section className="product-section departure-panel">
        <div className="section-heading"><div><span className="eyebrow">DEPARTURES</span><h2>出发团期</h2></div><span className="status-chip">{product.departure}</span></div>
        <p>{product.departure.includes("个") ? "原文已提供出发日期，价格与具体舱位仍需向旅行顾问确认。" : "原始资料尚未提供具体日期、价格与舱位；可先咨询并发起同行邀约。"}</p>
      </section>
      <section className="product-section">
        <span className="eyebrow">HIGHLIGHTS</span><h2>行程亮点</h2>
        <div className="highlight-list">{product.highlights.map((highlight, index) => <div key={highlight}><span>0{index + 1}</span><strong>{highlight}</strong></div>)}</div>
      </section>
      <section className="product-section">
        <span className="eyebrow">ITINERARY</span><h2>每日行程</h2>
        <div className="itinerary-list">{product.itinerary.map((item) => <div key={item.day}><span>{item.day}</span><strong>{item.title}</strong></div>)}</div>
      </section>
      <button className="primary-button">咨询这条路线</button>
      <BuddyInviteButton variant="route" onClick={() => navigate("create")} />
    </>
  );
}

function ProductPage({ navigate }: { navigate: (page: Page) => void }) {
  return (
    <>
      <div className="eyebrow">HX 海达路德 · 2026—2027 航季</div>
      <h1>16天经典南极之旅：探险家之路</h1>
      <p className="lead">从布宜诺斯艾利斯出发，飞往乌斯怀亚登船，深入南极半岛东侧与威德尔海区域。</p>

      <img className="product-hero-image" src="/products/explorers-trail/hero.webp" alt="南极冰海与远眺冰山" />

      <div className="product-stat-grid">
        <div><strong>16</strong><span>天行程</span></div>
        <div><strong>9</strong><span>天探索南极</span></div>
        <div><strong>HX</strong><span>探险游轮</span></div>
      </div>

      <section className="product-section departure-panel">
        <div className="section-heading">
          <div><span className="eyebrow">DEPARTURES</span><h2>选择出发团期</h2></div>
          <span className="status-chip">资料整理中</span>
        </div>
        <p>这条路线的标准行程已导入；具体出发日期、实时价格与舱位将在团期资料补齐后展示。</p>
        <BuddyInviteButton variant="route" onClick={() => navigate("create")} />
      </section>

      <section className="product-section">
        <span className="eyebrow">WHY THIS ROUTE</span>
        <h2>深入南极的奇观</h2>
        <p>这是一条为深度体验南极而设计的探险航程：在白色大陆停留九天，追随冰况与天气进入最值得探索的区域，寻找鲸鱼、海豹、企鹅与海鸟的踪迹。</p>
        <div className="highlight-list">
          <div><span>01</span><strong>探索南设得兰群岛、威德尔海与南极海峡</strong></div>
          <div><span>02</span><strong>乘小艇登陆，可体验皮划艇或雪鞋活动</strong></div>
          <div><span>03</span><strong>以天气与冰况为准，保留真正探险航程的弹性</strong></div>
        </div>
      </section>

      <section className="product-section image-split-section">
        <img src="/products/explorers-trail/route-map.webp" alt="探险家之路路线图" />
        <div>
          <span className="eyebrow">ROUTE</span>
          <h2>由南美洲，驶向更少人抵达的南极</h2>
          <p>航程从布宜诺斯艾利斯与乌斯怀亚开始，穿越德雷克海峡，在南极半岛东侧展开探索。</p>
        </div>
      </section>

      <section className="product-section">
        <span className="eyebrow">ITINERARY</span>
        <h2>每日行程</h2>
        <div className="itinerary-list">
          <div><span>DAY 1</span><strong>抵达布宜诺斯艾利斯</strong><p>抵达阿根廷首都，为探险之旅做好准备。</p></div>
          <div><span>DAY 2</span><strong>飞往乌斯怀亚，登上探险游轮</strong><p>从世界最南端城市出发，驶向南极。</p></div>
          <div><span>DAY 3—4</span><strong>穿越德雷克海峡</strong><p>与探险队一起了解南极知识，并准备登陆。</p></div>
          <div><span>DAY 5—13</span><strong>南极：另一个世界</strong><p>在南极半岛、威德尔海与周边水域灵活探索。</p></div>
          <div><span>DAY 14—15</span><strong>穿越德雷克海峡返航</strong><p>回顾旅程，在船上继续享受探险游轮生活。</p></div>
          <div><span>DAY 16</span><strong>抵达乌斯怀亚，返回布宜诺斯艾利斯</strong><p>结束航程，转乘飞机返回阿根廷首都。</p></div>
        </div>
      </section>

      <section className="product-section experience-gallery">
        <div className="section-heading"><div><span className="eyebrow">ON THE ICE</span><h2>登陆与野生动物</h2></div><span className="gallery-count">精选 2 图</span></div>
        <div className="gallery-grid">
          <img src="/products/explorers-trail/expedition.webp" alt="南极冲锋艇登陆体验" />
          <img src="/products/explorers-trail/wildlife.webp" alt="南极海豹与海鸟" />
        </div>
      </section>

      <section className="product-section ship-teaser">
        <img src="/products/explorers-trail/cabin.png" alt="阿蒙森号高级舱房" />
        <div>
          <span className="eyebrow">EXPEDITION SHIP</span>
          <h2>阿蒙森号</h2>
          <p>这艘混合动力探险游轮提供公共空间、餐饮、康体设施与多种舱房。船只内容将独立管理，供多条航线复用。</p>
          <button className="text-button">查看船只与舱位 ›</button>
        </div>
      </section>

      <section className="product-section cost-section">
        <span className="eyebrow">WHAT'S INCLUDED</span>
        <h2>费用说明</h2>
        <div className="cost-columns">
          <div><strong>费用包含</strong><ul><li>布宜诺斯艾利斯与乌斯怀亚间经济舱航班</li><li>探险巡游前一晚酒店与相关接送</li><li>所选船舱、每日三餐及部分饮品</li><li>船上讲座、科学中心及登陆活动</li><li>探险夹克、靴子和活动所需装备</li></ul></div>
          <div><strong>费用不含</strong><ul><li>国际航班与可能产生的额外住宿</li><li>旅游保险、行李搬运</li><li>可选岸上观光与小团体活动</li><li>船上健康与水疗区的可选服务</li></ul></div>
        </div>
      </section>

      <button className="primary-button">咨询这条路线</button>
      <BuddyInviteButton variant="route" onClick={() => navigate("create")} />
    </>
  );
}

function BuddyPage() {
  return (
    <>
      <div className="eyebrow">搭子详情</div>
      <h1>这是搭子卡片详情页</h1>
      <div className="profile-summary">
        <span className="large-avatar">林</span>
        <div>
          <h2>林女士</h2>
          <p>北京 · 58岁 · 退休人员</p>
        </div>
      </div>
      <div className="tag-row">
        <span>适度交流</span><span>自然摄影</span><span>可以拼房</span>
      </div>
      <p className="lead">这里以后展示自我介绍、意向产品、可接受团期、公开留言和平台历史服务记录。</p>
      <div className="comment-box">公开留言区域：这里暂时只显示文字占位。</div>
      <button className="primary-button">申请同行</button>
      <button className="secondary-button">发表公开留言</button>
    </>
  );
}

function CollectionPage({ navigate }: { navigate: (page: Page) => void }) {
  return (
    <>
      <div className="eyebrow">专题合集</div>
      <h1>这是产品合集页</h1>
      <p className="lead">合集可以按照船只、月份、路线或玩法自动组织产品。</p>
      <button className="compact-product" onClick={() => navigate("product")}>
        <span className="compact-cover">01</span>
        <span><strong>南极半岛经典11日</strong><small>2027年1月7日出发</small></span>
        <span>›</span>
      </button>
      <button className="compact-product" onClick={() => navigate("product")}>
        <span className="compact-cover second">02</span>
        <span><strong>穿越南极圈14日</strong><small>2027年1月21日出发</small></span>
        <span>›</span>
      </button>
    </>
  );
}

function CreatePage({ navigate }: { navigate: (page: Page) => void }) {
  return (
    <>
      <div className="eyebrow">CREATE</div>
      <h1>这是发起搭子页面</h1>
      <p className="lead">第一步选择一个或多个产品和团期，之后填写邀约说明。</p>
      <button className="select-card" onClick={() => navigate("product")}>
        <span>＋</span>
        <div><strong>选择旅行产品</strong><small>最多选择3个产品</small></div>
      </button>
      <label className="field-label" htmlFor="buddy-note">邀约说明</label>
      <textarea id="buddy-note" placeholder="简单介绍你想找什么样的同行伙伴……" />
      <button className="primary-button">预览搭子卡片</button>
    </>
  );
}

function SearchPage({
  mode,
  setMode,
  query,
  setQuery,
  answer,
  sendQuery,
  navigate,
}: {
  mode: "product" | "buddy";
  setMode: (mode: "product" | "buddy") => void;
  query: string;
  setQuery: (value: string) => void;
  answer: string;
  sendQuery: (event: FormEvent) => void;
  navigate: (page: Page) => void;
}) {
  return (
    <>
      <div className="eyebrow">AI TRAVEL ASSISTANT</div>
      <h1>这是AI搜索页面</h1>
      <p className="lead">你想寻找旅行产品，还是寻找同行伙伴？</p>
      <div className="segmented">
        <button className={mode === "product" ? "selected" : ""} onClick={() => setMode("product")}>找产品</button>
        <button className={mode === "buddy" ? "selected" : ""} onClick={() => setMode("buddy")}>找搭子</button>
      </div>
      <div className="assistant-bubble">
        {mode === "product"
          ? "可以告诉我你的目的地、时间、预算和期待的体验。"
          : "可以告诉我希望同行者的年龄、城市、旅行风格和意向产品。"}
      </div>
      <form className="search-form" onSubmit={sendQuery}>
        <input
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder={mode === "product" ? "例如：春节去南极，预算15万" : "例如：找一位北京出发的摄影搭子"}
        />
        <button type="submit">发送</button>
      </form>
      {answer ? (
        <div className="answer-block">
          <p>{answer}</p>
          <button className="compact-product" onClick={() => navigate(mode === "product" ? "product" : "buddy")}>
            <span className="compact-cover">AI</span>
            <span><strong>{mode === "product" ? "南极半岛经典11日" : "林女士的南极搭子邀约"}</strong><small>点击查看真实内容卡片</small></span>
            <span>›</span>
          </button>
        </div>
      ) : null}
    </>
  );
}

function ProfilePage() {
  return (
    <>
      <div className="eyebrow">PROFILE</div>
      <h1>这是我的页面</h1>
      <div className="profile-summary">
        <span className="large-avatar">旅</span>
        <div><h2>旅行用户</h2><p>个人资料待完善</p></div>
      </div>
      <div className="menu-list">
        <button><span>我的搭子邀约</span><span>›</span></button>
        <button><span>我的同行申请</span><span>›</span></button>
        <button><span>我的咨询</span><span>›</span></button>
        <button><span>消息中心</span><span>›</span></button>
        <button><span>规则与隐私</span><span>›</span></button>
      </div>
    </>
  );
}
