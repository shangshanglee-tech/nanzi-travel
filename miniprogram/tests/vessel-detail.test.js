const test = require("node:test");
const assert = require("node:assert/strict");

const {buildVesselDetailState} = require("../../miniprogram/pages/vessel-detail/view-model");

test("builds visible vessel modules and keeps cabin groups", () => {
  const state = buildVesselDetailState({
    capacity: 490,
    year_built: 2019,
    year_refurbished: 2025,
    experiences: [
      {title_zh: "科学中心", body_zh: "探险队讲座", media: []},
      {title_zh: "隐藏模块", body_zh: "", media: []},
    ],
    cabin_groups: [
      {title_zh: "套房", cabins: [{official_code: "MA", name: "XL 套房"}]},
      {title_zh: "空分组", cabins: []},
    ],
    media: [],
    products: [],
  });

  assert.deepEqual(state.facts, [
    {label: "载客", value: "约 490 位"},
    {label: "建造", value: "2019 年"},
    {label: "翻新", value: "2025 年"},
  ]);
  assert.equal(state.experiences.length, 1);
  assert.deepEqual(state.cabinGroups.map((group) => group.title), ["套房"]);
});
