# Django Admin Operations Navigation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Keep Django Admin's existing top bar and data behavior while adding an operations sidebar and tabbed vessel editor.

**Architecture:** A custom `admin/base_site.html` wraps all Admin content in an operations sidebar plus the existing content area. The vessel change form keeps its original single Django form and inline formsets; a dedicated Admin-only script inserts tabs and only hides or shows existing sections, so Django validation and formset management fields remain unchanged.

**Tech Stack:** Django Admin templates, Django `ModelAdmin.Media`, vanilla browser JavaScript, CSS, Django `TestCase`.

**Spec:** `docs/superpowers/specs/2026-08-18-django-admin-operations-navigation-design.md`

## Global Constraints

- Preserve the existing Django Admin top bar, URLs, authentication, permissions and server-side save behavior.
- Show only 旅行产品、目的地、船只、站点设置 in the operations sidebar.
- Do not add React, Ant Design, a new backend API, or a new data model.
- Keep every vessel tab panel in the same Django `<form>`; never clone, remove or move formset management inputs.
- Tab labels must be 基础信息、首页卡片、结构化事实、页面内容、舱位、甲板图.
- Use TDD: a focused test must fail before each production behavior change.

---

### Task 1: Add the global operations sidebar shell

**Files:**
- Create: `backend/catalog/templates/admin/base_site.html`
- Create: `backend/catalog/static/catalog/admin-operations.css`
- Modify: `backend/catalog/admin.py`
- Modify: `backend/catalog/tests/test_admin.py`

**Interfaces:**
- Consumes: Django Admin's `admin/base.html`, `admin_site.each_context`, `perms` and URL names `admin:catalog_*_changelist`.
- Produces: A global Admin layout with `.operations-sidebar`, `.operations-main` and active navigation markers.

- [ ] **Step 1: Write the failing sidebar render test**

```python
response = self.client.get(reverse("admin:catalog_vessel_changelist"))
self.assertContains(response, 'data-operations-nav="true"')
self.assertContains(response, "旅行产品")
self.assertContains(response, "目的地")
self.assertContains(response, "船只")
self.assertContains(response, "站点设置")
self.assertNotContains(response, 'data-operations-nav-item="用户"')
```

- [ ] **Step 2: Run the targeted test and verify it fails**

Run: `python manage.py test catalog.tests.test_admin.CatalogAdminTests.test_operations_sidebar_contains_only_daily_editorial_entries -v 2`

Expected: FAIL because no custom Admin base template exists.

- [ ] **Step 3: Add the minimal base template and stylesheet**

```django
{% extends "admin/base.html" %}
{% load i18n static %}
{% block extrastyle %}{{ block.super }}<link rel="stylesheet" href="{% static 'catalog/admin-operations.css' %}">{% endblock %}
{% block content %}
<div class="operations-layout">
  <nav class="operations-sidebar" data-operations-nav="true">…</nav>
  <main class="operations-main">{{ block.super }}</main>
</div>
{% endblock %}
```

Use `perms.catalog.view_product`, `view_destination`, `view_vessel` and `view_sitesettings` to gate each link. Compare `request.resolver_match.view_name` to mark the current model item active.

- [ ] **Step 4: Run the targeted test and verify it passes**

Run: `python manage.py test catalog.tests.test_admin.CatalogAdminTests.test_operations_sidebar_contains_only_daily_editorial_entries -v 2`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/catalog/templates/admin/base_site.html backend/catalog/static/catalog/admin-operations.css backend/catalog/admin.py backend/catalog/tests/test_admin.py
git commit -m "feat: add admin operations sidebar"
```

### Task 2: Add vessel editor tab interaction

**Files:**
- Create: `backend/catalog/static/catalog/vessel-editor-tabs.js`
- Modify: `backend/catalog/static/catalog/admin-operations.css`
- Modify: `backend/catalog/admin.py`
- Modify: `backend/catalog/tests/test_admin.py`

**Interfaces:**
- Consumes: The unchanged vessel change form, Django fieldset headings, inline group IDs and `.errorlist` markup.
- Produces: `data-vessel-editor-tabs`, tab buttons and `.vessel-tab-panel` visibility classes without moving form controls.

- [ ] **Step 1: Write failing source and render tests**

```python
response = self.client.get(reverse("admin:catalog_vessel_change", args=[vessel.pk]))
self.assertContains(response, 'data-vessel-editor-tabs="true"')
for label in ("基础信息", "首页卡片", "结构化事实", "页面内容", "舱位", "甲板图"):
    self.assertContains(response, label)

