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
      sessionFrom: "咨询来源=小楠子爱旅行",
    },
  );
});

test("consultation copy carries route, departure and vessel context", () => {
  assert.equal(
    buildConsultationCopy("12天南极半岛精华", "2026-12-09", "南森号"),
    "我想咨询：12天南极半岛精华\n团期：2026-12-09\n执行船只：南森号",
  );
});

test("contact state provides compact customer-service session context", () => {
  assert.equal(
    buildContactState({}, "12天南极半岛精华", "2026-12-09", "南森号").sessionFrom,
    "产品=12天南极半岛精华；团期=2026-12-09；船只=南森号",
  );
});
