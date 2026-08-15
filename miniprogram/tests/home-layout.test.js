const test = require("node:test");
const assert = require("node:assert/strict");
const {getHomeTopPadding} = require("../../miniprogram/pages/home/layout");

test("keeps the home eyebrow below a tall status bar", () => {
  assert.equal(getHomeTopPadding(59), 77);
});

test("uses a sensible fallback when system status is unavailable", () => {
  assert.equal(getHomeTopPadding(0), 38);
});
