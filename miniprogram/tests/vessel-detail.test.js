const test = require("node:test");
const assert = require("node:assert/strict");

const {buildVesselDetailState} = require("../../miniprogram/pages/vessel-detail/view-model");
const fs = require("node:fs");
const path = require("node:path");

const vesselMarkup = fs.readFileSync(
  path.join(__dirname, "../pages/vessel-detail/vessel-detail.wxml"),
  "utf8"
);
const vesselStyles = fs.readFileSync(
  path.join(__dirname, "../pages/vessel-detail/vessel-detail.wxss"),
  "utf8"
);
const vesselScript = fs.readFileSync(
  path.join(__dirname, "../pages/vessel-detail/vessel-detail.js"),
  "utf8"
);
const navMarkup = fs.readFileSync(
  path.join(__dirname, "../components/page-nav/page-nav.wxml"),
  "utf8"
);
const navStyles = fs.readFileSync(
  path.join(__dirname, "../components/page-nav/page-nav.wxss"),
  "utf8"
);

test("builds ordered visible vessel facilities and keeps cabin groups", () => {
  const state = buildVesselDetailState({
    capacity: 490,
    year_built: 2019,
    year_refurbished: 2025,
    has_science_center: true,
    has_wifi: true,
    is_hybrid: true,
    has_stabilization_system: true,
    restaurant_count: 3,
    bar_count: 2,
    has_executive_lounge: true,
    has_sauna: true,
    has_infinity_pool: true,
    heated_pool_count: 1,
    has_fitness_center: true,
    show_cabins: true,
    show_deck_plans: true,
    page_blocks: [
      {block_type: "heading", title: "探索与学习"},
      {
        block_type: "card",
        title: "科学中心",
        images: ["https://example.test/science.webp", "https://example.test/science-2.webp"],
        body: "跟随探险队理解极地。",
      },
      {block_type: "card", title: "缺图卡片", images: [], body: "不展示"},
    ],
    deck_plans: [{title: "7 层甲板", description: "公共区域", image: "https://example.test/deck-7.webp"}],
    cabin_groups: [
      {title_zh: "套房", cabins: [{official_code: "MA", name: "XL 套房"}]},
      {title_zh: "空分组", cabins: []},
    ],
    media: [],
    products: [],
  });

  assert.deepEqual(state.facilities, [
    {icon: "verified-badge", text: "2025年翻新"},
    {icon: "capacity", text: "最大载客量 490"},
    {icon: "science_center", text: "科研中心"},
    {icon: "wifi", text: "免费 Wi-Fi"},
    {icon: "hybrid", text: "环保混合动力引擎"},
    {icon: "modern_stable_tech", text: "船身稳定技术"},
    {icon: "restaurants", text: "3 个餐厅"},
    {icon: "bars", text: "2 个酒吧"},
    {icon: "lounge", text: "行政酒廊"},
    {icon: "spa", text: "桑拿房"},
    {icon: "swimming_pool", text: "无边泳池"},
    {icon: "hot_tubs", text: "1 个恒温泳池"},
    {icon: "fitness", text: "健身房"},
  ]);
  assert.deepEqual(state.pageBlocks.map((block) => block.title), ["探索与学习", "科学中心"]);
  assert.equal(state.pageBlocks[1].images.length, 2);
  assert.equal(state.cabinGroups.length, 1);
  assert.equal(state.deckPlans[0].title, "7 层甲板");
  assert.deepEqual(state.cabinGroups.map((group) => group.title), ["套房"]);
});

test("uses a built year only when no refurbishment year exists", () => {
  const state = buildVesselDetailState({year_built: 2020});

  assert.deepEqual(state.facilities, [{icon: "verified-badge", text: "建成于2020年"}]);
});

test("hides optional tail modules when vessel settings turn them off", () => {
  const state = buildVesselDetailState({
    show_cabins: false,
    show_deck_plans: false,
    cabin_groups: [{title_zh: "套房", cabins: [{name: "XL 套房"}]}],
    deck_plans: [{title: "7 层甲板", image: "https://example.test/deck-7.webp"}],
  });

  assert.deepEqual(state.cabinGroups, []);
  assert.deepEqual(state.deckPlans, []);
});

test("derives a safe vessel tone for remote facility icons", () => {
  assert.equal(buildVesselDetailState({card_tone: "#071A32"}).iconTone, "071A32");
  assert.equal(buildVesselDetailState({card_tone: "not-a-color"}).iconTone, "143f35");
});

