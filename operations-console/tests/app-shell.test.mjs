import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

test("navigation contains only the three approved content entries", async () => {
  const source = await readFile("src/layout/OperationsLayout.tsx", "utf8");

  for (const label of ["旅行产品", "目的地", "船只"]) {
    assert.match(source, new RegExp(label));
  }
  assert.doesNotMatch(source, /站点设置|用户|认证和授权/);
});
