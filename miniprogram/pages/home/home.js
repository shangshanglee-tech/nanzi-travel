const {getHome} = require("../../services/api");
const {getHomeTopPadding} = require("./layout");

Page({
  data: {loading: true, error: "", products: [], vessels: [], destinations: [], topPadding: 38},
  onLoad() {
    const system = wx.getSystemInfoSync();
    this.setData({topPadding: getHomeTopPadding(system.statusBarHeight || 0)});
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
        vessels: (data.featured_vessels || []).filter((vessel) => vessel.card_image),
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
  openProduct(event) {
    wx.navigateTo({url: `/pages/product-detail/product-detail?slug=${event.currentTarget.dataset.slug}`});
  },
  openVessel(event) {
    wx.navigateTo({url: `/pages/vessel-detail/vessel-detail?slug=${event.currentTarget.dataset.slug}`});
  },
});
