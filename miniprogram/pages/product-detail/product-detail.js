const {getProduct} = require("../../services/api");
const {formatDuration} = require("../../utils/format");

Page({
  data: {loading: true, error: "", product: {}, durationLabel: "", selectedDeparture: null},
  onLoad(query) {
    this.slug = query.slug || "";
    this.loadProduct();
  },
  async loadProduct() {
    this.setData({loading: true, error: ""});
    try {
      const product = await getProduct(this.slug);
      this.setData({product, durationLabel: formatDuration(product.duration_days), selectedDeparture: null});
      wx.setNavigationBarTitle({title: product.title});
    } catch (error) {
      this.setData({error: error.message || "加载失败，请稍后重试"});
    } finally {
      this.setData({loading: false});
    }
  },
  consult() {
    const departure = this.data.selectedDeparture;
    const query = [
      `product=${encodeURIComponent(this.data.product.title)}`,
      departure && departure.start_date ? `departure=${encodeURIComponent(departure.start_date)}` : "",
      departure && departure.vessel ? `vessel=${encodeURIComponent(departure.vessel.name)}` : "",
    ].filter(Boolean).join("&");
    wx.navigateTo({
      url: `/pages/contact/contact?${query}`,
    });
  },
  selectDeparture(event) {
    const departure = this.data.product.departures[event.currentTarget.dataset.index];
    this.setData({selectedDeparture: departure});
  },
  openVessel(event) {
    wx.navigateTo({url: `/pages/vessel-detail/vessel-detail?slug=${event.currentTarget.dataset.slug}`});
  },
});