test("uses a card visual as the immersive vessel detail hero", () => {
  assert.match(vesselMarkup, /<page-nav title="\{\{vessel\.name\}\}" transparent="\{\{true\}\}" show-title="\{\{navCollapsed\}\}" show-back="\{\{true\}\}" collapsed="\{\{navCollapsed\}\}" background-color="\{\{vessel\.card_tone \|\| '#143f35'\}\}"/);
  assert.match(vesselMarkup, /src="\{\{vessel\.card_image\}\}" mode="widthFix"/);
  assert.doesNotMatch(vesselMarkup, /vessel\.hero_image/);
  assert.match(vesselMarkup, /class="hero-official">\{\{vessel\.official_name\}\}/);
  assert.match(vesselMarkup, /class="hero-name">\{\{vessel\.name\}\}/);
  assert.match(vesselMarkup, /class="hero-intro">\{\{vessel\.intro_zh\}\}/);
  assert.match(vesselStyles, /\.hero-copy\s*\{[^}]*margin-top:\s*-172rpx/);
  assert.match(vesselStyles, /\.hero-official\s*\{[^}]*font-size:\s*24rpx[^}]*font-weight:\s*200[^}]*opacity:\s*1/);
  assert.match(vesselStyles, /\.hero-name\s*\{[^}]*margin-top:\s*12rpx[^}]*font-size:\s*46rpx[^}]*font-weight:\s*500/);
  assert.match(vesselStyles, /\.hero-intro\s*\{[^}]*margin-top:\s*24rpx/);
});

test("supports a transparent title-free page navigation variant", () => {
  assert.match(navMarkup, /class="nav \{\{transparent && !collapsed \? 'transparent' : ''\}\} \{\{collapsed \? 'collapsed' : ''\}\}"/);
  assert.match(navMarkup, /wx:if="\{\{showTitle\}\}" class="nav-title"/);
  assert.match(navStyles, /\.nav\.transparent\s*\{[^}]*position:\s*absolute[^}]*background:\s*transparent/);
  assert.match(navStyles, /\.nav\.transparent \.back-button\s*\{[^}]*color:\s*#fff/);
});

