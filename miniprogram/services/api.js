function buildQuery(filters = {}) {
  return Object.entries(filters)
    .filter(([, value]) => value !== "" && value !== null && value !== undefined)
    .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(value)}`)
    .join("&");
}

function apiError(code, message) {
  const error = new Error(message);
  error.code = code;
  return error;
}

function wxRequest(options) {
  return new Promise((resolve, reject) => {
    wx.request({
      ...options,
      timeout: 10000,
      success: resolve,
      fail: reject,
    });
  });
}

function createApiClient({baseUrl, request = wxRequest}) {
  async function send(path, options = {}) {
    let response;
    try {
      response = await request({
        url: `${baseUrl}${path}`,
        method: options.method || "GET",
        data: options.data,
        header: {Accept: "application/json", ...(options.header || {})},
      });
    } catch (cause) {
      throw apiError("network_error", "网络暂时不可用，请稍后重试");
    }

    if (response.statusCode < 200 || response.statusCode >= 300) {
      const backendError = response.data && response.data.error;
      throw apiError(
        (backendError && backendError.code) || "request_failed",
        (backendError && backendError.message) || "服务暂时不可用，请稍后重试",
      );
    }
    return response.data;
  }

  return {
    request: send,
    getSite: () => send("/site"),
    getHome: () => send("/home"),
    getProducts(filters = {}) {
      const query = buildQuery(filters);
      return send(`/products${query ? `?${query}` : ""}`);
    },
    getProduct: (slug) => send(`/products/${encodeURIComponent(slug)}`),
    getVessels: () => send("/vessels"),
    getVessel: (slug) => send(`/vessels/${encodeURIComponent(slug)}`),
  };
}

function currentClient() {
  const app = getApp();
  return createApiClient({baseUrl: app.globalData.apiBaseUrl});
}

module.exports = {
  buildQuery,
  createApiClient,
  getSite: () => currentClient().getSite(),
  getHome: () => currentClient().getHome(),
  getProducts: (filters) => currentClient().getProducts(filters),
  getProduct: (slug) => currentClient().getProduct(slug),
  getVessels: () => currentClient().getVessels(),
  getVessel: (slug) => currentClient().getVessel(slug),
};
