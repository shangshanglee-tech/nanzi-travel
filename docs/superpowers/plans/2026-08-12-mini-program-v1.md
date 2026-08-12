# 小楠子爱旅行小程序首版 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 交付一个可在微信开发者工具运行、可从运营后台发布南极产品、可通过公众号承接人工咨询的“小楠子爱旅行”首版小程序。

**Architecture:** 在现有 Git 仓库中保留 H5 原型作为视觉参考，新增微信原生小程序、Django 5.2 LTS 内容服务和部署配置。Django Admin 承担轻量运营后台，公开 API 只返回已发布产品；本地开发使用文件存储和 SQLite，生产使用阿里云 OSS 和同一台服务器上的 SQLite WAL 数据库。Nginx 将 `api.nanzitravel.com` 转发至新服务，将 `admin.nanzitravel.com` 提供给后台，旧 `/opt/nanzi-ai` 完整归档后退出公网入口但暂不删除。

**Tech Stack:** 微信原生小程序（WXML/WXSS/JavaScript）、Django 5.2 LTS、Django REST framework 3.16、Gunicorn、SQLite WAL、django-storages、boto3、阿里云 OSS、Nginx、systemd、Python unittest/Django TestCase、Node `node:test`

## Global Constraints

- 设计基线：`docs/superpowers/specs/2026-08-12-mini-program-design.md` v0.1。
- 首版只展示已确认发布的南极产品；北极和南非没有产品时不展示空栏目。
- 产品状态固定为 `draft`、`review`、`published`、`archived`。
- 不公开具体价格；不出现购买、订单、支付、定金或合同入口。
- 不收集手机号，不创建咨询表单或咨询单。
- “找搭子”“AI旅行顾问”“消息”首版只展示“功能开发中，敬请期待”。
- 底部导航固定为“首页、消息、我的”。
- “我的”首版不登录，展示品牌、公众号、服务说明、关于我们、协议、隐私和备案信息。
- `api.nanzitravel.com` 用于公开 API；`admin.nanzitravel.com` 用于运营后台。
- 旧 `/opt/nanzi-ai` 服务先备份再隔离，不删除其代码和知识库。
- 任何密钥、AppSecret、OSS Secret、Django Secret Key、后台密码不得提交到 Git。
- 每个任务使用测试先行、独立验收和独立提交。

---

## File Structure

```text
h5-prototype/
├── app/                              # 现有 H5 视觉参考，不作为正式小程序运行时
├── backend/
│   ├── manage.py
│   ├── pyproject.toml
│   ├── config/
│   │   ├── settings.py               # 环境、数据库、OSS、日志和安全配置
│   │   ├── urls.py                   # API 与后台入口
│   │   ├── wsgi.py
│   │   └── tests/
│   ├── catalog/
│   │   ├── models.py                 # 产品、团期、行程、图片、站点设置
│   │   ├── admin.py                  # 运营后台和发布动作
│   │   ├── serializers.py            # 公开 API 输出结构
│   │   ├── views.py                  # 首页、列表、详情、站点信息 API
│   │   ├── urls.py
│   │   ├── storage.py                # 本地/OSS 存储选择
│   │   ├── management/commands/import_products.py
│   │   └── tests/
│   └── requirements.lock
├── miniprogram/
│   ├── app.js
│   ├── app.json
│   ├── app.wxss
│   ├── sitemap.json
│   ├── assets/
│   ├── components/
│   │   ├── product-card/
│   │   ├── empty-state/
│   │   └── coming-soon/
│   ├── pages/
│   │   ├── home/
│   │   ├── products/
│   │   ├── product-detail/
│   │   ├── contact/
│   │   ├── messages/
│   │   ├── profile/
│   │   ├── about/
│   │   ├── privacy/
│   │   └── agreement/
│   ├── services/api.js
│   ├── utils/format.js
│   └── tests/
├── deploy/
│   ├── nginx/nanzi-travel.conf
│   ├── systemd/nanzi-travel-api.service
│   ├── logrotate/nanzi-travel
│   ├── scripts/bootstrap-server.sh
│   ├── scripts/deploy.sh
│   └── scripts/backup.sh
├── content/schema/product.schema.json
├── content/examples/antarctica-demo.json
├── docs/operations/
│   ├── content-publishing.md
│   ├── deployment.md
│   └── rollback.md
├── project.config.json
└── project.private.config.json.example
```

