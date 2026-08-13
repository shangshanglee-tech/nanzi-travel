const {getSite} = require("../../services/api");

Page({
  data: {loading: true, error: "", site: {}},
  onLoad() {
    this.loadSite();
  },
  async loadSite() {
    this.setData({loading: true, error: ""});
    try {
      this.setData({site: await getSite()});
    } catch (error) {
      this.setData({error: error.message || "加载失败，请稍后重试"});
    } finally {
      this.setData({loading: false});
    }
  },
});

