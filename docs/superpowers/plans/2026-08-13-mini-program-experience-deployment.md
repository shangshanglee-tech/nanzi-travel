# 小楠子爱旅行体验版部署 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 导入 11 条已授权 HX 南极线路，隔离部署小程序 API，并生成可由体验成员扫码访问的微信体验版。

**Architecture:** 新增 HX 数据转换命令，把 H5 数据映射为既有产品导入格式，并将封面图复制到 Django 受管媒体目录。生产环境只创建新的 Django、Nginx 与 systemd 服务；不执行会停止历史 AI 服务的旧初始化脚本。小程序已指向正式 API，服务验证后通过微信开发者工具上传体验版。

**Tech Stack:** Python 3.12、Django、SQLite、Gunicorn、Nginx、Let's Encrypt、微信原生小程序。

## Global Constraints

- 不得停止、删除或改变 `/opt/nanzi-ai` 与 `nanzi-ai.service` 的运行状态。
- 只发布 11 条已授权 HX 南极内容；不导入价格和库存，团期使用“咨询获取最新方案”。
- 不提交微信审核、不对公众发布；仅上传体验版。
- 不开放支付、订单、合同、登录、真实搭子、真实消息或面向用户的 AI。
- Gunicorn 仅监听 `127.0.0.1:8001`，公网仅开放 HTTPS。

---

## 文件结构

- `content/imports/hx-antarctica.json`：11 条路线的固定导入源。
- `content/imports/hx-heroes/<slug>/hero.webp`：11 张已授权封面图。
- `backend/catalog/management/commands/import_hx_antarctica.py`：H5 数据转换、媒体复制与产品导入。
- `backend/catalog/tests/test_import_hx_antarctica.py`：转换、幂等和媒体导入测试。
- `deploy/scripts/bootstrap-isolated-service.sh`：仅为新服务创建运行环境和证书。
- `deploy/tests/test_deploy_files.sh`：隔离脚本安全约束检查。
- `docs/operations/deployment.md`：隔离部署与体验版上传说明。

### Task 1: 固化 HX 内容并实现受测试约束的导入命令

**Files:**
- Create: `content/imports/hx-antarctica.json`
- Create: `content/imports/hx-heroes/<11个slug>/hero.webp`
- Create: `backend/catalog/management/commands/import_hx_antarctica.py`
- Create: `backend/catalog/tests/test_import_hx_antarctica.py`

**Interfaces:**
- Consumes: `products[].id/title/durationDays/summary/routeSummary/shipIds/departures/highlights/itinerary/hero`。
- Produces: `python manage.py import_hx_antarctica SOURCE --media-root PATH --status published`；写入既有 `Product`、`Departure`、`ItineraryDay` 与受管封面图。

- [ ] **Step 1: 写失败测试**

```python
def test_hx_import_creates_published_products_and_managed_hero_files(self):
    call_command("import_hx_antarctica", self.source, media_root=self.media_root, status="published")
    self.assertEqual(Product.objects.count(), 11)
    product = Product.objects.get(slug="highlights-of-antarctica")
    self.assertEqual(product.status, ProductStatus.PUBLISHED)
    self.assertTrue((self.media_root / product.hero_image.name).is_file())
    self.assertGreater(product.departures.count(), 0)
    self.assertGreater(product.itinerary_days.count(), 0)
```

- [ ] **Step 2: 验证失败**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_import_hx_antarctica -v 2`

Expected: FAIL，提示未知命令 `import_hx_antarctica`。

- [ ] **Step 3: 实现转换和幂等导入**

```python
def normalize_day_number(value: str, fallback: int) -> int:
    match = re.search(r"\d+", value)
    return int(match.group()) if match else fallback
```

将目的地写为 `{name: "南极", slug: "antarctica"}`；把 `shipIds` 映射为船名；每个日期写为 `start_date`、`label` 和 `consultation_status="咨询获取最新方案"`；按起始日保存行程段，不伪造逐日行程。封面复制至 `products/heroes/hx-<slug>.webp`，然后调用既有 `import_products` 完成写入。

- [ ] **Step 4: 验证通过**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_import_hx_antarctica catalog.tests.test_import_products -v 2`

Expected: PASS；重复执行后仍只有 11 条产品。

