import assert from "node:assert/strict";
import test from "node:test";
import { readFile } from "node:fs/promises";

test("destination management uses an Ant Design table and editing modal", async () => {
  const source = await readFile("src/features/destinations/DestinationListPage.tsx", "utf8");

  assert.match(source, /Table/);
  assert.match(source, /DestinationFormModal/);
  assert.match(source, /新建目的地/);
});
