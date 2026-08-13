Component({
  properties: {
    title: {type: String, value: "新功能"},
    description: {type: String, value: ""},
    mark: {type: String, value: "✦"},
  },
  methods: {
    showComingSoon() {
      wx.showModal({
        title: this.data.title,
        content: "功能开发中，敬请期待",
        showCancel: false,
        confirmColor: "#143F35",
      });
    },
  },
});
