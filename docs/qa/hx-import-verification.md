# HX 南极产品导入验收记录

- 内容来源：已授权的 HX 南极线路资料
- 导入范围：11 条产品、11 张本地受管封面图
- 导入状态：已发布（`published`）
- 价格与库存：未导入，前端统一引导人工咨询

## 自动验收

执行命令：

```bash
cd backend
.venv/bin/python manage.py test catalog.tests.test_import_hx_antarctica catalog.tests.test_import_products catalog.tests.test_api -v 1
.venv/bin/python manage.py check
.venv/bin/python manage.py import_hx_antarctica ../content/imports/hx-antarctica.json --status published
```

结果：通过。重复导入按 `slug` 更新，数据库仍为 11 条产品；公开列表和“12天南极半岛精华”详情均返回团期信息。

## 生产环境人工抽查清单

- [ ] 首页展示已发布产品，不展示草稿。
- [ ] 产品列表显示 11 条南极线路。
- [ ] 分别打开 12 天、16 天和 23 天产品详情，确认封面、亮点、行程段和团期可见。
- [ ] 团期只显示咨询提示，不显示价格、库存、付款或合同入口。
- [ ] “咨询该行程”显示公众号人工咨询引导。
