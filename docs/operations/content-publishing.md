# 产品内容发布流程

## 状态规则

- `draft`：草稿，只在后台可见。签约中或资料不完整的产品必须使用该状态。
- `review`：待审核，仍不在小程序公开。
- `published`：已发布，会进入小程序公开接口。
- `archived`：已下架，保留历史内容但不再公开。

## 批量导入草稿

按照 `content/schema/product.schema.json` 整理 JSON 文件，然后运行：

```bash
cd backend
.venv/bin/python manage.py import_products ../content/examples/antarctica-demo.json --status=draft
```

同一个 `slug` 再次导入会更新原产品及其团期、行程和图片，不会产生重复产品。导入器会先验证整份文件；任何字段错误都会取消本次全部写入。

## 发布前人工检查

1. 确认产品已经完成签约并获得公开发布授权。
2. 检查图片来源和使用授权。
3. 检查标题、简介、团期、每日行程、包含/不含、适合人群和重要提醒。
4. 确认不展示数值价格，不出现购买、支付、定金、合同入口。
5. 在后台选择产品并执行“发布所选产品”，在确认页再次核对后发布。

`content/examples/antarctica-demo.json` 仅用于开发验证，其中带有“演示内容”标记，不得发布。