- [ ] **Step 5: 提交**

```bash
git add content/imports backend/catalog/management/commands/import_hx_antarctica.py backend/catalog/tests/test_import_hx_antarctica.py
git commit -m "feat: import authorized HX Antarctica catalogue"
```

### Task 2: 验收真实内容的公开 API

**Files:**
- Modify: `backend/catalog/tests/test_api.py`
- Create: `docs/qa/hx-import-verification.md`

**Interfaces:**
- Consumes: Task 1 的命令与导入源。
- Produces: 本地数据库 11 条 `published` 产品，`/api/v1/home`、`/api/v1/products`、`/api/v1/products/<slug>` 可展示。

- [ ] **Step 1: 写 API 回归测试**

```python
def test_published_hx_product_is_present_in_list_and_detail(self):
    call_command("import_hx_antarctica", HX_SOURCE, status="published")
    listing = self.client.get("/api/v1/products")
    detail = self.client.get("/api/v1/products/highlights-of-antarctica")
    self.assertEqual(listing.status_code, 200)
    self.assertEqual(len(listing.json()["items"]), 11)
    self.assertEqual(detail.status_code, 200)
    self.assertTrue(detail.json()["departures"])
```

- [ ] **Step 2: 验证测试与实际数据导入**

Run: `cd backend && .venv/bin/python manage.py test catalog.tests.test_api -v 2 && .venv/bin/python manage.py import_hx_antarctica ../content/imports/hx-antarctica.json --status published && .venv/bin/python manage.py test -v 2`

Expected: PASS；若响应为列表而非 `items`，只调整断言以匹配既有公开 API，不改接口格式。

- [ ] **Step 3: 记录抽查并提交**

记录首页、列表、11 个详情、团期、图片与咨询文案抽查结果至 `docs/qa/hx-import-verification.md`。

```bash
git add backend/catalog/tests/test_api.py docs/qa/hx-import-verification.md
git commit -m "test: verify published HX catalogue APIs"
```

### Task 3: 新增不会触碰历史 AI 的初始化脚本

**Files:**
- Create: `deploy/scripts/bootstrap-isolated-service.sh`
- Modify: `deploy/tests/test_deploy_files.sh`
- Modify: `docs/operations/deployment.md`

**Interfaces:**
- Consumes: `/etc/nanzi-travel/backend.env`、现有 Nginx 与 systemd 模板。
- Produces: `sudo CONFIRM_ISOLATED_BOOTSTRAP=1 deploy/scripts/bootstrap-isolated-service.sh` 仅创建新运行账户、目录、证书、Nginx 和 systemd 配置。

- [ ] **Step 1: 写隔离安全静态测试**

```python
isolated = (root / "deploy/scripts/bootstrap-isolated-service.sh").read_text()
assert "CONFIRM_ISOLATED_BOOTSTRAP" in isolated
assert "nanzi-ai" not in isolated
assert "/opt/nanzi-ai" not in isolated
assert "5000" not in isolated
```

- [ ] **Step 2: 验证失败**

Run: `bash deploy/tests/test_deploy_files.sh`

Expected: FAIL，因为隔离脚本尚不存在。

- [ ] **Step 3: 实现隔离脚本**

脚本须拒绝未设置 `CONFIRM_ISOLATED_BOOTSTRAP=1` 的执行；只创建 `nanziapp`、`/opt/nanzi-travel`、`/var/lib/nanzi-travel`、日志和配置目录，校验生产环境变量文件，申请两个新域名证书，安装小程序服务相关 Nginx、systemd 和 logrotate 文件，并在 `nginx -t` 后 reload。不得包含针对旧服务的 `rm`、`disable`、`stop` 或 `kill`。

- [ ] **Step 4: 验证通过并提交**

Run: `bash deploy/tests/test_deploy_files.sh && bash -n deploy/scripts/bootstrap-isolated-service.sh`

Expected: PASS。

```bash
git add deploy/scripts/bootstrap-isolated-service.sh deploy/tests/test_deploy_files.sh docs/operations/deployment.md
git commit -m "feat: add isolated travel service bootstrap"
```

### Task 4: 服务器隔离部署与 HTTPS 验证

