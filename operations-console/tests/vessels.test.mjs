import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

test("vessel editor exposes core facts and card image management", async () => {
  const source = await readFile("src/features/vessels/VesselEditorPage.tsx", "utf8");
  assert.match(source, /结构化事实/);
  assert.match(source, /卡片图/);
  assert.match(source, /card_tone/);
});

test("vessel list does not render card images", async () => {
  const source = await readFile("src/features/vessels/VesselListPage.tsx", "utf8");
  assert.doesNotMatch(source, /卡片图/);
  assert.doesNotMatch(source, /<Image/);
});

test("vessel editor includes a page block composer with ordered content cards", async () => {
  const source = await readFile("src/features/vessels/VesselEditorPage.tsx", "utf8");
  assert.match(source, /PageBlockEditor/);
  const composer = await readFile("src/features/vessels/PageBlockEditor.tsx", "utf8");
  assert.match(composer, /上移/);
  assert.match(composer, /额外图片/);
});

test("vessel editor includes cabins and cabin display groups", async () => {
  const source = await readFile("src/features/vessels/VesselEditorPage.tsx", "utf8");
  assert.match(source, /CabinEditor/);
  const editor = await readFile("src/features/vessels/CabinEditor.tsx", "utf8");
  assert.match(editor, /舱位展示分组/);
  assert.match(editor, /MediaAssetPicker/);
});

test("vessel editor includes deck plan upload and deletion", async () => {
  const source = await readFile("src/features/vessels/VesselEditorPage.tsx", "utf8");
  assert.match(source, /DeckPlanEditor/);
  const editor = await readFile("src/features/vessels/DeckPlanEditor.tsx", "utf8");
  assert.match(editor, /甲板名称/);
  assert.match(editor, /SVG/);
});