---

### Task 1: 建立正式工程边界与自动检查

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/requirements.lock`
- Create: `backend/manage.py`
- Create: `backend/config/__init__.py`
- Create: `backend/config/settings.py`
- Create: `backend/config/urls.py`
- Create: `backend/config/wsgi.py`
- Create: `backend/config/tests/__init__.py`
- Create: `backend/config/tests/test_settings.py`
- Create: `miniprogram/app.js`
- Create: `miniprogram/app.json`
- Create: `miniprogram/app.wxss`
- Create: `miniprogram/sitemap.json`
- Create: `project.config.json`
- Create: `project.private.config.json.example`
- Modify: `.gitignore`
- Modify: `README.md`

**Interfaces:**
- Produces: Django project `config`, native mini-program root `miniprogram/`, reproducible commands documented in `README.md`.
- Consumes: Python 3.10+ and Node 22+ already available in the local workspace.

- [ ] **Step 1: Write the failing settings test**

```python
from django.conf import settings
from django.test import SimpleTestCase


class SettingsTests(SimpleTestCase):
    def test_public_hosts_and_time_zone_are_explicit(self):
        self.assertEqual(settings.TIME_ZONE, "Asia/Shanghai")
        self.assertIn("api.nanzitravel.com", settings.ALLOWED_HOSTS)
        self.assertIn("admin.nanzitravel.com", settings.ALLOWED_HOSTS)
```

- [ ] **Step 2: Run the test and verify it fails because the Django project does not exist**

Run: `cd backend && python3 -m unittest config.tests.test_settings`

Expected: FAIL with an import error for `django` or `config`.

- [ ] **Step 3: Create the project configuration and pin compatible packages**

Use these runtime constraints in `backend/pyproject.toml`:

```toml
[project]
name = "nanzi-travel-backend"
requires-python = ">=3.10,<3.15"
dependencies = [
  "Django>=5.2.16,<5.3",
  "djangorestframework>=3.16,<3.17",
  "gunicorn>=23,<24",
  "Pillow>=11,<13",
  "django-storages[s3]>=1.14,<2",
  "boto3>=1.40,<2",
]
```

Configure `TIME_ZONE="Asia/Shanghai"`, environment-backed `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, SQLite timeout, static files, media files and structured console logging. Use `touristappid` in committed `project.config.json`; keep the real AppID only in the developer's private local configuration.

- [ ] **Step 4: Install dependencies and run checks**

Run: `cd backend && python3 -m venv .venv && .venv/bin/pip install -e . && .venv/bin/python manage.py check && .venv/bin/python -m unittest config.tests.test_settings`

Expected: Django system check has no issues and the settings test passes.

- [ ] **Step 5: Verify the native mini-program manifest**

Run: `node -e "const fs=require('fs'); const a=JSON.parse(fs.readFileSync('miniprogram/app.json')); if(a.tabBar.list.map(x=>x.text).join(',')!=='首页,消息,我的') process.exit(1)"`

Expected: exit code 0.

- [ ] **Step 6: Commit the scaffold**

```bash
git add .gitignore README.md backend miniprogram project.config.json project.private.config.json.example
git commit -m "chore: scaffold mini program platform"
```

---

### Task 2: 实现旅行产品数据模型和发布规则

**Files:**
- Create: `backend/catalog/__init__.py`
- Create: `backend/catalog/apps.py`
- Create: `backend/catalog/models.py`
- Create: `backend/catalog/migrations/0001_initial.py`
- Create: `backend/catalog/tests/test_models.py`
- Modify: `backend/config/settings.py`

**Interfaces:**
- Produces: `Destination`, `Product`, `Departure`, `ItineraryDay`, `ProductImage`, `SiteSettings` models and `Product.objects.public()`.
- Consumes: Task 1 Django configuration.

- [ ] **Step 1: Write failing model tests**

