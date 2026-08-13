const test = require("node:test");
const assert = require("node:assert/strict");

const {toProductCard, collectFilterOptions} = require("../pages/products/view-model");


test("product card never invents a numeric price", () => {
  const card = toProductCard({
    title: "南极精华",
    slug: "antarctica-classic",
    duration_days: 12,
    subtitle: "经典路线",
  });

  assert.equal(card.priceLabel, "价格咨询");
  assert.equal(card.durationLabel, "12天");
  assert.equal(card.title, "南极精华");
});

test("filter options only contain values present in products", () => {
  const options = collectFilterOptions([
    {destination: {name: "南极", slug: "antarctica"}, tags: ["摄影", "首次去南极"]},
    {destination: {name: "南极", slug: "antarctica"}, tags: ["摄影"]},
  ]);

  assert.deepEqual(options.destinations, [{name: "南极", slug: "antarctica"}]);
  assert.deepEqual(options.tags, ["摄影", "首次去南极"]);
});
