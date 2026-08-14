# 小楠子爱旅行：程序自动发布设计

## 目标

把已验证的 `release` 分支自动发布到正式 API，并上传一份微信小程序体验版；正式审核与正式发布始终由管理员在微信后台人工完成。

## 触发与范围

- 触发：向 GitHub 私有仓库的 `release` 分支推送代码，或在 GitHub Actions 页面手动触发。
- 自动执行：代码测试、服务器备份、后端部署、服务健康检查、微信体验版上传。
- 不自动执行：微信审核提交、微信正式发布、数据库/产品内容的自动公开。
- 未通过测试的提交不会连接服务器，也不会上传体验版。

## 发布流程

1. GitHub Actions 运行 Node 小程序测试、Django 测试与 Django 系统检查。
2. 测试通过后，以专用发布账号 SSH 连接阿里云服务器。
3. 服务器运行现有备份脚本，备份 SQLite 数据库、媒体文件与运行配置。
4. 工作流上传当前提交的发布包；服务器使用现有 `deploy.sh` 创建带时间戳的新 release，执行迁移、收集静态文件、重启 `nanzi-travel-api.service`。
5. 工作流请求 `https://api.nanzitravel.com/healthz`。仅收到成功响应时，才继续微信体验版上传。
6. 使用微信 `miniprogram-ci` 将 `miniprogram/` 上传为体验版；版本号使用 GitHub run number，备注包含短提交号。
7. GitHub Actions 输出部署版本、健康检查结果和微信上传结果；失败步骤可在 Actions 日志直接定位。

## 失败与回滚

- 前置测试、包上传、部署或健康检查任一失败：工作流立即失败，不执行微信上传。
- 线上服务切换后健康检查失败：工作流调用服务器现有 `rollback.sh` 回到上一 release，再次检查健康状态；回滚失败时保留完整日志供人工处理。
- 自动回滚只处理程序文件与服务指针，不还原数据库。数据库迁移必须保持向后兼容；破坏性迁移不进入此自动流程。
- 工作流需要使用 `concurrency`：同一时间最多一个正式发布，新的发布等待或取消仍在排队的旧发布，避免两次部署互相覆盖。

## 凭证与权限

所有凭证仅保存在 GitHub Actions Secrets，禁止进入仓库、部署包、运行日志和小程序前端：

- `DEPLOY_HOST`：服务器 IP 或主机名。
- `DEPLOY_USER`：仅用于部署的 Linux 账号，不使用 root 登录。
- `DEPLOY_SSH_PRIVATE_KEY`：该账号对应的 SSH 私钥。
- `WECHAT_APPID`：小程序 AppID。
- `WECHAT_PRIVATE_KEY`：微信公众平台为小程序代码上传生成的私钥全文。

服务器新增受限 `nanzi-deploy` 账号。该账号需要普通 SSH shell 以便 GitHub 上传发布包并执行固定发布命令，但只能通过受控的 sudo 命令调用备份、部署、回滚和必要的服务状态检查；不可获得交互式 root shell。现有 `nanzi-ai.service` 不在发布脚本或权限范围内。

## 版本与审计

- 每次 API release 使用 UTC 时间戳目录，沿用 `/opt/nanzi-travel/releases/`。
- 备份目录沿用 `/opt/backups/nanzi-travel/`，默认保存 14 天。
- GitHub Actions 日志保留本次发布提交号、创建 release 路径、备份路径和体验版版本号，不输出密钥或环境变量全文。
- 内容数据继续由顾问在后台管理；本阶段不让 GitHub 工作流重新导入 HX 内容，避免代码发布覆盖人工编辑。

## 验收标准

1. 向 `release` 推送一个已通过测试的提交，可无需手工登录服务器完成 API 部署。
2. 部署成功后 `/healthz` 返回成功，且 GitHub Actions 记录该 release 路径。
3. 同一次发布自动产生新的微信体验版，管理员可在微信开发者工具/后台看到版本备注。
4. 测试失败或健康检查失败时，不上传体验版；健康检查失败后自动尝试一次回滚。
5. 仓库和 Actions 日志中不出现服务器密码、SSH 私钥或微信私钥。
