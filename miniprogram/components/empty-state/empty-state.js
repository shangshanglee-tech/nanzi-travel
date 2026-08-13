Component({
  properties: {
    title: {type: String, value: "暂时没有内容"},
    description: {type: String, value: "可以稍后再来看看"},
    actionText: {type: String, value: "重新加载"},
    showAction: {type: Boolean, value: true},
  },
  methods: {
    handleAction() {
      this.triggerEvent("retry");
    },
  },
});

