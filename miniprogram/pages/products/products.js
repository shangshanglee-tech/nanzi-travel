const {getProducts} = require("../../services/api");
const {normalizeFilterOptions, toProductCard} = require("./view-model");

Page({
  data: {
    loading: true,
    error: "",
    products: [],
    options: {destinations: [], months: [], durations: [], tags: []},
    filters: {destination: "", month: "", duration_min: "", duration_max: "", tag: ""},
    selected: {destination: "", month: "", duration: ""},
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
        options: normalizeFilterOptions(response.filters),
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
  chooseDestination(event) {
    const destination = this.data.options.destinations[Number(event.detail.value)];
    this.setData({"filters.destination": destination.slug, "selected.destination": destination.name});
    this.loadProducts();
  },
  chooseMonth(event) {
    const month = this.data.options.months[Number(event.detail.value)];
    this.setData({"filters.month": month.value, "selected.month": month.label});
    this.loadProducts();
  },
  chooseDuration(event) {
    const duration = this.data.options.durations[Number(event.detail.value)];
    this.setData({
      "filters.duration_min": duration.value,
      "filters.duration_max": duration.value,
      "selected.duration": duration.label,
    });
    this.loadProducts();
  },
  clearFilter(event) {
    const field = event.currentTarget.dataset.field;
    if (field === "duration") {
      this.setData({"filters.duration_min": "", "filters.duration_max": "", "selected.duration": ""});
    } else {
      this.setData({[`filters.${field}`]: "", [`selected.${field}`]: ""});
    }
    this.loadProducts();
  },
  clearFilters() {
    this.setData({
      filters: {destination: "", month: "", duration_min: "", duration_max: "", tag: ""},
      selected: {destination: "", month: "", duration: ""},
    });
    this.loadProducts();
  },
  openProduct(event) {
    wx.navigateTo({url: `/pages/product-detail/product-detail?slug=${encodeURIComponent(event.detail.slug)}`});
  },
});
