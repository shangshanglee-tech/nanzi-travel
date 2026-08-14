const {getVessel} = require("../../services/api");

Page({
  data: {loading: true, error: "", vessel: {}},
  onLoad(query) {
    this.slug = query.slug || "";
    this.loadVessel();
  },
  async loadVessel() {
    this.setData({loading: true, error: ""});
    try {
      const vessel = await getVessel(this.slug);
      this.setData({vessel});
      wx.setNavigationBarTitle({title: vessel.name});
    } catch (error) {
      this.setData({error: error.message || "加载失败，请稍后重试"});
    } finally {
      this.setData({loading: false});
    }
  },
  openProduct(event) {
    wx.navigateTo({url: `/pages/product-detail/product-detail?slug=${event.currentTarget.dataset.slug}`});
  },
  consult() {
    wx.navigateTo({url: `/pages/contact/contact?vessel=${encodeURIComponent(this.data.vessel.name || "")}`});
  },
});
