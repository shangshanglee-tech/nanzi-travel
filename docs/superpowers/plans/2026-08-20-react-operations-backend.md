# React 运营后台 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 以 React + Ant Design 替代 Django Admin，日常只管理旅行产品、目的地和船只。

**Architecture:** Django 保留模型、媒体存储、会话登录和管理 API。React 应用由 Vite 构建后在 `admin.nanzitravel.com` 同域托管，调用 `/api/admin/v1/`；现有 `/api/v1/` 保持不变。

**Tech Stack:** Django 5、Django REST Framework、React 19、TypeScript、Vite、Ant Design、Nginx、GitHub Actions。

**Spec:** `docs/superpowers/specs/2026-08-20-react-operations-backend-design.md`

## Global Constraints

- 公开 `/api/v1/` 的路径和响应保持兼容。
- 管理 API 均在 `/api/admin/v1/`，要求超级管理员会话。
- 初始账号名为 `admin`；密码只由服务器环境变量 `OPERATIONS_ADMIN_PASSWORD` 提供，不进入 Git。
- React 导航仅有旅行产品、目的地、船只。
- 三类内容完整迁移并经过线上数据验证前，不删除 Django Admin。
- `project.config.json` 和 `backend/uv.lock` 不提交。

---

## File Structure

- `operations-console/`：Vite + React + Ant Design 应用与前端测试。
- `backend/catalog/operations_serializers.py`：管理 API 专用序列化与嵌套写入校验。
- `backend/catalog/operations_views.py`：登录、资源 CRUD、图片上传接口。
- `backend/catalog/operations_urls.py`：`/api/admin/v1/` 路由。
- `backend/templates/operations/index.html`：带 CSRF token 的单页应用外壳。
- `backend/catalog/tests/test_operations_*.py`：管理 API 与公开 API 兼容性测试。
- `.github/workflows/release.yml`：构建 React bundle 后再打包发布。

### Task 1: 认证、CSRF 与单页应用入口

**Files:**
- Create: `backend/catalog/operations_views.py`
- Create: `backend/catalog/operations_urls.py`
- Create: `backend/templates/operations/index.html`
- Create: `backend/catalog/management/commands/ensure_operations_admin.py`
- Create: `backend/catalog/tests/test_operations_auth.py`
- Modify: `backend/catalog/views.py`
- Modify: `backend/config/urls.py`

**Produces:** `GET /` 管理端外壳；`GET /api/admin/v1/auth/csrf`；`POST /api/admin/v1/auth/login`、`logout`；`GET /api/admin/v1/auth/me`。

- [ ] **Step 1: Write the failing test**

```python
def test_superuser_login_creates_management_session(self):
    User.objects.create_superuser("admin", password="admin123456")
    response = self.client.post("/api/admin/v1/auth/login", data={"username": "admin", "password": "admin123456"}, content_type="application/json")
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json()["username"], "admin")
```

- [ ] **Step 2: Run RED verification**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_operations_auth -v 2`

Expected: route-not-found failure.

- [ ] **Step 3: Implement the minimum API**

```python
user = authenticate(request, **request.data)
if not user or not user.is_superuser:
    return Response({"detail": "账号或密码错误"}, status=400)
login(request, user)
return Response({"username": user.get_username()})
```

Use `IsAdminUser` for non-auth endpoints; expose the result of `get_token(request)` to React via the HTML `<meta name="csrf-token">`; the bootstrap command must fail if `OPERATIONS_ADMIN_PASSWORD` is absent.

- [ ] **Step 4: Run GREEN verification and commit**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_operations_auth -v 2`

```bash
git add backend/catalog/operations_views.py backend/catalog/operations_urls.py backend/templates/operations/index.html backend/catalog/management/commands/ensure_operations_admin.py backend/catalog/tests/test_operations_auth.py backend/catalog/views.py backend/config/urls.py
git commit -m "feat: add operations console authentication"
```

### Task 2: React + Ant Design shell and release bundle