test("collapses the vessel hero into a fixed, tone-matched title navigation after scrolling", () => {
  assert.match(vesselScript, /navCollapsed:\s*false/);
  assert.match(vesselScript, /navCollapseOffset:\s*260/);
  assert.match(vesselScript, /onPageScroll\(event\)\s*\{[^}]*scrollTop >= this\.data\.navCollapseOffset/);
  assert.match(navMarkup, /transparent && !collapsed/);
  assert.match(navMarkup, /collapsed \? 'collapsed' : ''/);
  assert.match(navMarkup, /background-color: \{\{collapsed \? backgroundColor : 'transparent'\}\}/);
  assert.match(navStyles, /\.nav\.collapsed\s*\{[^}]*position:\s*fixed/);
  assert.match(navStyles, /\.nav\.collapsed \.nav-title\s*\{[^}]*text-align:\s*left/);
  assert.match(navStyles, /\.nav\.collapsed \.back-button, \.nav\.collapsed \.nav-title\s*\{[^}]*color:\s*#fff/);
});

test("continues the hero card tone below the image for the full Chinese introduction", () => {
  assert.match(vesselMarkup, /class="hero" style="background-color: \{\{vessel\.card_tone \|\| '#143f35'\}\}"/);
  assert.match(vesselMarkup, /class="hero-intro">\{\{vessel\.intro_zh\}\}/);
  assert.doesNotMatch(vesselMarkup, /vessel-intro-card/);
  assert.match(vesselStyles, /\.hero-intro\s*\{[^}]*color:\s*#fff[^}]*font-size:\s*26rpx[^}]*font-weight:\s*200[^}]*line-height:\s*36rpx[^}]*white-space:\s*pre-line/);
});

test("renders a two-column vessel facility grid instead of the green introduction card", () => {
  assert.doesNotMatch(vesselMarkup, /class="intro dark-intro"/);
  assert.match(vesselMarkup, /wx:if="\{\{detail\.facilities\.length\}\}" class="facility-grid"/);
  assert.match(vesselMarkup, /class="facility-icon" src="\{\{apiBaseUrl\}\}\/vessel-icons\/\{\{item\.icon\}\}\.svg\?tone=\{\{detail\.iconTone\}\}" mode="aspectFit"/);
  assert.match(vesselMarkup, /\{\{item\.text\}\}/);
  assert.match(vesselStyles, /\.facility-grid\s*\{[^}]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/);
  assert.match(vesselStyles, /\.facility-grid\s*\{[^}]*padding:\s*96rpx 52rpx 52rpx/);
  assert.match(vesselStyles, /\.facility-grid\s*\{[^}]*background:\s*transparent/);
  assert.match(vesselStyles, /\.facility-item\s*\{[^}]*font-size:\s*24rpx[^}]*font-weight:\s*500/);
  assert.match(vesselStyles, /\.page\s*\{[^}]*background:\s*#F3F2EE/);
  assert.doesNotMatch(vesselStyles, /outline:\s*2rpx/);
});

test("renders operator page blocks as a continuous information flow before optional tail modules", () => {
  assert.match(vesselMarkup, /wx:if="\{\{detail\.pageBlocks\.length\}\}" class="page-composer"/);
  assert.match(vesselMarkup, /item\.block_type === 'heading'/);
  assert.match(vesselMarkup, /wx:if="\{\{item\.images\.length > 1\}\}" class="composer-card-swiper"/);
  assert.match(vesselMarkup, /class="composer-card-image" src="\{\{image\}\}" mode="aspectFill"/);
  assert.match(vesselMarkup, /indicator-color="rgba\(255,255,255,\.25\)"/);
  assert.match(vesselMarkup, /indicator-active-color="#ffffff"/);
  assert.match(vesselMarkup, /indicator-dots="\{\{true\}\}"/);
  assert.match(vesselMarkup, /class="composer-card-image" src="\{\{item\.images\[0\]\}\}" mode="aspectFill"/);
  assert.match(vesselMarkup, /wx:if="\{\{detail\.showCabins && detail\.cabinGroups\.length\}\}"/);
  assert.match(vesselMarkup, /wx:if="\{\{detail\.deckPlans\.length\}\}" class="page-composer deck-plans"/);
  assert.match(vesselMarkup, /class="composer-heading" style="\{\{detail\.cardToneStyle\}\}">甲板舱位图<\/view>/);
  assert.match(vesselMarkup, /wx:if="\{\{detail\.deckPlans\.length > 1\}\}" class="deck-plan-swiper" current="\{\{deckPlanIndex\}\}" bindchange="changeDeckPlan"/);
  assert.match(vesselMarkup, /<swiper-item wx:for="\{\{detail\.deckPlans\}\}" wx:key="image">/);
  assert.match(vesselMarkup, /class="deck-plan-image" src="\{\{item\.image\}\}" mode="aspectFit"/);
  assert.match(vesselMarkup, /class="deck-plan-image" src="\{\{detail\.deckPlans\[0\]\.image\}\}" mode="aspectFit"/);
  assert.match(vesselMarkup, /class="composer-card-body deck-plan-body"/);
  assert.match(vesselMarkup, /class="deck-plan-name">\{\{currentDeckPlan\.title\}\}/);
  assert.match(vesselMarkup, /class="deck-plan-copy">\{\{currentDeckPlan\.description\}\}/);
  assert.match(vesselScript, /deckPlanIndex:\s*0/);
  assert.match(vesselScript, /currentDeckPlan:/);
  assert.match(vesselScript, /changeDeckPlan\(event\)/);
  assert.match(vesselScript, /event\.detail\.current/);
  assert.match(vesselStyles, /\.deck-plan-image\s*\{[^}]*height:\s*527rpx[^}]*background:\s*#fff/);
  assert.match(vesselStyles, /\.deck-plan-swiper\s*\{[^}]*height:\s*527rpx/);
  assert.doesNotMatch(vesselMarkup, /class="gallery-scroll"/);
  assert.doesNotMatch(vesselMarkup, /class="experience"/);
  assert.match(vesselMarkup, /class="composer-heading" style="\{\{detail\.cardToneStyle\}\}"/);
  assert.match(vesselStyles, /\.composer-heading\s*\{[^}]*margin:\s*96rpx 8rpx 52rpx[^}]*font-size:\s*48rpx[^}]*font-weight:\s*500/);
  assert.match(vesselStyles, /\.composer-card\s*\{[^}]*margin-bottom:\s*52rpx/);
  assert.match(vesselStyles, /\.composer-card-swiper\s*\{[^}]*height:\s*527rpx/);
  assert.match(vesselStyles, /\.composer-card-image\s*\{[^}]*height:\s*527rpx/);
  assert.doesNotMatch(vesselStyles, /composer-card-image-backdrop/);
  assert.match(vesselStyles, /\.composer-card-title\s*\{[^}]*padding:\s*24rpx 28rpx 12rpx[^}]*font-size:\s*36rpx[^}]*font-weight:\s*500/);
  assert.match(vesselStyles, /\.composer-card-body\s*\{[^}]*padding:\s*0 28rpx 52rpx[^}]*color:\s*rgba\(0,0,0,\.65\)[^}]*font-size:\s*26rpx[^}]*font-weight:\s*400/);
});
