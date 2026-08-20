import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

test("product editor has dedicated departure and itinerary editors", async () => {
  const source = await readFile("src/features/products/ProductEditorPage.tsx", "utf8");

  assert.match(source, /ProductDepartureEditor/);
  assert.match(source, /ItineraryEditor/);
  assert.match(source, /发布状态/);
});

test("product editor includes a dedicated image manager", async () => {
  const source = await readFile("src/features/products/ProductEditorPage.tsx", "utf8");
  assert.match(source, /ProductImageEditor/);
});