```python
from django.test import TestCase
from django.utils import timezone
from catalog.models import Destination, Product


class ProductPublishingTests(TestCase):
    def setUp(self):
        self.destination = Destination.objects.create(name="南极", slug="antarctica")

    def test_public_queryset_only_returns_published_products(self):
        Product.objects.create(destination=self.destination, title="草稿", slug="draft", status="draft")
        live = Product.objects.create(
            destination=self.destination,
            title="已发布",
            slug="live",
            status="published",
            published_at=timezone.now(),
        )
        self.assertEqual(list(Product.objects.public()), [live])

    def test_published_product_requires_published_at(self):
        product = Product(destination=self.destination, title="未定时", slug="invalid", status="published")
        with self.assertRaisesMessage(Exception, "published_at"):
            product.full_clean()
```

- [ ] **Step 2: Run the tests and verify missing models**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_models -v 2`

Expected: FAIL because `catalog.models` does not exist.

- [ ] **Step 3: Implement focused models**

Use explicit fields and small related models:

```python
class ProductStatus(models.TextChoices):
    DRAFT = "draft", "草稿"
    REVIEW = "review", "待审核"
    PUBLISHED = "published", "已发布"
    ARCHIVED = "archived", "已下架"


class ProductQuerySet(models.QuerySet):
    def public(self):
        return self.filter(status=ProductStatus.PUBLISHED, published_at__isnull=False)
```

`Product` includes title, slug, subtitle, summary, season, duration_days, destination, hero_image, vessel, departure_city, tags/highlights/included/excluded/suitable_for/notices JSON lists, status, sort_order, published_at and timestamps. `Departure`, `ItineraryDay`, and `ProductImage` use product foreign keys and explicit sort orders. `SiteSettings` is a singleton containing brand, official-account, service, legal and filing copy.

- [ ] **Step 4: Generate migrations and run all model tests**

Run: `cd backend && .venv/bin/python manage.py makemigrations catalog && .venv/bin/python manage.py migrate && .venv/bin/python manage.py test catalog.tests.test_models -v 2`

Expected: migration succeeds and tests pass.

- [ ] **Step 5: Commit the domain model**

```bash
git add backend/catalog backend/config/settings.py
git commit -m "feat: model travel product publishing"
```

---

### Task 3: 建立可由小楠子使用的运营后台

**Files:**
- Create: `backend/catalog/admin.py`
- Create: `backend/catalog/forms.py`
- Create: `backend/catalog/tests/test_admin.py`
- Modify: `backend/config/urls.py`

**Interfaces:**
- Produces: authenticated `/admin/`, product inlines, `publish_products` and `archive_products` actions.
- Consumes: Task 2 models.

- [ ] **Step 1: Write failing admin permission and publish-action tests**

```python
from django.contrib.admin.sites import site
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from catalog.models import Destination, Product


