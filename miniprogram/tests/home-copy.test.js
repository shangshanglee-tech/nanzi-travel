const fs = require("node:fs");
const path = require("node:path");
const test = require("node:test");
const assert = require("node:assert/strict");

const homeMarkup = fs.readFileSync(
  path.join(__dirname, "../pages/home/home.wxml"),
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
