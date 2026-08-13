const test = require("node:test");
const assert = require("node:assert/strict");

const {buildConsultationCopy, buildContactState} = require("../pages/contact/view-model");


test("consultation copy includes the selected product title", () => {
  assert.equal(
    buildConsultationCopy("12天南极半岛精华"),
    "我想咨询：12天南极半岛精华",
  );
});

test("contact state always keeps the official account fallback", () => {
  assert.deepEqual(
    buildContactState({}, ""),
    {
      officialAccountName: "小楠子爱旅行俱乐部",
      officialAccountGuide: "请在微信中搜索公众号名称并关注，获取人工咨询服务。",
      consultationCopy: "我想咨询小楠子的旅行产品",
    },
  );
});
