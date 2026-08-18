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

test("shows only vessels that have a prepared card visual", () => {
  const homeScript = fs.readFileSync(path.join(__dirname, "../pages/home/home.js"), "utf8");

  assert.match(homeScript, /featured_vessels \|\| \[\]\)\.filter\(\(vessel\) => vessel\.card_image\)/);
});

test("uses the prepared vessel card image with bilingual vessel names and its Chinese summary", () => {
  assert.match(homeMarkup, /src="{{item\.card_image}}"/);
  assert.match(homeMarkup, /style="background-color: {{item\.card_tone}}"/);
  assert.doesNotMatch(homeMarkup, /class="vessel-fact"/);
  assert.match(homeMarkup, /class="vessel-summary">\{\{item\.summary\}\}/);
  assert.match(homeStyles, /\.vessel-card-body\s*\{[^}]*margin-top:\s*-172rpx/);
  assert.match(homeStyles, /\.vessel-card-body\s*\{[^}]*color:\s*#fff/);
  assert.match(homeStyles, /\.vessel-name\s*\{[^}]*font-size:\s*46rpx/);
  assert.match(homeStyles, /\.vessel-name\s*\{[^}]*margin-top:\s*16rpx/);
  assert.match(homeStyles, /\.vessel-official\s*\{[^}]*font-size:\s*24rpx[^}]*font-weight:\s*200[^}]*opacity:\s*1/);
  assert.match(homeStyles, /\.vessel-summary\s*\{[^}]*font-size:\s*26rpx[^}]*font-weight:\s*200/);
  assert.match(homeStyles, /\.vessel-summary\s*\{[^}]*margin-top:\s*24rpx/);
  assert.match(homeStyles, /\.vessel-summary\s*\{\s*display:\s*block;\s*overflow:\s*visible;\s*margin-top:\s*24rpx;\s*\}/);
});

test("marks vessel cards with the ship type icon in the upper right corner", () => {
  const shipIcon = fs.readFileSync(path.join(__dirname, "../assets/ship-white.svg"), "utf8");

  assert.match(homeMarkup, /class="vessel-type-mark"/);
  assert.match(homeMarkup, /src="\/assets\/ship-white\.svg"/);
  assert.match(homeStyles, /\.vessel-type-mark\s*\{[^}]*position:\s*absolute[^}]*top:\s*26rpx[^}]*right:\s*26rpx/);
  assert.match(homeStyles, /\.vessel-type-mark\s*\{[^}]*width:\s*81rpx[^}]*height:\s*81rpx/);
  assert.doesNotMatch(shipIcon, /#cdcdcd/i);
  assert.match(shipIcon, /fill="#FFFFFF"/);
});

test("marks every product card with the route type icon in the upper right corner", () => {
  const mapIcon = fs.readFileSync(path.join(__dirname, "../assets/map-white.svg"), "utf8");

  assert.match(homeMarkup, /class="product-type-mark"/);
  assert.match(homeMarkup, /src="\/assets\/map-white\.svg"/);
  assert.match(homeStyles, /\.product-type-mark\s*\{[^}]*position:\s*absolute[^}]*top:\s*26rpx[^}]*right:\s*26rpx/);
  assert.match(mapIcon, /fill="#FFFFFF"/);
});

test("uses the shared system font instead of device-dependent serif fallbacks", () => {
  assert.doesNotMatch(homeStyles, /font-family:\s*serif/);
  assert.doesNotMatch(navStyles, /font-family:\s*serif/);
});

test("lowers the brand eyebrow without moving the headline", () => {
  assert.match(homeStyles, /\.eyebrow\s*\{[^}]*transform:\s*translateY\(4rpx\)/);
});