class CatalogAdminTests(TestCase):
    def test_anonymous_user_cannot_open_product_admin(self):
        response = self.client.get(reverse("admin:catalog_product_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/admin/login/", response.url)

    def test_product_is_registered_with_admin(self):
        self.assertIn(Product, site._registry)
```

- [ ] **Step 2: Run tests and verify Product is not registered**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_admin -v 2`

Expected: FAIL on the registry assertion.

- [ ] **Step 3: Configure the product editor**

Register `Destination`, `Product`, and `SiteSettings`. Add inline editors for departures, itinerary days, and product images. Make timestamps read-only, show status/destination/season in the list, add filters for status and destination, and require confirmation for bulk publication. Publication sets `status="published"` and `published_at=timezone.now()`; archiving sets `status="archived"` without deleting content.

- [ ] **Step 4: Add JSON-list validation with clear Chinese errors**

`forms.py` must reject non-list values for `tags`, `highlights`, `included`, `excluded`, `suitable_for`, and `notices`, and reject empty strings inside lists.

- [ ] **Step 5: Run admin tests and Django checks**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_admin -v 2 && .venv/bin/python manage.py check`

Expected: tests pass and system check has no issues.

- [ ] **Step 6: Commit the admin**

```bash
git add backend/catalog/admin.py backend/catalog/forms.py backend/catalog/tests backend/config/urls.py
git commit -m "feat: add travel content admin"
```

---

### Task 4: 提供只读公开 API 和稳定错误格式

**Files:**
- Create: `backend/catalog/serializers.py`
- Create: `backend/catalog/views.py`
- Create: `backend/catalog/urls.py`
- Create: `backend/catalog/tests/test_api.py`
- Modify: `backend/config/urls.py`

**Interfaces:**
- Produces:
  - `GET /api/v1/site`
  - `GET /api/v1/home`
  - `GET /api/v1/products?destination=antarctica&month=2026-11&duration_min=10&duration_max=20&tag=首次去南极`
  - `GET /api/v1/products/<slug>`
- Consumes: Task 2 public queryset and related models.

- [ ] **Step 1: Write failing API visibility tests**

```python
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from catalog.models import Destination, Product


class ProductApiTests(TestCase):
    def setUp(self):
        destination = Destination.objects.create(name="南极", slug="antarctica")
        self.live = Product.objects.create(
            destination=destination,
            title="南极精华",
            slug="antarctica-classic",
            status="published",
            published_at=timezone.now(),
            duration_days=12,
        )
        Product.objects.create(destination=destination, title="签约中", slug="reserve", status="draft")

    def test_product_list_hides_drafts(self):
        response = self.client.get("/api/v1/products")
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item["slug"] for item in response.json()["results"]], ["antarctica-classic"])

    def test_unknown_product_uses_stable_error_shape(self):
        response = self.client.get("/api/v1/products/not-found")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {"error": {"code": "not_found", "message": "产品不存在或尚未发布"}})
```

- [ ] **Step 2: Run tests and verify routes are missing**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_api -v 2`

Expected: FAIL with 404 for the unimplemented list route.

- [ ] **Step 3: Implement serializers and read-only views**

List responses contain only card fields. Detail responses include departures, itinerary days, images, inclusions, exclusions, suitable audiences, notices and the contact-page payload. Validate month as `YYYY-MM`; invalid filters return status 400 with `{"error":{"code":"invalid_filter","message":"出发月份格式应为 YYYY-MM"}}`.

- [ ] **Step 4: Add cache headers and health endpoint**

Set public list/detail responses to `Cache-Control: public, max-age=60`; add `GET /healthz` returning `{"status":"ok"}` without database writes.

- [ ] **Step 5: Run API and full backend tests**

Run: `cd backend && .venv/bin/python manage.py test -v 2`

Expected: all backend tests pass.

- [ ] **Step 6: Commit the API**

```bash
git add backend/catalog backend/config/urls.py
git commit -m "feat: expose published travel catalog api"
```

---

### Task 5: 接入本地媒体与阿里云 OSS

**Files:**
- Create: `backend/catalog/storage.py`
- Create: `backend/catalog/tests/test_storage.py`
- Modify: `backend/catalog/models.py`
- Modify: `backend/config/settings.py`
- Modify: `backend/pyproject.toml`
- Create: `backend/.env.example`

**Interfaces:**
- Produces: local `MEDIA_ROOT` storage in development and `AliyunMediaStorage` in production.
- Consumes: Task 2 image fields and Task 3 admin upload forms.

- [ ] **Step 1: Write failing storage selection tests**

```python
from django.test import SimpleTestCase, override_settings
from catalog.storage import build_media_storage


class MediaStorageTests(SimpleTestCase):
    @override_settings(USE_OSS=False)
    def test_local_mode_uses_filesystem_storage(self):
        self.assertEqual(build_media_storage().__class__.__name__, "FileSystemStorage")
```

