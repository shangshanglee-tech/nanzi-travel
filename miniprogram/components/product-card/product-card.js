Component({
  properties: {product: {type: Object, value: {}}},
  methods: {
    openProduct() {
      this.triggerEvent("open", {slug: this.data.product.slug});
    },
  },
});
