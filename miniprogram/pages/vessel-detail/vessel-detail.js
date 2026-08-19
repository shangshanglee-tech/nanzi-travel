const {getVessel} = require("../../services/api");
const {buildVesselDetailState} = require("./view-model");

Page({
  data: {loading: true, error: "", vessel: {}, detail: {}, apiBaseUrl: "", navCollapsed: false, navCollapseOffset: 260, deckPlanIndex: 0, currentDeckTitle: "", currentDeckBody: ""},
  onLoad(query) {
    this.slug = query.slug || "";
    this.setData({apiBaseUrl: getApp().globalData.apiBaseUrl});
    this.loadVessel();
  },
  async loadVessel() {
    this.setData({loading: true, error: ""});
    try {
      const vessel = await getVessel(this.slug);
      const detail = buildVesselDetailState(vessel);
      this.setData({vessel, detail});
      this.setCurrentDeckPlan(0, detail);
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
  setCurrentDeckPlan(index, detail) {
    const plan = (detail || this.data.detail).deckPlans[index] || {};
    this.setData({deckPlanIndex: index, currentDeckTitle: plan.title || "", currentDeckBody: plan.description || ""});
  },
  changeDeckPlan(event) {
    this.setCurrentDeckPlan(event.detail.current);
  },
  onPageScroll(event) {
    const navCollapsed = event.scrollTop >= this.data.navCollapseOffset;
    if (navCollapsed !== this.data.navCollapsed) this.setData({navCollapsed});
  },
});
