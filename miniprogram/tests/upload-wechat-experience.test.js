const test = require("node:test");
const assert = require("node:assert/strict");

const {buildUploadConfig} = require("../../scripts/upload-wechat-experience.cjs");

test("builds an experience build version from the workflow run", () => {
  assert.deepEqual(
    buildUploadConfig({
      appid: "wx123",
      privateKeyPath: "/tmp/key",
      runNumber: "17",
      sha: "abc123def",
    }),
    {
      appid: "wx123",
      privateKeyPath: "/tmp/key",
      version: "0.1.17",
      desc: "release abc123d",
    },
  );
});
