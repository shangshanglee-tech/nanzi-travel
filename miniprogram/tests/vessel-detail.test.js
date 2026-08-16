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

test("builds visible vessel modules and keeps cabin groups", () => {
  const state = buildVesselDetailState({
    capacity: 490,
    year_built: 2019,
    year_refurbished: 2025,
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

  assert.deepEqual(state.facts, [
    {label: "载客", value: "约 490 位"},
    {label: "建造", value: "2019 年"},
    {label: "翻新", value: "2025 年"},
  ]);
  assert.equal(state.experiences.length, 1);
  assert.deepEqual(state.cabinGroups.map((group) => group.title), ["套房"]);
});

test("uses a card visual as the immersive vessel detail hero", () => {
  assert.match(vesselMarkup, /<page-nav transparent="\{\{true\}\}" show-title="\{\{false\}\}" show-back="\{\{true\}\}"/);
  assert.match(vesselMarkup, /src="\{\{vessel\.card_image \|\| vessel\.hero_image\}\}" mode="widthFix"/);
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
