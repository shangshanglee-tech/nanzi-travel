const {getSite} = require("../../services/api");
const {buildContactState} = require("./view-model");

Page({
  data: {
    loading: true,
    componentUnavailable: false,
    officialAccountName: "小楠子爱旅行俱乐部",
    officialAccountGuide: "请在微信中搜索公众号名称并关注，获取人工咨询服务。",
    consultationCopy: "我想咨询小楠子的旅行产品",
    sessionFrom: "咨询来源=小楠子爱旅行",
  },
  onLoad(query) {
    this.productTitle = query.product || "";
    this.departure = query.departure || "";
    this.vessel = query.vessel || "";
    this.loadContact();
  },
  async loadContact() {
    try {
      const site = await getSite();
      this.setData(buildContactState(site, this.productTitle, this.departure, this.vessel));
    } catch (error) {
      this.setData(buildContactState({}, this.productTitle, this.departure, this.vessel));
    } finally {
      this.setData({loading: false});
    }
  },
  handleOfficialAccountError() {
    this.setData({componentUnavailable: true});
  },
  copyAccountName() {
    wx.setClipboardData({data: this.data.officialAccountName});
  },
  copyConsultation() {
    wx.setClipboardData({data: this.data.consultationCopy});
  },
});
