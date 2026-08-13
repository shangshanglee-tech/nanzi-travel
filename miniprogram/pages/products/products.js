const {getProducts} = require("../../services/api");
const {collectFilterOptions, toProductCard} = require("./view-model");

Page({
  data: {
    loading: true,
    error: "",
    products: [],
    options: {destinations: [], tags: []},
    filters: {destination: "", tag: ""},
  },
  onLoad(query) {
    if (query.destination) this.setData({"filters.destination": query.destination});
    this.loadProducts();
  },
  async loadProducts() {
    this.setData({loading: true, error: ""});
    try {
      const response = await getProducts(this.data.filters);
      const rawProducts = response.results || [];
      this.setData({
        products: rawProducts.map(toProductCard),
        options: collectFilterOptions(rawProducts),
      });
    } catch (error) {
      this.setData({error: error.message || "加载失败，请稍后重试"});
    } finally {
      this.setData({loading: false});
    }
  },
  chooseTag(event) {
    const tag = event.currentTarget.dataset.tag;
    this.setData({"filters.tag": this.data.filters.tag === tag ? "" : tag});
    this.loadProducts();
  },
  clearFilters() {
    this.setData({filters: {destination: "", tag: ""}});
    this.loadProducts();
  },
  openProduct(event) {
    wx.navigateTo({url: `/pages/product-detail/product-detail?slug=${encodeURIComponent(event.detail.slug)}`});
  },
});
