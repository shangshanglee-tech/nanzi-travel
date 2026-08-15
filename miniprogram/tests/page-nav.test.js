const test = require("node:test");
const assert = require("node:assert/strict");
const {getNavigationMetrics} = require("../../miniprogram/components/page-nav/metrics");
const appConfig = require("../../miniprogram/app.json");

test("uses the capsule right edge to reserve header space", () => {
  assert.deepEqual(
    getNavigationMetrics({top: 48, height: 32, right: 352}, 24, 375),
    {topPadding: 24, height: 44, rightPadding: 31}
  );
});

test("uses custom navigation globally", () => {
  assert.equal(appConfig.window.navigationStyle, "custom");
});
