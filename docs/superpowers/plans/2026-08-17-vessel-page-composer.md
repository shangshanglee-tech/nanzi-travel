# Vessel Page Composer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let operators compose a vessel detail page from ordered headings and image cards, while independently controlling the optional cabin and deck-plan sections.

**Architecture:** Add a `VesselPageBlock` model for the ordered middle-page stream and a `VesselDeckPlan` model for ordered deck-plan images. Keep cabin groups as the existing structured records and expose them only when `show_cabins` is enabled. The Django vessel editor uses stacked inline blocks plus a small admin script that folds card rows under their preceding heading; the mini-program renders the public API in its fixed page order.

**Tech Stack:** Django 5.2, Django admin, Django REST Framework, WeChat Mini Program WXML/WXSS/JavaScript, Node built-in tests, Django `TestCase`.

## Global Constraints

- A page block is either a heading or a content card.
- A heading has a required title and no image requirement.
- A content card has a required title and image; its body is optional.
- Card blocks inherit their displayed group from the preceding heading in sort order.
- The front end remains a complete information flow and never folds groups.
- Cabin detail and deck plans are both optional whole-page tail sections controlled by vessel-level boolean fields.
- Deck-plan items are ordered images with an optional title and description.
- Existing `VesselExperience` rows are no longer rendered as the page-composer content stream.

---

### Task 1: Persist page blocks and deck plans

**Files:**
- Modify: `backend/catalog/models.py`
- Create: `backend/catalog/migrations/0010_vessel_page_composer.py`
- Test: `backend/catalog/tests/test_models.py`

**Interfaces:**
- Produces `VesselPageBlock(vessel, block_type, title, image, body, is_visible, sort_order)`.
- Produces `VesselDeckPlan(vessel, title, description, image, is_visible, sort_order)`.
- Produces `Vessel.show_cabins` and `Vessel.show_deck_plans` booleans.

- [ ] **Step 1: Write failing model validation tests**

```python
def test_content_card_requires_a_title_and_image(self):
    block = VesselPageBlock(vessel=self.vessel, block_type="card")
    with self.assertRaisesRegex(ValidationError, "图片"):
        block.full_clean()

def test_heading_only_requires_its_title(self):
    block = VesselPageBlock(vessel=self.vessel, block_type="heading", title="船上体验")
    block.full_clean()
```

- [ ] **Step 2: Run the model tests and verify they fail because the models do not exist.**

- [ ] **Step 3: Add models, validation, ordering metadata, and migration.**

- [ ] **Step 4: Run the model tests and verify they pass.**

### Task 2: Add the operator editor with group folding

**Files:**
- Modify: `backend/catalog/admin.py`
- Create: `backend/catalog/static/catalog/vessel-page-blocks-admin.js`
- Test: `backend/catalog/tests/test_admin.py`

**Interfaces:**
- Consumes the models from Task 1.
- Produces vessel editor fieldsets for tail-section switches and three stacked inlines: page blocks, cabins, deck plans.

- [ ] **Step 1: Write failing admin tests that assert the inline models and display switches are registered.**

```python
inline_models = {inline.model for inline in VesselAdmin.inlines}
self.assertIn(VesselPageBlock, inline_models)
self.assertIn(VesselDeckPlan, inline_models)
self.assertIn("show_cabins", editable_fields)
self.assertIn("show_deck_plans", editable_fields)
```

- [ ] **Step 2: Run the focused admin test and verify it fails.**

- [ ] **Step 3: Register stacked inlines and attach the editor JavaScript.**

- [ ] **Step 4: Implement JavaScript that detects heading rows and toggles the following card rows until the next heading; newly added rows are reprocessed.**

- [ ] **Step 5: Run the focused admin test and verify it passes.**

### Task 3: Publish the composed content API

**Files:**
- Modify: `backend/catalog/serializers.py`
- Test: `backend/catalog/tests/test_api.py`

**Interfaces:**
- Consumes visible ordered `page_blocks`, `deck_plans`, `show_cabins`, and `show_deck_plans`.
- Produces public vessel detail keys `page_blocks`, `deck_plans`, `show_cabins`, and `show_deck_plans`.

- [ ] **Step 1: Write a failing API test for visible ordered blocks, card image URLs, hidden blocks, and the two switches.**

- [ ] **Step 2: Run the vessel API test and verify it fails.**

- [ ] **Step 3: Add block and deck-plan serializers plus vessel detail serializer methods that filter `is_visible=True`.**

- [ ] **Step 4: Run the vessel API test and verify it passes.**

### Task 4: Render the information flow on the mini-program vessel page

**Files:**
- Modify: `miniprogram/pages/vessel-detail/view-model.js`
- Modify: `miniprogram/pages/vessel-detail/vessel-detail.wxml`
- Modify: `miniprogram/pages/vessel-detail/vessel-detail.wxss`
- Test: `miniprogram/tests/vessel-detail.test.js`

**Interfaces:**
- Consumes `page_blocks`, `deck_plans`, `show_cabins`, and `show_deck_plans` from Task 3.
- Produces `detail.pageBlocks`, `detail.cabinGroups`, and `detail.deckPlans` for WXML.

- [ ] **Step 1: Write failing view-model and markup tests covering ordered headings/cards, no front-end folding, and both optional tail sections.**

- [ ] **Step 2: Run the vessel-detail Node test and verify it fails.**

- [ ] **Step 3: Render headings and cards after the facility grid, then conditionally render cabins and deck plans after them.**

- [ ] **Step 4: Run the vessel-detail Node test and verify it passes.**

### Task 5: Verify, migrate, and commit

**Files:**
- Modify: all files above

- [ ] **Step 1: Run `node --test miniprogram/tests/*.test.js`.**
- [ ] **Step 2: Run `/tmp/nanzi-test-311/bin/python backend/manage.py test catalog.tests -v 1`.**
- [ ] **Step 3: Run `/tmp/nanzi-test-311/bin/python backend/manage.py makemigrations --check --dry-run` and `git diff --check`.**
- [ ] **Step 4: Commit scoped changes without `project.config.json`.**
