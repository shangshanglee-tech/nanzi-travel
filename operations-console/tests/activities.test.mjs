import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

test("activity editor keeps information and images on one page", async () => {
  const source = await readFile("src/features/activities/ActivityEditorPage.tsx", "utf8");
  const editor = await readFile("src/components/RichTextEditor.tsx", "utf8");
  for (const label of ["目的地", "活动图片", "活动介绍"]) assert.match(source, new RegExp(label));
  for (const label of ["小标题", "项目符号", "编号列表"]) assert.match(editor, new RegExp(label));
  assert.doesNotMatch(source, /关联旅行产品/);
  assert.match(source, />取消</);
  assert.doesNotMatch(source, />返回列表</);
  assert.doesNotMatch(source, /<Tabs/);
});

test("destination editor does not expose sorting or activation", async () => {
  const form = await readFile("src/features/destinations/DestinationFormModal.tsx", "utf8");
  const list = await readFile("src/features/destinations/DestinationListPage.tsx", "utf8");
  assert.doesNotMatch(form, /排序|启用|Switch|InputNumber/);
  assert.doesNotMatch(list, /排序|状态|changeActive|Switch/);
});

test("vessel list offers a new vessel action", async () => {
  const source = await readFile("src/features/vessels/VesselListPage.tsx", "utf8");
  assert.match(source, /新建船只/);
  assert.match(source, /\/vessels\/new/);
});
