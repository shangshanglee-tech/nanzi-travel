const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");

const homeMarkup = fs.readFileSync(
  path.join(__dirname, "../pages/home/home.wxml"),
  "utf8"
);
const homeStyles = fs.readFileSync(
  path.join(__dirname, "../pages/home/home.wxss"),
  "utf8"
);
const navStyles = fs.readFileSync(
  path.join(__dirname, "../components/page-nav/page-nav.wxss"),
  "utf8"
);

test("uses the compact two-line home hero copy", () => {
  assert.match(homeMarkup, /src="\/assets\/XNZ\.svg"/);
  assert.match(homeMarkup, /<view class="eyebrow">NANZI TRAVEL · 小楠子爱旅行<\/view>/);
  assert.match(homeMarkup, /<view class="headline">看更远的世界<\/view>/);
  assert.doesNotMatch(homeMarkup, /编辑精选|从南极开始/);
});

test("places the vessel section between the first and second product cards", () => {
  const vesselIndex = homeMarkup.indexOf('class="vessel-section"');
  const productLoopIndex = homeMarkup.indexOf('wx:for="{{products}}"');
  assert.ok(vesselIndex > productLoopIndex);
  assert.match(homeMarkup, /wx:if="{{index === 0 && vessels\.length}}"/);
});

test("uses a vertical vessel card list without a section heading", () => {
  assert.match(homeMarkup, /class="vessel-list"/);
  assert.doesNotMatch(homeMarkup, /认识探险船|每艘船都有不同气质|scroll-x class="vessel-scroll"/);
});

test("uses the shared system font instead of device-dependent serif fallbacks", () => {
  assert.doesNotMatch(homeStyles, /font-family:\s*serif/);
  assert.doesNotMatch(navStyles, /font-family:\s*serif/);
});
