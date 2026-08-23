import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

test("activity editor keeps information and images on one page", async () => {
  const source = await readFile("src/features/activities/ActivityEditorPage.tsx", "utf8");
  const editor = await readFile("src/components/RichTextEditor.tsx", "utf8");
  for (const label of ["目的地", "活动图片", "活动介绍"]) assert.match(source, new RegExp(label));
  for (const label of ["加粗", "项目符号", "编号列表"]) assert.match(editor, new RegExp(label));
  assert.doesNotMatch(editor, /小标题/);
  assert.match(editor, /onPaste/);
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

test("operations console provides a reusable media library", async () => {
  const app = await readFile("src/App.tsx", "utf8");
  const picker = await readFile("src/components/MediaAssetPicker.tsx", "utf8");
  assert.match(app, /media-assets/);
  assert.match(picker, /从素材库选择/);
  assert.match(picker, /上传新素材/);
  assert.match(picker, /setFile\(selected\)/);
  const library = await readFile("src/features/media-assets/MediaAssetListPage.tsx", "utf8");
  assert.match(library, /编辑/);
  assert.match(library, /请先选择图片/);
  assert.match(library, /上传失败/);
  assert.match(library, /setFile\(selected\)/);
});