**Files:**
- Modify: `/etc/nanzi-travel/backend.env`（服务器配置，不提交）
- Runtime: `/opt/nanzi-travel/releases/*`、`/var/lib/nanzi-travel/db.sqlite3`、Nginx/systemd 配置（不提交）

**Interfaces:**
- Consumes: Task 1/3 提交、SSH 管理权限、已解析的两个域名。
- Produces: `https://api.nanzitravel.com/healthz`、`https://api.nanzitravel.com/api/v1/home`、`https://admin.nanzitravel.com/admin/`。

- [ ] **Step 1: 只读检查旧服务与端口**

Run: `ssh <server> 'systemctl status nanzi-ai.service --no-pager || true; readlink -f /opt/nanzi-ai || true; ss -lntup'`

Expected: 只记录，不停止或重启旧服务。

- [ ] **Step 2: 创建最小生产环境变量**

依据 `backend/.env.example` 创建配置，设置随机 `DJANGO_SECRET_KEY`、`DJANGO_DEBUG=false`、两个域名、生产数据库与媒体目录；首版设 `USE_OSS=false`，用后台域名 HTTPS 提供本地媒体；权限为 `0640 root:nanziapp`。

- [ ] **Step 3: 启动独立服务并部署**

```bash
sudo CONFIRM_ISOLATED_BOOTSTRAP=1 deploy/scripts/bootstrap-isolated-service.sh
sudo deploy/scripts/deploy.sh /path/to/h5-prototype/.worktrees/mini-program-v1
```

Expected: 新服务启动，旧 AI 状态与 Step 1 相同。

- [ ] **Step 4: 导入生产内容并创建后台管理员**

```bash
sudo -u nanziapp env DJANGO_DB_PATH=/var/lib/nanzi-travel/db.sqlite3 /opt/nanzi-travel/current/backend/.venv/bin/python /opt/nanzi-travel/current/backend/manage.py import_hx_antarctica /opt/nanzi-travel/current/backend/content/imports/hx-antarctica.json --status published
sudo -u nanziapp /opt/nanzi-travel/current/backend/.venv/bin/python /opt/nanzi-travel/current/backend/manage.py createsuperuser
```

Expected: 11 条产品可见；管理员密码只在受控终端输入，绝不写入仓库。

- [ ] **Step 5: 外网验证**

Run: `curl --fail https://api.nanzitravel.com/healthz && curl --fail https://api.nanzitravel.com/api/v1/home && curl --fail -I https://admin.nanzitravel.com/admin/`

Expected: 三项成功，新服务为 active，旧 AI 状态未改变。

### Task 5: 微信域名配置与体验版上传

**Files:**
- Modify: `miniprogram/app.js`（仅当生产地址与现值不一致时）
- Runtime: 微信公众平台开发设置与微信开发者工具上传记录（不提交）

**Interfaces:**
- Consumes: Task 4 的有效 API；AppID `wx9dacae494a7ff9ab`；管理员和体验成员。
- Produces: 体验版二维码；两名体验成员在微信中看到真实产品内容。

- [ ] **Step 1: 配置 request 合法域名**

在小程序公众平台“开发管理 → 开发设置 → 服务器域名”添加 `https://api.nanzitravel.com`，等待校验成功；不添加 IP、HTTP 或无关域名。

- [ ] **Step 2: 真机预览并上传**

在微信开发者工具导入项目根目录，确认 AppID 为 `wx9dacae494a7ff9ab`，真机检查首页、列表、详情、团期与咨询入口。上传版本 `0.1.0-experience`，备注“11 条 HX 南极产品展示与咨询入口；仅体验版”，不点击“提交审核”。

- [ ] **Step 3: 扫码验收并提交必要代码变更**

在公众平台“版本管理”取得体验二维码，由管理员和合伙人扫码验收。仅在 `app.js` 有实际修改时执行：

```bash
git add miniprogram/app.js
git commit -m "chore: set production API endpoint"
```

## 自查

- 五个任务覆盖内容导入、隔离部署、HTTPS、后台、微信体验版与回退路径。
- 不包含产品价格、支付、合同、账号、真实搭子、消息或用户 AI。
- 不使用会停止历史 AI 服务的旧 bootstrap 脚本。
- 所有代码任务均含失败验证、实现、通过验证与提交步骤；无 TBD/TODO 占位。
