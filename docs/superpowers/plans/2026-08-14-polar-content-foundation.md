# 极地产品内容底座 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 HX 11 条南极路线升级为可维护的中文路线、船只、舱位、执行船团期和逐日行程内容，并在小程序中实现路线/船只互相跳转和带上下文的客服咨询。

**Architecture:** Django 将路线、船只、舱位、团期与首页编排作为并列对象和关系管理；路线与船只多对多，团期明确关联执行船，舱位属于船。导入程序读取已授权 HX 官方资料，写入可复核的中文内容和来源字段。微信原生小程序读取扩展 API，展示卡片并通过客服会话按钮透传当前选择。

**Tech Stack:** Python 3.12、Django 5.2、Django REST Framework、SQLite、微信原生小程序、WXSS/WXML/JavaScript。

## Global Constraints

- 船只与路线是并列内容对象，通过多对多关系互相导流；首页/专题集合只编排内容，不拥有路线或船只。
- 只使用已授权 HX 官方资料；每条中文内容保留来源链接、抓取时间与复核状态。
- 中文采用顾问式改写，不编造精确登陆点、每日活动、价格、库存、合同或可售承诺。
- 官方区间行程必须拆成逐日记录，保留 `source_range`；区间内每日复用同一说明并注明弹性探险安排。
- 舱位只提供静态介绍，不实现价格、库存、在线预订、订单、支付或合同。
- 咨询使用小程序客服会话，透传当前路线、日期、执行船与舱位；公众号不承担该上下文会话。

---

## 文件结构

- `backend/catalog/models.py`：新增船只、舱位、首页编排和关系字段。
- `backend/catalog/migrations/0003_polar_content_foundation.py`：数据表与关系迁移。
- `backend/catalog/serializers.py`：船只、舱位、团期执行船、路线关联船和首页卡片序列化。
- `backend/catalog/views.py`、`backend/catalog/urls.py`：公开船只列表/详情接口与扩展首页接口。
- `backend/catalog/management/commands/import_hx_polar_content.py`：导入结构化 HX 中文内容、封面和团期执行船。
- `content/imports/hx-polar-content.json`：首批 3 艘船、舱位和 11 条路线的已复核内容源。
- `backend/catalog/tests/test_polar_content.py`：模型、导入、API 和公开状态测试。
- `miniprogram/pages/vessel-detail/*`：船只详情页。
- `miniprogram/pages/product-detail/*`：路线详情的船卡、团期选择与客服上下文。
- `miniprogram/pages/contact/*`：客服会话入口和会话卡片信息。
- `miniprogram/pages/home/*`、`miniprogram/app.json`、`miniprogram/services/api.js`：首页船只卡与新 API。

### Task 1: 建立并验证并列内容模型

**Files:**
- Modify: `backend/catalog/models.py`
- Create: `backend/catalog/migrations/0003_polar_content_foundation.py`
- Modify: `backend/catalog/tests/test_models.py`

**Interfaces:**
- Produces: `Vessel`, `CabinType`, `EditorialCollection`, `EditorialEntry`；`Product.vessels`；`Departure.vessel`；`ItineraryDay.source_range`。

- [ ] **Step 1: 写失败测试**

```python
def test_route_and_vessel_are_peer_objects_linked_many_to_many(self):
    vessel = Vessel.objects.create(slug="roald-amundsen", name="阿蒙森号")
    product = Product.objects.create(title="南极半岛精华", slug="highlights", destination=self.destination)
    product.vessels.add(vessel)
    departure = Departure.objects.create(product=product, vessel=vessel, start_date="2026-12-09")
    self.assertEqual(list(vessel.products.all()), [product])
    self.assertEqual(departure.vessel, vessel)
```

