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
  assert.match(homeMarkup, /<view class="eyebrow">NANZI TRAVEL<\/view>/);
  assert.match(homeMarkup, /<view class="headline">看更远的世界<\/view>/);
  assert.doesNotMatch(homeMarkup, /编辑精选|从南极开始/);
});
