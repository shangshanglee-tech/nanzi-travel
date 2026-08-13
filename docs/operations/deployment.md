# 服务器部署操作手册

## 上线前条件

1. `api.nanzitravel.com` 和 `admin.nanzitravel.com` 均解析到目标服务器。
2. 已在 `/etc/nanzi-travel/backend.env` 填写生产配置，权限为 `0640 root:nanziapp`。
   OSS 的 boto3 Endpoint 使用 `https://s3.oss-<地域>.aliyuncs.com` 格式，代码固定采用 V2 签名和虚拟托管寻址。
3. 已确认阿里云安全组仅开放 22、80、443，未开放 5000 和 8001。
4. 已确认旧 `/opt/nanzi-ai` 服务无人使用，并预留回滚窗口。

## 首次初始化

旧的 `bootstrap-server.sh` 会归档并关闭历史 AI 服务，只能在已经明确确认要下线旧服务时使用。首版体验版部署不得执行它。

体验版使用只创建新服务的隔离初始化脚本。执行前确认 `api.nanzitravel.com` 与 `admin.nanzitravel.com` 已解析至此服务器，并预先创建 `/etc/nanzi-travel/backend.env`：

```bash
sudo CERTBOT_EMAIL=管理员邮箱 \
  CONFIRM_ISOLATED_BOOTSTRAP=1 deploy/scripts/bootstrap-isolated-service.sh
```

该脚本不会触碰 `/opt/nanzi-ai`、`nanzi-ai.service` 或历史服务端口配置。

## 旧服务切换（不用于体验版）

初始化脚本会先完整归档旧服务，再申请证书、建立最小权限账户、切换 Nginx 配置并关闭旧服务。必须阅读脚本后显式确认：

```bash
sudo CONFIRM_SERVER_BOOTSTRAP=1 deploy/scripts/bootstrap-server.sh
```

旧服务归档位于 `/opt/backups/nanzi-ai/<时间戳>`，源文件不会删除。主机防火墙会封锁 5000；阿里云安全组仍须在控制台人工核对。

## 发布新版本

```bash
sudo deploy/scripts/backup.sh
sudo deploy/scripts/deploy.sh /path/to/h5-prototype
```

发布后检查：

- `https://api.nanzitravel.com/healthz`
- `https://api.nanzitravel.com/api/v1/home`
- `https://admin.nanzitravel.com/admin/`
- `systemctl status nanzi-travel-api.service`
- `nginx -t`

## 定时备份

以 root 的定时任务每天运行 `deploy/scripts/backup.sh`。备份默认保留 14 天，包含 SQLite 一致性副本、媒体文件和加密存储所需的运行配置；备份目录必须仅 root 可读。
