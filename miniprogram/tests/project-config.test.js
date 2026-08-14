const test = require("node:test");
const assert = require("node:assert/strict");
const config = require("../project.config.json");

test("WeChat CI has a project configuration with the production app id", () => {
  assert.equal(config.appid, "wx9dacae494a7ff9ab");
  assert.equal(config.compileType, "miniprogram");
});