**Files:**
- Create: `operations-console/package.json`
- Create: `operations-console/vite.config.ts`
- Create: `operations-console/src/main.tsx`
- Create: `operations-console/src/App.tsx`
- Create: `operations-console/src/api/client.ts`
- Create: `operations-console/src/layout/OperationsLayout.tsx`
- Create: `operations-console/src/features/auth/LoginPage.tsx`
- Create: `operations-console/tests/app-shell.test.mjs`
- Modify: `backend/templates/operations/index.html`
- Modify: `.github/workflows/release.yml`
- Modify: `deploy/nginx/nanzi-travel.conf`
- Modify: `deploy/scripts/deploy.sh`
- Modify: `deploy/tests/test_deploy_files.sh`

**Produces:** Vite output under `backend/catalog/static/catalog/operations/`; React routes `/login`、`/products`、`/destinations`、`/vessels`。

- [ ] **Step 1: Write the failing test**

```javascript
test("navigation contains only three content entries", async () => {
  const source = await readFile("src/layout/OperationsLayout.tsx", "utf8");
  for (const label of ["旅行产品", "目的地", "船只"]) assert.match(source, new RegExp(label));
  assert.doesNotMatch(source, /站点设置/);
});
```

- [ ] **Step 2: Run RED verification**

Run: `cd operations-console && node --test tests/app-shell.test.mjs`

Expected: missing-file failure.

- [ ] **Step 3: Implement shell and deployment**

```tsx
const menuItems = [
  { key: "/products", label: <Link to="/products">旅行产品</Link> },
  { key: "/destinations", label: <Link to="/destinations">目的地</Link> },
  { key: "/vessels", label: <Link to="/vessels">船只</Link> },
];
```

Vite builds to `backend/catalog/static/catalog/operations/`. Release CI installs Node 22 dependencies and runs the build before creating the archive. Nginx proxies the root only on `admin.nanzitravel.com`; `api.nanzitravel.com` root remains 404.

- [ ] **Step 4: Run GREEN verification and commit**

Run: `cd operations-console && npm ci && npm run build && node --test tests/app-shell.test.mjs`

```bash
git add operations-console backend/templates/operations/index.html .github/workflows/release.yml deploy/nginx/nanzi-travel.conf deploy/scripts/deploy.sh deploy/tests/test_deploy_files.sh
git commit -m "feat: add ant design operations console shell"
```

### Task 3: Destination resource

**Files:**
- Create: `backend/catalog/operations_serializers.py`
- Create: `backend/catalog/tests/test_operations_destinations.py`
- Modify: `backend/catalog/operations_views.py`
- Modify: `backend/catalog/operations_urls.py`
- Create: `operations-console/src/api/destinations.ts`
- Create: `operations-console/src/features/destinations/DestinationListPage.tsx`
- Create: `operations-console/src/features/destinations/DestinationFormModal.tsx`
- Create: `operations-console/tests/destinations.test.mjs`
- Modify: `operations-console/src/App.tsx`

**Produces:** `GET/POST /api/admin/v1/destinations` and `PATCH/DELETE /api/admin/v1/destinations/<id>` for `name`、`slug`、`is_active`、`sort_order`。

- [ ] **Step 1: Write the failing test**

```python
def test_admin_can_create_destination(self):
    self.login_admin()
    response = self.client.post("/api/admin/v1/destinations", data={"name": "北极", "slug": "arctic", "is_active": True, "sort_order": 10}, content_type="application/json")
    self.assertEqual(response.status_code, 201)
```

- [ ] **Step 2: Run RED verification**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_operations_destinations -v 2`

Expected: route-not-found failure.

- [ ] **Step 3: Implement API and Ant Design table/modal**

Use a `ModelSerializer` for uniqueness validation. Use `Table`, `Modal`, `Form`, `Switch`, `InputNumber`, `Popconfirm` and refetch only after successful mutation.

- [ ] **Step 4: Run GREEN verification and commit**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_operations_destinations -v 2 && cd ../operations-console && node --test tests/destinations.test.mjs`