source = (Path(__file__).resolve().parents[1] / "static/catalog/vessel-editor-tabs.js").read_text()
self.assertIn("#page_blocks-group", source)
self.assertIn("TOTAL_FORMS", source)
self.assertIn("firstInvalidPanel", source)
```

- [ ] **Step 2: Run the targeted test and verify it fails**

Run: `python manage.py test catalog.tests.test_admin.CatalogAdminTests.test_vessel_editor_renders_six_tabs_without_replacing_formsets -v 2`

Expected: FAIL because the tab asset and hook are absent.

- [ ] **Step 3: Register assets and implement tab controller**

In `VesselAdmin.Media`, load `catalog/vessel-editor-tabs.js` after `catalog/vessel-page-blocks-admin.js` and load `catalog/admin-operations.css`.

The script must:

```javascript
const tabs = [
  {id: "general", label: "基础信息", fieldsets: ["基础与发布", "中文展示文案"]},
  {id: "card", label: "首页卡片", fieldsets: ["首页卡片展示"]},
  {id: "facts", label: "结构化事实", fieldsets: ["结构化事实"]},
  {id: "content", label: "页面内容", groups: ["#page_blocks-group"]},
  {id: "cabins", label: "舱位", groups: ["#cabintype_set-group", "#cabindisplaygroup_set-group"], fields: ["show_cabins"]},
  {id: "decks", label: "甲板图", groups: ["#vesseldeckplan_set-group"], fields: ["show_deck_plans"]},
];
```

Build buttons as `type="button"`, assign existing fieldsets / inline groups to a panel by adding CSS classes only, and switch with `hidden` plus an `is-active` class. Detect the first tab containing `.errorlist` or `.errors` on page load and activate it.

- [ ] **Step 4: Run the targeted test and verify it passes**

Run: `python manage.py test catalog.tests.test_admin.CatalogAdminTests.test_vessel_editor_renders_six_tabs_without_replacing_formsets -v 2`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add backend/catalog/static/catalog/vessel-editor-tabs.js backend/catalog/static/catalog/admin-operations.css backend/catalog/admin.py backend/catalog/tests/test_admin.py
git commit -m "feat: add vessel editor tabs"
```

### Task 3: Verify admin save and existing page-content image deletion

**Files:**
- Modify: `backend/catalog/tests/test_admin.py`
- Modify: `backend/catalog/static/catalog/vessel-editor-tabs.js` only if the test shows a panel switch breaks form input inclusion.

**Interfaces:**
- Consumes: Existing `VesselPageBlockInlineForm` and its `existing_additional_images` delete field.
- Produces: Proof that tab interaction preserves management fields and existing additional-image deletion.

- [ ] **Step 1: Write failing regression test for tabbed form preservation**

```python
response = self.client.get(reverse("admin:catalog_vessel_change", args=[vessel.pk]))
self.assertContains(response, 'name="page_blocks-TOTAL_FORMS"')
self.assertContains(response, 'name="page_blocks-INITIAL_FORMS"')
self.assertContains(response, 'name="page_blocks-0-existing_additional_images"')
self.assertContains(response, 'data-vessel-tab="content"')
```

- [ ] **Step 2: Run the targeted test and verify it fails**

Run: `python manage.py test catalog.tests.test_admin.CatalogAdminTests.test_vessel_tabs_keep_page_block_management_and_delete_fields -v 2`

Expected: FAIL until the page-content inline is assigned to the content Tab without being removed from the form.

- [ ] **Step 3: Make the smallest tab-controller correction**

Keep all native inputs in their original DOM positions. Toggle only the `hidden` attribute on the enclosing fieldset or inline group; do not alter `name`, `id`, `value`, `TOTAL_FORMS`, `INITIAL_FORMS`, `DELETE`, or `existing_additional_images` fields.

- [ ] **Step 4: Run backend and mini-program regression checks**

Run:

```bash
python manage.py test catalog.tests.test_admin -v 2
node --test miniprogram/tests/*.test.js
git diff --check
```

Expected: all tests pass; no whitespace errors.

- [ ] **Step 5: Commit**

```bash
git add backend/catalog/tests/test_admin.py backend/catalog/static/catalog/vessel-editor-tabs.js
git commit -m "test: preserve vessel editor formsets across tabs"
```

## Self-review

- The plan includes every confirmed sidebar item and every confirmed vessel Tab.
- The sidebar preserves Django Admin's top bar and URL/permission model.
- The tab controller only changes visibility and cannot break Django formset submission.
- Each task has a focused failing test, explicit verification command and commit point.
