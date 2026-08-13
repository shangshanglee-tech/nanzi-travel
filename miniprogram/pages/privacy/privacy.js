const {getSite} = require("../../services/api");
const {loadDocument} = require("../../utils/document");

Page({
  data: {content: "", loading: true},
  async onLoad() {
    const content = await loadDocument(
      getSite,
      "privacy_text",
      "首版小程序不要求登录，不收集手机号，也不创建咨询表单。",
    );
    this.setData({content, loading: false});
  },
});