```bash
git add backend/catalog/operations_serializers.py backend/catalog/operations_views.py backend/catalog/operations_urls.py backend/catalog/tests/test_operations_destinations.py operations-console/src/api/destinations.ts operations-console/src/features/destinations operations-console/tests/destinations.test.mjs operations-console/src/App.tsx
git commit -m "feat: manage destinations in operations console"
```

### Task 4: Travel product resource

**Files:**
- Create: `backend/catalog/tests/test_operations_products.py`
- Modify: `backend/catalog/operations_serializers.py`
- Modify: `backend/catalog/operations_views.py`
- Modify: `backend/catalog/operations_urls.py`
- Create: `operations-console/src/api/products.ts`
- Create: `operations-console/src/features/products/ProductListPage.tsx`
- Create: `operations-console/src/features/products/ProductEditorPage.tsx`
- Create: `operations-console/src/features/products/ProductDepartureEditor.tsx`
- Create: `operations-console/src/features/products/ItineraryEditor.tsx`
- Create: `operations-console/src/features/products/ProductImageEditor.tsx`
- Create: `operations-console/tests/products.test.mjs`
- Modify: `operations-console/src/App.tsx`

**Produces:** Authenticated product CRUD with destination, associated vessels, publication status, ordered departures, daily itinerary, gallery and hero upload.

- [ ] **Step 1: Write the failing nested-save test**

```python
def test_admin_can_save_product_with_departure_and_daily_itinerary(self):
    self.login_admin()
    response = self.client.post("/api/admin/v1/products", data=json.dumps({"title": "12天南极半岛精华", "slug": "antarctica-12-days", "destination_id": self.destination.id, "status": "draft", "departures": [{"label": "2027年1月", "start_date": "2027-01-03"}], "itinerary_days": [{"day_number": 1, "title": "抵达", "description": "抵达乌斯怀亚"}]}), content_type="application/json")
    self.assertEqual(response.status_code, 201)
```

- [ ] **Step 2: Run RED verification**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_operations_products -v 2`

Expected: route-not-found failure.

- [ ] **Step 3: Implement atomic nested save and sectioned editor**

Write product, departures, itinerary and image ordering inside `transaction.atomic()`. Use React forms with destination/vessel selects, draft/published control, editable departure/day lists, upload previews and delete confirmation.

- [ ] **Step 4: Run GREEN verification and commit**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_operations_products -v 2 && cd ../operations-console && npm run build && node --test tests/products.test.mjs`

```bash
git add backend/catalog/operations_serializers.py backend/catalog/operations_views.py backend/catalog/operations_urls.py backend/catalog/tests/test_operations_products.py operations-console/src/api/products.ts operations-console/src/features/products operations-console/tests/products.test.mjs operations-console/src/App.tsx
git commit -m "feat: manage products in operations console"
```

### Task 5: Vessel resource

**Files:**
- Create: `backend/catalog/tests/test_operations_vessels.py`
- Modify: `backend/catalog/operations_serializers.py`
- Modify: `backend/catalog/operations_views.py`
- Modify: `backend/catalog/operations_urls.py`
- Create: `operations-console/src/api/vessels.ts`
- Create: `operations-console/src/features/vessels/VesselListPage.tsx`
- Create: `operations-console/src/features/vessels/VesselEditorPage.tsx`
- Create: `operations-console/src/features/vessels/VesselFactsForm.tsx`
- Create: `operations-console/src/features/vessels/PageBlockEditor.tsx`
- Create: `operations-console/src/features/vessels/CabinEditor.tsx`
- Create: `operations-console/src/features/vessels/DeckPlanEditor.tsx`
- Create: `operations-console/tests/vessels.test.mjs`
- Modify: `operations-console/src/App.tsx`

**Produces:** Vessel CRUD preserving card visual, structured facts, ordered page blocks/multiple images, cabins, cabin groups and deck plans.