- [ ] **Step 2: Run the test and verify the storage module is missing**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_storage -v 2`

Expected: FAIL importing `catalog.storage`.

- [ ] **Step 3: Implement environment-backed storage**

Use these environment variable names only:

```text
USE_OSS
OSS_ACCESS_KEY_ID
OSS_SECRET_ACCESS_KEY
OSS_BUCKET_NAME
OSS_ENDPOINT_URL
OSS_CUSTOM_DOMAIN
```

Production media objects allow anonymous read-only access through the configured media domain; only the backend deployment identity may create, replace, or delete them. Never expose upload credentials to the mini-program.

- [ ] **Step 4: Verify local upload and model migration**

Run: `cd backend && .venv/bin/python manage.py makemigrations catalog && .venv/bin/python manage.py migrate && .venv/bin/python manage.py test catalog.tests.test_storage -v 2`

Expected: tests pass and an admin-uploaded local image resolves under `/media/` in development.

- [ ] **Step 5: Commit media storage**

```bash
git add backend/catalog backend/config/settings.py backend/pyproject.toml backend/.env.example
git commit -m "feat: support product media on oss"
```

---

### Task 6: 实现小程序公共数据层和三栏骨架

**Files:**
- Create: `miniprogram/services/api.js`
- Create: `miniprogram/utils/format.js`
- Create: `miniprogram/tests/api.test.js`
- Create: `miniprogram/tests/format.test.js`
- Create: `miniprogram/pages/home/home.{js,json,wxml,wxss}`
- Create: `miniprogram/pages/messages/messages.{js,json,wxml,wxss}`
- Create: `miniprogram/pages/profile/profile.{js,json,wxml,wxss}`
- Create: `miniprogram/components/empty-state/empty-state.{js,json,wxml,wxss}`
- Modify: `miniprogram/app.json`
- Modify: `miniprogram/app.wxss`

**Interfaces:**
- Produces: `request(path, options)`, `getHome()`, `getProducts(filters)`, `getProduct(slug)`, shared loading/error/empty states and working tab navigation.
- Consumes: Task 4 API response format.

- [ ] **Step 1: Write failing request and formatting tests**

```javascript
const test = require("node:test");
const assert = require("node:assert/strict");
const { buildQuery } = require("../services/api");
const { formatDuration } = require("../utils/format");

test("buildQuery omits empty filters", () => {
  assert.equal(buildQuery({ destination: "antarctica", month: "" }), "destination=antarctica");
});