- [ ] **Step 2: 验证失败**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_models -v 2`

Expected: FAIL，提示 `Vessel` 尚不存在。

- [ ] **Step 3: 实现最小模型**

`Vessel` 包含 `slug/name/official_name/summary/hero_image/capacity/year_built/features/source_url/source_fetched_at/review_status/sort_order`；`CabinType` 关联 `Vessel` 并包含 `name/category/size_sqm/bed_layout/view_type/summary/highlights/image/source_url/sort_order`；`EditorialCollection` 与 `EditorialEntry` 可按顺序关联 `Product` 或 `Vessel`，但 entry 必须恰好指向其中之一。

- [ ] **Step 4: 迁移并验证通过**

Run: `cd backend && .venv/bin/python manage.py makemigrations --check && .venv/bin/python manage.py test catalog.tests.test_models -v 2`

Expected: PASS，迁移文件受版本控制且 `EditorialEntry.clean()` 拒绝同时为空或同时关联两种内容。

- [ ] **Step 5: 提交**

```bash
git add backend/catalog/models.py backend/catalog/migrations/0003_polar_content_foundation.py backend/catalog/tests/test_models.py
git commit -m "feat: model polar routes vessels and cabins"
```

### Task 2: 提供公开内容 API

**Files:**
- Modify: `backend/catalog/serializers.py`
- Modify: `backend/catalog/views.py`
- Modify: `backend/catalog/urls.py`
- Modify: `backend/catalog/tests/test_api.py`

**Interfaces:**
- Produces: `GET /api/v1/vessels`、`GET /api/v1/vessels/<slug>`；产品详情返回 `vessels`、团期返回 `vessel`、行程返回 `source_range`；首页返回 `featured_vessels` 与 `featured_entries`。

- [ ] **Step 1: 写失败 API 测试**

```python
def test_product_detail_exposes_possible_vessels_and_selected_departure_vessel(self):
    response = self.client.get("/api/v1/products/highlights")
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json()["vessels"][0]["slug"], "roald-amundsen")
    self.assertEqual(response.json()["departures"][0]["vessel"]["slug"], "roald-amundsen")
```

- [ ] **Step 2: 验证失败**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_api -v 2`

Expected: FAIL，因为产品详情没有 `vessels` 与团期 `vessel` 字段。

- [ ] **Step 3: 实现序列化器与视图**

船只列表只返回公开卡片字段；船只详情返回舱位和关联路线。所有公开视图只返回已发布路线、已启用船只及其可见关联；继续使用 `public, max-age=60` 缓存策略和既有稳定错误格式。

- [ ] **Step 4: 验证通过**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_api -v 2`

Expected: PASS，草稿路线、未启用船只和缺少执行船的团期不泄露不存在的公开对象。

- [ ] **Step 5: 提交**

```bash
git add backend/catalog/serializers.py backend/catalog/views.py backend/catalog/urls.py backend/catalog/tests/test_api.py
git commit -m "feat: expose polar vessels and departures APIs"
```

### Task 3: 整理官方资料并导入中文内容

**Files:**
- Create: `content/imports/hx-polar-content.json`
- Create: `content/imports/hx-vessels/<slug>/hero.webp`
- Create: `backend/catalog/management/commands/import_hx_polar_content.py`
- Create: `backend/catalog/tests/test_polar_content.py`

**Interfaces:**
- Consumes: 已授权 HX 路线、船只、舱位与团期官方资料。
- Produces: `python manage.py import_hx_polar_content SOURCE --status published`；导入 3 艘船、对应静态舱位、11 条中文路线、逐日行程和团期执行船。

- [ ] **Step 1: 写失败导入测试**

```python
def test_import_creates_daily_rows_from_source_ranges_and_links_departures_to_vessels(self):
    call_command("import_hx_polar_content", SOURCE, status="published")
    product = Product.objects.get(slug="highlights-of-antarctica")
    self.assertEqual(product.itinerary_days.filter(source_range="Day 3-4").count(), 2)
    self.assertEqual(product.departures.get(start_date="2026-12-09").vessel.slug, "roald-amundsen")
    self.assertEqual(Vessel.objects.count(), 3)
```

- [ ] **Step 2: 验证失败**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_polar_content -v 2`

Expected: FAIL，提示未知命令或缺少导入对象。

- [ ] **Step 3: 形成首批内容源并实现导入**

内容源为每条路线提供中文概览、中文亮点、逐日中文文案、来源 URL 和复核状态；为每个团期提供 `start_date/end_date/vessel_slug`；为每艘船提供中文档案和静态舱型资料。导入按 slug 更新，复制本地媒体，清理并重建受此导入控制的关联记录；区间 `Day 5-9` 生成 day_number 5 至 9 的五条记录，均保留 `source_range="Day 5-9"`。

