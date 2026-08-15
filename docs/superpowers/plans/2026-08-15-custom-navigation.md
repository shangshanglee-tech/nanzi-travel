# 自定义小程序顶部导航 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 全局移除微信默认标题栏，并为二级页面提供安全、统一的自定义返回与标题栏。

**Architecture:** 在 `app.json` 启用自定义导航栏；新增一个轻量的顶部导航组件，由非首页页面按需引用。组件读取微信胶囊按钮信息计算右侧安全区，并在无历史栈时回到首页。

**Tech Stack:** 微信小程序原生组件、Node 内置测试运行器。

## Global Constraints

- 首页不显示品牌标题。
- 非首页页面保留返回入口和当前页面标题。
- 不修改接口、内容模型、底部 Tab 或咨询流程。

---

### Task 1: 自定义顶部导航组件

**Files:**
- Create: `miniprogram/components/page-nav/page-nav.js`
- Create: `miniprogram/components/page-nav/page-nav.wxml`
- Create: `miniprogram/components/page-nav/page-nav.wxss`
- Create: `miniprogram/components/page-nav/page-nav.json`
- Create: `miniprogram/tests/page-nav.test.js`

**Interfaces:**
- Produces: `getNavigationMetrics()`，返回 `{topPadding, height, rightPadding}`。
- Consumes: 组件属性 `title: string` 和 `showBack: boolean`。

- [ ] **Step 1: 写失败测试**

```js
const {getNavigationMetrics} = require("../../miniprogram/components/page-nav/metrics");
test("uses system capsule position for right safe space", () => {
  assert.equal(getNavigationMetrics({top: 48, height: 32}, 24).rightPadding, 44);
});
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `node --test miniprogram/tests/page-nav.test.js`
Expected: FAIL with module not found.

- [ ] **Step 3: 实现最小组件**

```js
function getNavigationMetrics(capsule, statusBarHeight = 0) {
  return {topPadding: statusBarHeight, height: capsule.height + 12, rightPadding: capsule.width + 16};
}
```

组件点击返回时：历史栈大于一层调用 `wx.navigateBack()`，否则调用 `wx.switchTab({url: "/pages/home/home"})`。

- [ ] **Step 4: 运行测试并确认通过**

Run: `node --test miniprogram/tests/page-nav.test.js`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add miniprogram/components/page-nav miniprogram/tests/page-nav.test.js
git commit -m "feat: add custom page navigation"
```

### Task 2: 全局启用并接入各页面

**Files:**
- Modify: `miniprogram/app.json`
- Modify: `miniprogram/pages/products/products.json`
- Modify: `miniprogram/pages/product-detail/product-detail.json`
- Modify: `miniprogram/pages/vessel-detail/vessel-detail.json`
- Modify: `miniprogram/pages/contact/contact.json`
- Modify: `miniprogram/pages/messages/messages.json`
- Modify: `miniprogram/pages/profile/profile.json`
- Modify: `miniprogram/pages/about/about.json`
- Modify: `miniprogram/pages/privacy/privacy.json`
- Modify: `miniprogram/pages/agreement/agreement.json`
- Modify: each corresponding `.wxml`

**Interfaces:**
- Consumes: `page-nav` component and its `title` / `showBack` properties.
- Produces: 页面不再依赖微信默认导航栏。

- [ ] **Step 1: 写失败配置测试**

```js
const config = require("../../miniprogram/app.json");
test("uses custom navigation globally", () => {
  assert.equal(config.window.navigationStyle, "custom");
});
```

- [ ] **Step 2: 运行测试并确认失败**

Run: `node --test miniprogram/tests/page-nav.test.js`
Expected: FAIL because `navigationStyle` is absent.

- [ ] **Step 3: 逐页接入**

在每个非首页页面内容前插入：

```xml
<page-nav title="页面标题" show-back="{{true}}" />
```

在页面配置内注册 `page-nav`，并将全局 `window.navigationStyle` 设为 `custom`。首页不插入组件。

- [ ] **Step 4: 运行测试并确认通过**

Run: `node --test miniprogram/tests/page-nav.test.js`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add miniprogram
git commit -m "feat: use custom navigation throughout mini program"
```

### Task 3: 完整校验

**Files:**
- Test: `miniprogram/tests/*.test.js`

- [ ] **Step 1: 运行完整小程序测试**

Run: `node --test miniprogram/tests/*.test.js`
Expected: PASS.

- [ ] **Step 2: 检查格式与项目配置**

Run: `git diff --check`
Expected: no output.

- [ ] **Step 3: 在微信开发者工具验证**

验证首页无默认标题，产品与船只详情可返回，右上角胶囊不遮挡内容。
