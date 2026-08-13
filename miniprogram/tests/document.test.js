const test = require("node:test");
const assert = require("node:assert/strict");

const {loadDocument} = require("../utils/document");


test("document loader returns local copy when site API is unavailable", async () => {
  const content = await loadDocument(
    () => Promise.reject(new Error("offline")),
    "privacy_text",
    "本地隐私说明",
  );

  assert.equal(content, "本地隐私说明");
});

test("document loader prefers published site copy", async () => {
  const content = await loadDocument(
    () => Promise.resolve({agreement_text: "后台发布的用户协议"}),
    "agreement_text",
    "本地协议",
  );

  assert.equal(content, "后台发布的用户协议");
});
