import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

test("navigation follows the approved content configuration order", async () => {
  const source = await readFile("src/layout/OperationsLayout.tsx", "utf8");

  for (const label of ["目的地", "船只", "活动", "旅行产品"]) {
    assert.match(source, new RegExp(label));
  }
  assert.ok(source.indexOf("目的地") < source.indexOf("船只"));
  assert.ok(source.indexOf("船只") < source.indexOf("活动"));
  assert.ok(source.indexOf("活动") < source.indexOf("旅行产品"));
  assert.doesNotMatch(source, /站点设置|用户|认证和授权/);
});
