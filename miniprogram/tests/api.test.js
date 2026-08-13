const test = require("node:test");
const assert = require("node:assert/strict");

const { buildQuery, createApiClient } = require("../services/api");


test("buildQuery omits empty filters and encodes Chinese values", () => {
  assert.equal(
    buildQuery({ destination: "antarctica", month: "", tag: "首次去南极" }),
    "destination=antarctica&tag=%E9%A6%96%E6%AC%A1%E5%8E%BB%E5%8D%97%E6%9E%81",
  );
});

test("API client normalizes network failures", async () => {
  const client = createApiClient({
    baseUrl: "https://api.example.test/api/v1",
    request() {
      return Promise.reject(new Error("offline"));
    },
  });

  await assert.rejects(
    client.getHome(),
    (error) =>
      error.code === "network_error" &&
      error.message === "网络暂时不可用，请稍后重试",
  );
});

test("API client preserves backend error codes and messages", async () => {
  const client = createApiClient({
    baseUrl: "https://api.example.test/api/v1",
    request() {
      return Promise.resolve({
        statusCode: 404,
        data: {error: {code: "not_found", message: "产品不存在或尚未发布"}},
      });
    },
  });

  await assert.rejects(
    client.getProduct("missing"),
    (error) => error.code === "not_found" && error.message === "产品不存在或尚未发布",
  );
});
