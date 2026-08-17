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
    experiences: [
      {title_zh: "科学中心", body_zh: "探险队讲座", media: []},
      {title_zh: "隐藏模块", body_zh: "", media: []},
    ],
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
  assert.equal(state.experiences.length, 1);
  assert.deepEqual(state.cabinGroups.map((group) => group.title), ["套房"]);
});

test("uses a built year only when no refurbishment year exists", () => {
  const state = buildVesselDetailState({year_built: 2020});

  assert.deepEqual(state.facilities, [{icon: "verified-badge", text: "建成于2020年"}]);
});

test("derives a safe vessel tone for remote facility icons", () => {
  assert.equal(buildVesselDetailState({card_tone: "#071A32"}).iconTone, "071A32");
  assert.equal(buildVesselDetailState({card_tone: "not-a-color"}).iconTone, "143f35");
});

test("uses a card visual as the immersive vessel detail hero", () => {
  assert.match(vesselMarkup, /<page-nav transparent="\{\{true\}\}" show-title="\{\{false\}\}" show-back="\{\{true\}\}"/);
  assert.match(vesselMarkup, /src="\{\{vessel\.card_image\}\}" mode="widthFix"/);
  assert.doesNotMatch(vesselMarkup, /vessel\.hero_image/);
  assert.match(vesselMarkup, /class="hero-official">\{\{vessel\.official_name\}\}/);
  assert.match(vesselMarkup, /class="hero-name">\{\{vessel\.name\}\}/);
  assert.match(vesselMarkup, /class="hero-intro">\{\{vessel\.intro_zh\}\}/);
  assert.match(vesselStyles, /\.hero-copy\s*\{[^}]*margin-top:\s*-172rpx/);
});

test("supports a transparent title-free page navigation variant", () => {
  assert.match(navMarkup, /class="nav \{\{transparent \? 'transparent' : ''\}\}"/);
  assert.match(navMarkup, /wx:if="\{\{showTitle\}\}" class="nav-title"/);
  assert.match(navStyles, /\.nav\.transparent\s*\{[^}]*position:\s*absolute[^}]*background:\s*transparent/);
  assert.match(navStyles, /\.nav\.transparent \.back-button\s*\{[^}]*color:\s*#fff/);
});

test("continues the hero card tone below the image for the full Chinese introduction", () => {
  assert.match(vesselMarkup, /class="hero" style="background-color: \{\{vessel\.card_tone \|\| '#143f35'\}\}"/);
  assert.match(vesselMarkup, /class="hero-intro">\{\{vessel\.intro_zh\}\}/);
  assert.doesNotMatch(vesselMarkup, /vessel-intro-card/);
  assert.match(vesselStyles, /\.hero-intro\s*\{[^}]*white-space:\s*pre-line/);
});

test("renders a two-column vessel facility grid instead of the green introduction card", () => {
  assert.doesNotMatch(vesselMarkup, /class="intro dark-intro"/);
  assert.match(vesselMarkup, /wx:if="\{\{detail\.facilities\.length\}\}" class="facility-grid"/);
  assert.match(vesselMarkup, /class="facility-icon" src="\{\{apiBaseUrl\}\}\/vessel-icons\/\{\{item\.icon\}\}\.svg\?tone=\{\{detail\.iconTone\}\}" mode="aspectFit"/);
  assert.match(vesselMarkup, /\{\{item\.text\}\}/);
  assert.match(vesselStyles, /\.facility-grid\s*\{[^}]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)/);
  assert.match(vesselStyles, /\.facility-grid\s*\{[^}]*background:\s*transparent/);
  assert.match(vesselStyles, /\.page\s*\{[^}]*background:\s*#F3F2EE/);
});
