const {getProduct} = require("../../services/api");
const {formatDuration} = require("../../utils/format");

Page({
  data: {loading: true, error: "", product: {}, durationLabel: ""},
  onLoad(query) {
    this.slug = query.slug || "";
    this.loadProduct();
  },
  async loadProduct() {
    this.setData({loading: true, error: ""});
    try {
      const product = await getProduct(this.slug);
      this.setData({product, durationLabel: formatDuration(product.duration_days)});
      wx.setNavigationBarTitle({title: product.title});
    } catch (error) {
      this.setData({error: error.message || "加载失败，请稍后重试"});
    } finally {
      this.setData({loading: false});
    }
  },
  consult() {
    wx.navigateTo({
      url: `/pages/contact/contact?product=${encodeURIComponent(this.data.product.title)}`,
    });
  },
});
