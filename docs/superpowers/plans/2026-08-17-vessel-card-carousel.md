# Vessel Card Carousel Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Allow each operator-configured vessel page card to show an ordered, swipeable set of images.

**Architecture:** Keep the card's existing required image as its first image so existing content remains valid. Add ordered `VesselPageBlockImage` records for additional images, managed from the same vessel editor. The API combines the primary image and visible extra images into a single `images` list; the mini-program renders one image normally or a scrollable carousel with a page indicator when more than one image exists.

**Tech Stack:** Django 5.2, Django admin, Django REST Framework, WeChat Mini Program WXML/WXSS/JavaScript, Node built-in tests, Django `TestCase`.

## Global Constraints

- Only `card` blocks may receive additional images.
- An additional image must belong to the same vessel as its selected card.
- The original card image remains first in the public `images` list.
- Hidden additional images never appear in the public API.
- The indicator appears only when a card has two or more images.
- Existing cards and their first images remain valid without data migration.

---

### Task 1: Persist ordered additional card images

**Files:**
- Modify: `backend/catalog/models.py`
- Create: `backend/catalog/migrations/0011_vessel_page_block_images.py`
- Test: `backend/catalog/tests/test_models.py`

- [ ] Write failing validation tests for card-only and same-vessel constraints.
- [ ] Run the tests and verify failure.
- [ ] Add `VesselPageBlockImage` with image, visibility, and sort order validation.
- [ ] Generate migration and rerun tests.

### Task 2: Add vessel-editor image management and public API

**Files:**
- Modify: `backend/catalog/admin.py`
- Modify: `backend/catalog/serializers.py`
- Test: `backend/catalog/tests/test_admin.py`
- Test: `backend/catalog/tests/test_api.py`

- [ ] Write failing tests for the image inline and ordered public `images` list.
- [ ] Add the vessel-scoped additional-image inline and serializer method.
- [ ] Run focused backend tests.

### Task 3: Render swipeable cards with indicators

**Files:**
- Modify: `miniprogram/pages/vessel-detail/view-model.js`
- Modify: `miniprogram/pages/vessel-detail/vessel-detail.js`
- Modify: `miniprogram/pages/vessel-detail/vessel-detail.wxml`
- Modify: `miniprogram/pages/vessel-detail/vessel-detail.wxss`
- Test: `miniprogram/tests/vessel-detail.test.js`

- [ ] Write a failing view-model/markup test for carousel state and indicators.
- [ ] Add per-card image index state and a horizontal `scroll-view` image rail.
- [ ] Render the indicator only for cards with multiple images.
- [ ] Run Node tests.

### Task 4: Verify and commit

- [ ] Run all Django and Node tests.
- [ ] Run migration check and whitespace check.
- [ ] Commit without `project.config.json` or unrelated local work.