- [ ] **Step 4: 验证通过**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_polar_content catalog.tests.test_api -v 2 && .venv/bin/python manage.py check`

Expected: PASS，11 条路线、3 艘船、全部团期执行船和逐日行程可重复导入。

- [ ] **Step 5: 提交**

```bash
git add content/imports backend/catalog/management/commands/import_hx_polar_content.py backend/catalog/tests/test_polar_content.py
git commit -m "feat: import reviewed Chinese polar content"
```

### Task 4: 实现路线与船只的双向浏览

**Files:**
- Create: `miniprogram/pages/vessel-detail/vessel-detail.js`
- Create: `miniprogram/pages/vessel-detail/vessel-detail.wxml`
- Create: `miniprogram/pages/vessel-detail/vessel-detail.wxss`
- Create: `miniprogram/pages/vessel-detail/vessel-detail.json`
- Modify: `miniprogram/app.json`
- Modify: `miniprogram/services/api.js`
- Modify: `miniprogram/pages/home/home.js`
- Modify: `miniprogram/pages/home/home.wxml`
- Modify: `miniprogram/pages/home/home.wxss`
- Modify: `miniprogram/pages/product-detail/product-detail.js`
- Modify: `miniprogram/pages/product-detail/product-detail.wxml`
- Modify: `miniprogram/pages/product-detail/product-detail.wxss`
- Test: `miniprogram/tests/product-detail.test.js`

**Interfaces:**
- Consumes: Task 2 的 `getVessels()`、`getVessel(slug)` 和扩展产品详情字段。
- Produces: 首页船只卡；路线页的可能执行船与选中团期执行船卡；船页的舱位和关联路线卡。

- [ ] **Step 1: 写失败页面行为测试**

```javascript
test("selecting a departure exposes its execution vessel", () => {
  const state = selectDeparture(productWithTwoVessels, "2026-12-09");
  expect(state.selectedDeparture.vessel.slug).toBe("roald-amundsen");
});
```

- [ ] **Step 2: 验证失败**

Run: `npm test -- miniprogram/tests/product-detail.test.js`

Expected: FAIL，因为 `selectDeparture` 尚不存在。

- [ ] **Step 3: 实现最小页面交互**

路线页将团期渲染为可选择项；选择后显示对应船卡。路线页和船页的卡片使用 `wx.navigateTo` 跳转，而不是把船或路线视为层级。首页将 API 的船只卡与路线卡分别展示；舱位只显示静态资料与“咨询此舱位”入口。

- [ ] **Step 4: 验证通过**

Run: `npm test -- miniprogram/tests/product-detail.test.js && npm test`

Expected: PASS；微信开发者工具真机预览中能完成“首页船卡 → 船页 → 路线页”和“路线页 → 选择日期 → 执行船卡 → 船页”。

- [ ] **Step 5: 提交**

```bash
git add miniprogram
git commit -m "feat: browse polar vessels routes and departures"
```

### Task 5: 接入带上下文的小程序客服咨询

**Files:**
- Create: `miniprogram/utils/consultation.js`
- Create: `miniprogram/tests/consultation.test.js`
- Modify: `miniprogram/pages/contact/contact.js`
- Modify: `miniprogram/pages/contact/contact.wxml`
- Modify: `miniprogram/pages/contact/contact.wxss`
- Modify: `miniprogram/pages/product-detail/product-detail.js`
- Modify: `miniprogram/pages/vessel-detail/vessel-detail.js`

**Interfaces:**
- Produces: `buildConsultationContext({product, departure, vessel, cabin})`，返回 `{sessionFrom, title, path, image}`；客服按钮使用 `open-type="contact"`、`session-from` 和会话内页面卡片属性。

- [ ] **Step 1: 写失败上下文测试**

```javascript
test("builds consultation context from a selected route departure and vessel", () => {
  const result = buildConsultationContext({product, departure, vessel, cabin: null});
  expect(result.sessionFrom).toContain("2026-12-09");
  expect(result.sessionFrom).toContain("MS Roald Amundsen");
  expect(result.title).toBe("咨询：12天南极半岛精华");
});
```

- [ ] **Step 2: 验证失败**

Run: `npm test -- miniprogram/tests/consultation.test.js`

Expected: FAIL，因为 `buildConsultationContext` 尚不存在。

- [ ] **Step 3: 实现上下文与客服按钮**

`sessionFrom` 使用 JSON 文本，字段固定为 `source/product_slug/product_title/departure_date/vessel_slug/vessel_name/cabin_name`；未选择字段写空字符串。联系页显示当前选择摘要，并以 `button open-type="contact"` 打开客服会话；会话卡片标题为“咨询：<路线或船只名称>”，路径为当前详情页，图片为路线或船的封面。

- [ ] **Step 4: 验证通过**

Run: `npm test -- miniprogram/tests/consultation.test.js && npm test`

Expected: PASS；开发者工具中点击咨询会打开小程序客服会话，客服会话来源包含所选日期、执行船和舱位（如有）。

- [ ] **Step 5: 提交与部署验收**

```bash
git add miniprogram
git commit -m "feat: carry travel context into customer service"
```

部署后重新导入内容，验证 `https://api.nanzitravel.com/api/v1/home`、路线详情、船只详情和产品封面；上传新的体验版，但不提交审核。

## 自查

- 数据模型将船只、路线、专题集合设为并列对象，符合首页自由编排要求。
- 团期已具备明确执行船；舱位只归属船只，不含实时交易字段。
- 区间行程逐日拆分并保留来源区间，未伪造细节。
- 路线、船和咨询入口均有中文内容、公开 API、页面与自动化测试覆盖。
- 不包含支付、库存、订单、合同、用户 AI、真实搭子或多顾问 CRM。
