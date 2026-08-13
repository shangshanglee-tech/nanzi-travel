const {getHome} = require("../../services/api");

Page({
  data: {loading: true, error: "", products: [], destinations: []},
  onLoad() {
    this.loadHome();
  },
  onPullDownRefresh() {
    this.loadHome().finally(() => wx.stopPullDownRefresh());
  },
  async loadHome() {
    this.setData({loading: true, error: ""});
    try {
      const data = await getHome();
      this.setData({
        products: data.featured_products || [],
        destinations: data.destinations || [],
      });
    } catch (error) {
      this.setData({error: error.message || "加载失败，请稍后重试"});
    } finally {
      this.setData({loading: false});
    }
  },
  openProducts() {
    wx.navigateTo({url: "/pages/products/products?destination=antarctica"});
  },
});
