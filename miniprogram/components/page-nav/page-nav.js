const {getNavigationMetrics} = require("./metrics");

Component({
  properties: {
    title: {type: String, value: ""},
    showBack: {type: Boolean, value: true},
  },
  data: {
    metrics: {topPadding: 20, height: 44, rightPadding: 16},
  },
  lifetimes: {
    attached() {
      const system = wx.getSystemInfoSync();
      const capsule = wx.getMenuButtonBoundingClientRect();
      this.setData({
        metrics: getNavigationMetrics(capsule, system.statusBarHeight || 0, system.windowWidth || 375),
      });
    },
  },
  methods: {
    goBack() {
      if (getCurrentPages().length > 1) {
        wx.navigateBack();
        return;
      }
      wx.switchTab({url: "/pages/home/home"});
    },
  },
});
