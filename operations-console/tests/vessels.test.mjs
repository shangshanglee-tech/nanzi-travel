import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

test("vessel editor exposes core facts and card image management", async () => {
  const source = await readFile("src/features/vessels/VesselEditorPage.tsx", "utf8");
  assert.match(source, /结构化事实/);
  assert.match(source, /卡片图/);
  assert.match(source, /card_tone/);
});

test("vessel editor includes a page block composer with ordered content cards", async () => {
  const source = await readFile("src/features/vessels/VesselEditorPage.tsx", "utf8");
  assert.match(source, /PageBlockEditor/);
  const composer = await readFile("src/features/vessels/PageBlockEditor.tsx", "utf8");
  assert.match(composer, /上移/);
  assert.match(composer, /额外图片/);
});
