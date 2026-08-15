# Vessel Content Backoffice Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a desktop content backoffice and reusable vessel detail template, using MS Roald Amundsen as the first complete vessel.

**Architecture:** Django Admin becomes the protected desktop editor for the first release. Official English facts and editable Chinese content are stored separately. The mini program exposes only published records from the API, so content-only publication needs no WeChat code upload.

**Tech Stack:** Django 5.2, Django REST Framework, Django Admin, SQLite, existing media storage, WeChat mini program WXML/JS.

## Global Constraints

- Preserve every official cabin code and structured fact even if the page groups cabins differently.
- Preserve English official source text and editable Chinese operating copy.
- Use project media storage; never hotlink official images.
- Public ship pages exclude live price, inventory, payment and contract data.
- Public API returns published content only.
- Code deployment must never overwrite manually edited vessel content.

## File Map

- `backend/catalog/models.py`: vessel state, bilingual fields, experience modules, cabin groups and media.
- `backend/catalog/admin.py`, `backend/catalog/forms.py`: desktop editing, validation and publishing.
- `backend/catalog/serializers.py`, `backend/catalog/views.py`: published vessel API.
- `backend/catalog/management/commands/import_hx_polar_content.py`: safe, explicit source refresh.
- `deploy/scripts/deploy.sh`: application deployment only.
- `miniprogram/pages/vessel-detail/*`: modular public ship detail page.
- `content/imports/hx-roald-amundsen-content.json`: reviewed source snapshot for the initial vessel.
- `backend/catalog/management/commands/import_vessel_content.py`: idempotent first-vessel import.

---

### Task 1: Protect edited vessel content during code deployment

**Files:**
- Modify: `deploy/scripts/deploy.sh`
- Modify: `deploy/tests/test_deploy_files.sh`
- Modify: `backend/catalog/management/commands/import_hx_polar_content.py`
- Modify: `backend/catalog/tests/test_polar_content.py`

**Produces:** Deployments that never import or overwrite content. `import_hx_polar_content SOURCE` remains available but deletes source data only with explicit `--replace-source-data`.

- [ ] **Step 1: Write the failing safety test**

Add:

```python
assert "import_hx_polar_content" not in deploy_script
assert "/var/lib/nanzi-travel/content" not in deploy_script
```

- [ ] **Step 2: Verify red**

Run: `bash deploy/tests/test_deploy_files.sh`

Expected: failure because the current script imports HX content.

- [ ] **Step 3: Implement deployment safety**

Remove the content copying and `import_hx_polar_content` call from `deploy/scripts/deploy.sh`. Keep migration, static collection, restart and health checks.

Add:

```python
parser.add_argument("--replace-source-data", action="store_true")
```

Pass this flag into existing import helpers and put broad `.delete()` calls behind it.

- [ ] **Step 4: Add preservation test and verify green**

Create a cabin with `summary="人工文案"`, import without the flag, and assert it remains:

```python
self.assertTrue(CabinType.objects.filter(summary="人工文案").exists())
```

Run:

```bash
bash deploy/tests/test_deploy_files.sh
cd backend && python manage.py test catalog.tests.test_polar_content -v 1
```

- [ ] **Step 5: Commit**

```bash
git add deploy backend/catalog/management/commands/import_hx_polar_content.py backend/catalog/tests/test_polar_content.py
git commit -m "fix: keep vessel content safe during releases"
```

### Task 2: Add the full reusable vessel content model

**Files:**
- Modify: `backend/catalog/models.py`
- Create: `backend/catalog/migrations/0004_vessel_content_backoffice.py`
- Modify: `backend/catalog/tests/test_models.py`

**Produces:**
- `VesselContentStatus`: `DRAFT` and `PUBLISHED`.
- `VesselExperience`: bilingual on-board experience blocks.
- `CabinDisplayGroup`: vessel-specific presentation group with many cabins.
- `VesselMedia`: an image attached to exactly one vessel, experience or cabin.

- [ ] **Step 1: Write failing model tests**

