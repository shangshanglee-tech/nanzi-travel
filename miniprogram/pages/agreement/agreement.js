const {getSite} = require("../../services/api");
const {loadDocument} = require("../../utils/document");

Page({
  data: {content: "", loading: true},
  async onLoad() {
    const content = await loadDocument(
      getSite,
      "agreement_text",
      "小程序展示的旅行信息用于咨询参考，具体服务内容以双方最终确认文件为准。",
    );
    this.setData({content, loading: false});
  },
});
