const {getSite} = require("../../services/api");
const {loadDocument} = require("../../utils/document");

Page({
  data: {content: "", loading: true},
  async onLoad() {
    const content = await loadDocument(
      getSite,
      "about_us",
      "小楠子爱旅行，专注值得出发的旅行体验。",
    );
    this.setData({content, loading: false});
  },
});