Cover: a published vessel requires `published_at`; one cabin can belong to two groups; media with two parents is rejected.

```python
vessel.content_status = VesselContentStatus.PUBLISHED
with self.assertRaises(ValidationError):
    vessel.full_clean()
```

- [ ] **Step 2: Verify red**

Run: `cd backend && python manage.py test catalog.tests.test_models -v 1`

Expected: attributes and model classes do not exist.

- [ ] **Step 3: Implement models**

Extend `Vessel` with `operator_name`, `ship_type`, `year_refurbished`, `short_pitch`, `intro_zh`, `intro_en`, `source_checked_at`, `content_status`, `published_at`, `created_at` and `updated_at`.

Extend `CabinType` with `official_code`, `official_name`, `description_zh`, `description_en`, `max_guests`, `deck`, `amenities`, `display_tags`, `is_accessible`, `is_visible` and `source_checked_at`.

```python
class VesselExperience(models.Model):
    vessel = models.ForeignKey(Vessel, related_name="experiences", on_delete=models.CASCADE)
    kind = models.CharField(max_length=80, blank=True)
    title_zh = models.CharField(max_length=160)
    title_en = models.CharField(max_length=160, blank=True)
    body_zh = models.TextField(blank=True)
    body_en = models.TextField(blank=True)
    is_visible = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
```

`VesselMedia.clean()` counts non-null vessel/experience/cabin parents and requires exactly one.

- [ ] **Step 4: Create migration and verify green**

```bash
cd backend
python manage.py makemigrations catalog --name vessel_content_backoffice
python manage.py sqlmigrate catalog 0004
python manage.py test catalog.tests.test_models -v 1
```

Expected: additive migration and passing tests.

- [ ] **Step 5: Commit**

```bash
git add backend/catalog/models.py backend/catalog/migrations/0004_vessel_content_backoffice.py backend/catalog/tests/test_models.py
git commit -m "feat: add vessel editorial content models"
```

### Task 3: Build the desktop editor and published vessel API

**Files:**
- Modify: `backend/catalog/admin.py`
- Modify: `backend/catalog/forms.py`
- Modify: `backend/catalog/serializers.py`
- Modify: `backend/catalog/views.py`
- Modify: `backend/catalog/tests/test_admin.py`
- Modify: `backend/catalog/tests/test_api.py`

**Produces:** A protected editor at `/admin/catalog/vessel/<id>/change/` and a detail API containing overview, experience modules, grouped cabins, media and linked routes.

- [ ] **Step 1: Write failing Admin and API tests**

Assert Vessel is registered, has experience/group/media inlines, and `publish_vessels` stamps a date. Assert drafts are excluded from public responses and published detail contains cabin code and groups:

```python
self.assertEqual(response.json()["cabin_groups"][0]["cabins"][0]["official_code"], "MA")
self.assertNotIn(draft.slug, [item["slug"] for item in response.json()["results"]])
```

- [ ] **Step 2: Verify red**

```bash
cd backend
python manage.py test catalog.tests.test_admin catalog.tests.test_api -v 1
```

Expected: Vessel is not registered and fields are missing.

- [ ] **Step 3: Implement the editor**

Add `VesselAdminForm` and `CabinTypeAdminForm` to validate `features`, `amenities` and `display_tags` as lists of nonempty strings.

Register `VesselAdmin` with sections “基础与发布”, “中文展示文案”, “英文原文与来源”, “结构化事实”. Add stacked inlines for experiences/groups, tabular inline for media, and actions `publish_vessels` and `unpublish_vessels`.

- [ ] **Step 4: Implement public serializers and views**

Add request-aware media, experience, cabin and cabin-group serializers. Filter public queries with `is_active=True`, `content_status="published"` and non-null `published_at`. Prefetch media, experiences, cabin groups/cabins and linked routes.

Visible cabins without a group must be returned in an `其他舱位` group.

- [ ] **Step 5: Verify green and commit**

