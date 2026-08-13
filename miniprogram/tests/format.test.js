const test = require("node:test");
const assert = require("node:assert/strict");

const { formatDuration } = require("../utils/format");


test("formatDuration uses Chinese day unit", () => {
  assert.equal(formatDuration(12), "12天");
});

test("formatDuration hides missing values", () => {
  assert.equal(formatDuration(null), "");
});