test("formatDuration uses Chinese day unit", () => {
  assert.equal(formatDuration(12), "12天");
});
```

- [ ] **Step 2: Run tests and verify modules are missing**

Run: `node --test miniprogram/tests/*.test.js`

Expected: FAIL importing the service and formatter.

- [ ] **Step 3: Implement the API client**

Base URL is read from `getApp().globalData.apiBaseUrl` and defaults to `https://api.nanzitravel.com/api/v1`. Requests time out after 10 seconds. Network failures normalize to `{code:"network_error", message:"网络暂时不可用，请稍后重试"}`; non-2xx API errors preserve the backend `error.code` and `error.message`.

- [ ] **Step 4: Implement the shell and global visual tokens**

Use the H5 palette as the baseline: paper `#F3F2EE`, ink `#151515`, accent `#143F35`, accent-soft `#DBE6DE`. Configure tabs “首页、消息、我的”; messages shows the confirmed construction copy. Profile is a real service page, not a login screen.

- [ ] **Step 5: Run pure JavaScript tests and import into WeChat Developer Tools**

Run: `node --test miniprogram/tests/*.test.js`

Expected: all tests pass; developer tools load three tabs without WXML, WXSS or manifest errors.

- [ ] **Step 6: Commit the mini-program shell**

```bash
git add miniprogram project.config.json
git commit -m "feat: add mini program shell and api client"
```

---

### Task 7: 实现首页、产品列表和详情纵向闭环

**Files:**
- Create: `miniprogram/components/product-card/product-card.{js,json,wxml,wxss}`
- Create: `miniprogram/components/coming-soon/coming-soon.{js,json,wxml,wxss}`
- Create: `miniprogram/pages/products/products.{js,json,wxml,wxss}`
- Create: `miniprogram/pages/product-detail/product-detail.{js,json,wxml,wxss}`
- Modify: `miniprogram/pages/home/home.{js,wxml,wxss}`
- Modify: `miniprogram/app.json`
- Create: `miniprogram/tests/product-view-model.test.js`

**Interfaces:**
- Produces: product browsing flow `home → products → product-detail`, and reusable coming-soon behavior.
- Consumes: Task 6 API client and Task 4 response fields.

- [ ] **Step 1: Write failing view-model tests**

```javascript
const test = require("node:test");
const assert = require("node:assert/strict");
const { toProductCard } = require("../pages/products/view-model");

test("product card never invents price", () => {
  const card = toProductCard({ title: "南极精华", duration_days: 12, subtitle: "经典路线" });
  assert.equal(card.priceLabel, "价格咨询");
  assert.equal(card.durationLabel, "12天");
});
```

- [ ] **Step 2: Run the test and verify the view model is missing**

Run: `node --test miniprogram/tests/product-view-model.test.js`

Expected: FAIL importing `view-model`.

- [ ] **Step 3: Implement responsive product discovery**

Home uses magazine-like hero cards from the H5 reference. Product list supports destination, month, duration and tag filters but only renders filter controls that have values in the API response. Empty results use a calm retry/clear-filter state rather than an empty category card.

- [ ] **Step 4: Implement complete product detail**

Render hero, highlights, facts, departures, itinerary, gallery, vessel/resource, inclusions, exclusions, suitable audience, notices and a sticky “咨询该行程” action. Never render a numeric price field in v1.

- [ ] **Step 5: Wire coming-soon entries**

Both “找搭子” and “AI旅行顾问” call the same component and show exactly `功能开发中，敬请期待` without network calls or form fields.

- [ ] **Step 6: Verify tests and manual paths**

Run: `node --test miniprogram/tests/*.test.js`

Expected: all tests pass. In Developer Tools, test API success, no-product state, API timeout, product-detail refresh and back navigation.

- [ ] **Step 7: Commit product browsing**

```bash
git add miniprogram
git commit -m "feat: build product discovery and detail"
```

---

### Task 8: 实现公众号咨询、“我的”和合规页面

**Files:**
- Create: `miniprogram/pages/contact/contact.{js,json,wxml,wxss}`
- Create: `miniprogram/pages/about/about.{js,json,wxml,wxss}`
- Create: `miniprogram/pages/privacy/privacy.{js,json,wxml,wxss}`
- Create: `miniprogram/pages/agreement/agreement.{js,json,wxml,wxss}`
- Modify: `miniprogram/pages/profile/profile.{js,wxml,wxss}`
- Modify: `miniprogram/pages/product-detail/product-detail.js`
- Modify: `miniprogram/app.json`
- Create: `miniprogram/tests/contact.test.js`

**Interfaces:**
- Produces: product-aware contact page, official account component with fallback, brand/service/legal pages.
- Consumes: Task 4 `/site` payload and Task 7 selected product title.

- [ ] **Step 1: Write failing contact-copy test**

```javascript
const test = require("node:test");
const assert = require("node:assert/strict");
const { buildConsultationCopy } = require("../pages/contact/view-model");

test("consultation copy includes product title", () => {
  assert.equal(
    buildConsultationCopy("12天南极半岛精华"),
    "我想咨询：12天南极半岛精华",
  );
});
```

- [ ] **Step 2: Run test and verify the view model is missing**

Run: `node --test miniprogram/tests/contact.test.js`

Expected: FAIL importing the contact view model.

- [ ] **Step 3: Implement consultation page with two valid paths**

Render `<official-account>` when WeChat allows it. Always render the fallback:公众号名称“小楠子爱旅行俱乐部”、search instructions, current product title and copyable consultation wording. Do not claim that a normal button can always open a公众号 chat.

- [ ] **Step 4: Implement the useful profile tab**

Profile includes brand card, contact entry, official-account guidance, service description, about, agreement, privacy and ICP filing information. It contains no login button and no fake counters.

- [ ] **Step 5: Verify all navigation and official-account error events**

Run: `node --test miniprogram/tests/*.test.js`

Expected: tests pass. In Developer Tools, simulate `official-account` load error and verify the fallback remains fully usable.

- [ ] **Step 6: Commit contact and compliance pages**

```bash
git add miniprogram
git commit -m "feat: add official account consultation flow"
```

---

### Task 9: 建立产品导入格式与可重复内容发布

**Files:**
- Create: `content/schema/product.schema.json`
- Create: `content/examples/antarctica-demo.json`
- Create: `backend/catalog/management/__init__.py`
- Create: `backend/catalog/management/commands/__init__.py`
- Create: `backend/catalog/management/commands/import_products.py`
- Create: `backend/catalog/tests/test_import_products.py`
- Create: `docs/operations/content-publishing.md`

**Interfaces:**
- Produces: `python manage.py import_products <file> --status=draft` with idempotent slug-based updates.
- Consumes: Task 2 models and the later real product content supplied by the partner.

- [ ] **Step 1: Write failing idempotent import test**

```python
from django.core.management import call_command
from django.test import TestCase
from catalog.models import Product


class ImportProductsTests(TestCase):
    def test_importing_same_slug_twice_updates_without_duplicate(self):
        call_command("import_products", "content/examples/antarctica-demo.json", status="draft")
        call_command("import_products", "content/examples/antarctica-demo.json", status="draft")
        self.assertEqual(Product.objects.filter(slug="antarctica-demo").count(), 1)
```

- [ ] **Step 2: Run the test and verify the command is missing**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_import_products -v 2`

Expected: FAIL because `import_products` is unknown.

- [ ] **Step 3: Define and validate the JSON contract**

The schema requires slug, title, destination, summary, duration_days, status-independent content arrays, itinerary and departures. Unknown keys fail validation to prevent silent content loss. The example is clearly named “演示内容” and is imported as `draft`, never `published`.

- [ ] **Step 4: Implement atomic import**

Use `transaction.atomic()`, `update_or_create(slug=...)`, replace related itinerary/departure/image rows only after the whole file validates, and print created/updated counts. Reject `--status=published` unless every product has at least one hero image, one highlight, one itinerary row and one notice.

- [ ] **Step 5: Run import and full backend tests**

Run: `cd backend && .venv/bin/python manage.py test -v 2 && .venv/bin/python manage.py import_products ../content/examples/antarctica-demo.json --status=draft`

Expected: tests pass; one draft demo product exists and is absent from public API.

- [ ] **Step 6: Commit the publishing workflow**

```bash
git add content backend/catalog/management backend/catalog/tests docs/operations/content-publishing.md
git commit -m "feat: add repeatable product content import"
```

---

### Task 10: 安全部署、历史服务归档和回滚

**Files:**
- Create: `deploy/nginx/nanzi-travel.conf`
- Create: `deploy/systemd/nanzi-travel-api.service`
- Create: `deploy/logrotate/nanzi-travel`
- Create: `deploy/scripts/bootstrap-server.sh`
- Create: `deploy/scripts/deploy.sh`
- Create: `deploy/scripts/backup.sh`
- Create: `deploy/tests/test_deploy_files.sh`
- Create: `docs/operations/deployment.md`
- Create: `docs/operations/rollback.md`

**Interfaces:**
- Produces: system service on `127.0.0.1:8001`, Nginx HTTPS routes, daily database/media/config backup, documented rollback.
- Consumes: backend from Tasks 1–5, existing server, `api.nanzitravel.com`, `admin.nanzitravel.com`.

- [ ] **Step 1: Write failing deployment-file assertions**

```bash
#!/usr/bin/env bash
set -euo pipefail
grep -q '127.0.0.1:8001' deploy/systemd/nanzi-travel-api.service
grep -q 'server_name api.nanzitravel.com' deploy/nginx/nanzi-travel.conf
grep -q 'server_name admin.nanzitravel.com' deploy/nginx/nanzi-travel.conf
! grep -R --line-number -E '(SECRET_KEY|ACCESS_KEY|PASSWORD)=.+$' deploy
```

- [ ] **Step 2: Run the test and verify deployment files are missing**

Run: `bash deploy/tests/test_deploy_files.sh`

Expected: FAIL because service and Nginx files do not exist.

- [ ] **Step 3: Create least-privilege runtime and deployment config**

The service runs as `nanziapp`, binds only `127.0.0.1:8001`, uses `/opt/nanzi-travel/current/backend`, loads `/etc/nanzi-travel/backend.env`, and restarts on failure. Nginx serves `/api/` and `/healthz` on the API host and `/admin/` plus static assets on the admin host. Add request-size limits and security headers.

- [ ] **Step 4: Encode the safe server transition**

`bootstrap-server.sh` must:

1. create `/opt/backups/nanzi-ai/<timestamp>`;
2. archive `/opt/nanzi-ai`, its systemd unit, Nginx config and non-secret metadata;
3. renew or issue valid certificates for both new hosts;
4. create the `nanziapp` runtime account and `/opt/nanzi-travel/releases` layout;
5. remove public access to port 5000 at the host/cloud firewall level;
6. leave the historical files intact;
7. require explicit `CONFIRM_SERVER_BOOTSTRAP=1` before making changes.

- [ ] **Step 5: Add backup and rollback behavior**

Backup uses `sqlite3 .backup` for a consistent database copy, archives `/etc/nanzi-travel` without printing secrets, retains 14 daily copies and verifies each archive with `tar -tf`. Rollback switches `/opt/nanzi-travel/current` to the previous release, runs `manage.py migrate`, restarts the service and verifies `/healthz`.

- [ ] **Step 6: Run static deployment tests**

Run: `bash deploy/tests/test_deploy_files.sh && git diff --check`

Expected: all assertions pass and no secret-looking assignment is committed.

- [ ] **Step 7: Commit deployment artifacts**

```bash
git add deploy docs/operations/deployment.md docs/operations/rollback.md
git commit -m "ops: add secure server deployment and rollback"
```

---

### Task 11: 完成首版端到端验收与发布清单

**Files:**
- Create: `docs/qa/v1-acceptance.md`
- Create: `docs/qa/wechat-review-checklist.md`
- Modify: `docs/superpowers/specs/2026-08-12-mini-program-design.md`
- Modify: `README.md`

**Interfaces:**
- Produces: repeatable acceptance evidence and design version v0.2 reflecting implemented details.
- Consumes: all previous tasks and the partner's first approved product set when available.

- [ ] **Step 1: Run all automated tests**

Run: `cd backend && .venv/bin/python manage.py test -v 2 && cd .. && node --test miniprogram/tests/*.test.js && bash deploy/tests/test_deploy_files.sh`

Expected: all commands pass.

- [ ] **Step 2: Verify the vertical publishing slice**

Create one draft product in admin, preview it, publish it, verify it appears in `/api/v1/home`, open it in the mini-program, navigate to the contact page, then archive it and verify it disappears from list and detail APIs.

- [ ] **Step 3: Verify failure behavior**

Test offline mode, 10-second API timeout, malformed product slug, empty product list, broken image URL, official-account component load failure and expired admin session. Each path must show a recoverable Chinese message and must not expose a stack trace or secret.

- [ ] **Step 4: Verify compliance copy and navigation**

Confirm there is no purchase/payment/contract wording, no numeric price, no phone collection, and no false claim that the button always opens公众号 chat. Confirm the message page and both future-feature entries show the agreed construction copy.

- [ ] **Step 5: Update design version and release evidence**

Increment the design baseline to v0.2, add the implemented architecture decisions and a version-history entry, and link the acceptance and WeChat review checklists.

- [ ] **Step 6: Commit acceptance documentation**

```bash
git add README.md docs
git commit -m "docs: add v1 acceptance and review checklist"
```

---

## Parallel Product Content Preparation

Development can begin before final products arrive. The partner should prepare each launch product using the fields in `content/schema/product.schema.json`:

1. official product title and short subtitle;
2. authorized hero image and gallery images with source/usage confirmation;
3. one-paragraph summary and 3–6 highlights;
4. total days, route, vessel/resource, departure location and season;
5. all valid departures and their consultation status;
6. complete daily/segmented itinerary;
7. inclusions and exclusions;
8. suitable audience, physical requirements and important notices;
9. actual contracting/service provider identity for internal review;
10. confirmation that the content may be publicly published.

Content from the two suppliers still under contract is imported only as `draft` and remains invisible until written publication approval is confirmed.
