import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

test("activity editor keeps information and images on one page", async () => {
  const source = await readFile("src/features/activities/ActivityEditorPage.tsx", "utf8");
  for (const label of ["目的地", "关联旅行产品", "活动图片", "解说文字"]) assert.match(source, new RegExp(label));
  assert.doesNotMatch(source, /<Tabs/);
});