- [ ] **Step 1: Write the failing nested-vessel test**

```python
def test_admin_can_save_vessel_page_blocks(self):
    self.login_admin()
    response = self.client.patch(f"/api/admin/v1/vessels/{self.vessel.pk}", data=json.dumps({"name": "阿蒙森号", "page_blocks": [{"block_type": "heading", "title": "探索与学习"}]}), content_type="application/json")
    self.assertEqual(response.status_code, 200)
```

- [ ] **Step 2: Run RED verification**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_operations_vessels -v 2`

Expected: route-not-found failure.

- [ ] **Step 3: Implement transaction-safe vessel tabs**

Use Ant Design `Tabs`: 基础信息、首页卡片、结构化事实、页面内容、舱位、甲板图. Assign `sort_order` from list order on every save. Use multipart image upload endpoints; each delete is a `Popconfirm` and only persists on Save.

- [ ] **Step 4: Run GREEN verification and commit**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_operations_vessels -v 2 && cd ../operations-console && npm run build && node --test tests/vessels.test.mjs`

```bash
git add backend/catalog/operations_serializers.py backend/catalog/operations_views.py backend/catalog/operations_urls.py backend/catalog/tests/test_operations_vessels.py operations-console/src/api/vessels.ts operations-console/src/features/vessels operations-console/tests/vessels.test.mjs operations-console/src/App.tsx
git commit -m "feat: manage vessels in operations console"
```

### Task 6: Production acceptance and Django Admin removal

**Files:**
- Modify: `backend/config/urls.py`
- Modify: `backend/catalog/admin.py`
- Delete: `backend/templates/admin/index.html`
- Delete: `backend/templates/admin/base_site.html`
- Delete: `backend/catalog/templates/admin/base_site.html`
- Delete: `backend/catalog/templates/admin/catalog/vessel/change_form.html`
- Delete: `backend/catalog/templates/admin/catalog/vessel/deck_plans_inline.html`
- Delete: `backend/catalog/templates/admin/catalog/vessel/page_blocks_inline.html`
- Delete: `backend/catalog/static/catalog/admin-operations.css`
- Delete: `backend/catalog/static/catalog/vessel-page-blocks-admin.js`
- Delete: `backend/catalog/static/catalog/deck-plan-upload-admin.js`
- Delete: `backend/catalog/static/catalog/vessel-editor-tabs.js`
- Create: `backend/catalog/tests/test_operations_live_content.py`

- [ ] **Step 1: Write failing retirement tests**

```python
def test_django_admin_is_not_routed_after_cutover(self):
    self.assertEqual(self.client.get("/admin/").status_code, 404)

def test_public_api_stays_available_after_console_cutover(self):
    self.assertEqual(self.client.get("/api/v1/products").status_code, 200)
```

- [ ] **Step 2: Run RED verification**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_operations_live_content -v 2`

Expected: Django Admin still responds, so the first test fails.

- [ ] **Step 3: Manually accept the complete console before removal**

Verify real data through React: all destinations, 11 HX products, and three vessels open and save; all images load in the mini program; product and vessel ordering is preserved. Then remove `path("admin/", admin.site.urls)` and all admin-only code listed above.

- [ ] **Step 4: Run full verification and deploy**

Run: `cd backend && .venv/bin/python manage.py test && python manage.py check && cd ../operations-console && npm ci && npm run build && node --test tests/*.test.mjs && cd ../miniprogram && npm ci --ignore-scripts && node --test tests/*.test.js && cd .. && git diff --check`

```bash
git add backend operations-console .github/workflows/release.yml deploy
git commit -m "feat: retire django admin for operations console"
git push github release
```

## Plan self-review

- Authentication and same-origin CSRF are Task 1; UI/build/release are Task 2; the three approved resources are Tasks 3–5; public compatibility and old-admin deletion are Task 6.
- API namespace, static build directory and identity rule are consistent across tasks.
- No password is embedded in production source or the release repository.