```bash
cd backend
python manage.py test catalog.tests.test_admin catalog.tests.test_api -v 1
python manage.py check
git add backend/catalog/admin.py backend/catalog/forms.py backend/catalog/serializers.py backend/catalog/views.py backend/catalog/tests
git commit -m "feat: publish vessel content from desktop editor"
```

### Task 4: Render the reusable vessel template in the mini program

**Files:**
- Create: `miniprogram/pages/vessel-detail/view-model.js`
- Modify: `miniprogram/pages/vessel-detail/vessel-detail.js`
- Modify: `miniprogram/pages/vessel-detail/vessel-detail.wxml`
- Modify: `miniprogram/pages/vessel-detail/vessel-detail.wxss`
- Create: `miniprogram/tests/vessel-detail.test.js`

**Produces:** Vessel pages ordered as hero/facts, overview, experience modules, cabin groups, linked routes and consultation.

- [ ] **Step 1: Write failing view-model tests**

```javascript
const state = buildVesselDetailState(vessel);
assert.deepEqual(state.cabinGroups.map((group) => group.title), ["套房", "阳台房"]);
assert.equal(state.experiences.length, 1);
```

Also cover empty or hidden modules and ungrouped cabins.

- [ ] **Step 2: Verify red**

Run: `node --test miniprogram/tests/vessel-detail.test.js`

Expected: module-not-found failure.

- [ ] **Step 3: Implement state and page**

```javascript
{ facts: [], experiences: [], cabinGroups: [], gallery: [], products: [] }
```

Use Chinese API fields first, official names only as fallback. Every optional WXML section uses `wx:if`; no empty cards. Render experience galleries, official cabin codes/facts, routes and existing consultation entry.

- [ ] **Step 4: Verify green and commit**

```bash
node --test miniprogram/tests/*.test.js
git add miniprogram/pages/vessel-detail miniprogram/tests/vessel-detail.test.js
git commit -m "feat: render modular vessel detail"
```

### Task 5: Seed MS Roald Amundsen and release

**Files:**
- Create: `content/imports/hx-roald-amundsen-content.json`
- Create: `backend/catalog/management/commands/import_vessel_content.py`
- Create: `backend/catalog/tests/test_vessel_content_import.py`
- Modify: `README.md`

**Produces:** `python manage.py import_vessel_content PATH --publish`, an idempotent import that changes only the named vessel. Natural keys are vessel slug, experience kind, group slug and `(vessel, official_code)`.

- [ ] **Step 1: Write failing idempotence test**

```python
call_command("import_vessel_content", source, publish=True)
call_command("import_vessel_content", source, publish=True)
self.assertEqual(VesselExperience.objects.count(), 1)
```

Also assert the vessel is visible through the public detail endpoint.

- [ ] **Step 2: Verify red**

Run: `cd backend && python manage.py test catalog.tests.test_vessel_content_import -v 1`

Expected: command-not-found failure.

- [ ] **Step 3: Create source snapshot and importer**

Record all available official cabin codes, facts, English source text, Chinese editorial copy and source URL/check date. Do not invent unavailable facts. Record official image URLs/captions as source metadata; only upload user-selected final images.

Implement via `update_or_create`; never use broad deletes. `--publish` sets `published_at` only after the complete import succeeds.

- [ ] **Step 4: Verify and release**

```bash
cd backend && python manage.py test catalog.tests -v 1 && python manage.py check
cd .. && node --test miniprogram/tests/*.test.js
bash deploy/tests/test_deploy_files.sh
bash deploy/tests/test_github_release_files.sh
git diff --check
```

Push verified code to `release`, run the explicit 阿蒙森号 import with `--publish`, verify `/api/v1/vessels/roald-amundsen`, then upload a WeChat experience build once because the client page has changed. Later content-only publishing needs no WeChat upload.

- [ ] **Step 5: Commit**

```bash
git add content/imports/hx-roald-amundsen-content.json backend/catalog/management/commands/import_vessel_content.py backend/catalog/tests/test_vessel_content_import.py README.md
git commit -m "feat: seed MS Roald Amundsen vessel content"
```

