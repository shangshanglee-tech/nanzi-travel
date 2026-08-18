# Django Admin 运营导航改造设计

## 目标

在不替换 Django Admin 顶部栏、账号权限和保存机制的前提下，将日常运营入口收敛为左侧分级导航；将船只编辑的长表单拆成右侧横向 Tab，降低内容维护时的滚动与误操作成本。

## 范围

本次只覆盖 Django Admin 的运营入口与船只编辑页。

- 保留 Django Admin 顶部栏、面包屑、登录、权限与默认保存行为。
- 左栏只显示：旅行产品、目的地、船只、站点设置。
- 用户、组仍可通过 Django Admin 原有入口访问，但不出现在运营左栏。
- 船只编辑页使用横向 Tab：基础信息、首页卡片、结构化事实、页面内容、舱位、甲板图。
- 不新增业务数据模型、API 或独立前端后台。

## 页面结构

```text
┌──────────────────── 顶部：保留 Django Admin ────────────────────┐
├──────── 左侧运营导航 ────────┬────────── 右侧当前内容 ───────────┤
│ 内容管理                    │ 船只编辑页                       │
│  - 旅行产品                 │ [基础信息][首页卡片][结构化事实] │
│  - 目的地                   │ [页面内容][舱位][甲板图]         │
│  - 船只                     │                                  │
│                              │ 当前 Tab 的 Django 原生表单      │
│ 系统                         │                                  │
│  - 站点设置                 │ 原有保存按钮与错误提示           │
└─────────────────────────────┴──────────────────────────────────┘
```

## 左侧运营导航

使用 Django Admin 的自定义基础模板插入导航区域，不改变现有 Admin URL。

| 分组 | 项目 | URL | 选中条件 |
| --- | --- | --- | --- |
| 内容管理 | 旅行产品 | `admin:catalog_product_changelist` | 当前 model 为 `catalog.Product` |
| 内容管理 | 目的地 | `admin:catalog_destination_changelist` | 当前 model 为 `catalog.Destination` |
| 内容管理 | 船只 | `admin:catalog_vessel_changelist` | 当前 model 为 `catalog.Vessel` |
| 系统 | 站点设置 | `admin:catalog_sitesettings_changelist` | 当前 model 为 `catalog.SiteSettings` |

导航使用 Django 模板反向 URL；无权限项目不渲染。用户与组不在该导航中，但不移除默认 Admin 权限能力。

## 船只编辑 Tab

编辑表单仍是同一个 `<form>`，所有 Tab 内容始终保留在 DOM 中。切换仅用 JavaScript 控制显示状态，因此：

- 用户可在多个 Tab 中连续修改；
- 点击 Django 原有保存按钮时，所有修改一起提交；
- 后端原有校验、图片上传、待删除图片、inline formset 管理字段完全沿用；
- 保存失败时，前端自动切换到第一个包含字段错误的 Tab。

| Tab | 对应现有字段 / Inline |
| --- | --- |
| 基础信息 | 基础与发布、中文展示文案 |
| 首页卡片 | 首页卡片展示 |
| 结构化事实 | 结构化事实 |
| 页面内容 | `VesselPageBlockInline` |
| 舱位 | `CabinTypeInline`、`CabinDisplayGroupInline` |
| 甲板图 | 页面末尾模块的甲板开关、`VesselDeckPlanInline` |

“页面末尾模块”中的舱位展示开关放入“舱位”；甲板展示开关放入“甲板图”。

## 技术实现

- 新增 Django Admin 基础模板覆盖，基于 `admin/base_site.html` 继承，并在主内容区域外包裹运营侧栏。
- `VesselAdmin` 提供自定义 `change_form_template`，为船只编辑页输出 Tab 元数据与容器标记。
- 新增仅用于 Admin 的 JavaScript：初始化 Tab、记录当前 Tab、切换面板、保存失败时定位第一个有错误的面板。
- 新增仅用于 Admin 的 CSS：两栏布局、左栏当前态、横向 Tab；视觉遵循当前 Django Admin 样式，不引入 Ant Design 或 React 依赖。
- 现有 `vessel-page-blocks-admin.js` 持续负责页面内容卡片的分组、折叠、图片删除与新增行行为；Tab 脚本不得改写它的表单字段或管理字段。

## 错误与边界

- 侧栏链接通过 URL reverse 生成；某个模型未注册或当前用户无权限时不显示链接。
- 首次打开船只编辑页默认停留“基础信息”。
- 若提交校验失败，包含 `.errors` 或 `.errorlist` 的第一个 Tab 自动成为当前 Tab。
- Tab 切换不会删除、克隆或移动输入控件，避免破坏 Django inline formset 的 `TOTAL_FORMS`、`INITIAL_FORMS` 和图片待删除字段。
- 在窄屏下左栏与内容区改为上下排列；后台的主要使用场景仍为桌面端。

## 验收与测试

- Django Admin 页面包含四个运营导航项目，并按当前 model 呈现选中态。
- 无权限用户看不到对应运营导航链接。
- 船只编辑页渲染六个横向 Tab；每个 Tab 对应正确的现有 fieldset 或 inline。
- 切换 Tab 后，所有表单 input 与 inline 管理字段仍在同一个 form 内。
- 页面内容卡片的“添加图片”“删除图片”和保存流程继续可用。
- 模型表单错误注入后，页面初始激活包含第一个错误的 Tab。
- 运行 backend 管理后台测试与现有小程序测试，不出现回归。
