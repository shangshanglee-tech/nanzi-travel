# 回滚操作手册

## 应用版本回滚

不传参数会选择当前版本之外最新的一份发布目录：

```bash
sudo deploy/scripts/rollback.sh
```

也可以明确指定版本：

```bash
sudo deploy/scripts/rollback.sh /opt/nanzi-travel/releases/<时间戳>
```

脚本会切换 `current` 软链接、运行兼容迁移、重启服务并验证本机健康检查。

## 数据恢复

数据恢复是独立且有损的操作，不由应用回滚脚本自动执行。恢复前必须停止 API、再备份当前数据库，然后从 `/opt/backups/nanzi-travel/<时间戳>/db.sqlite3` 恢复，并重新启动服务验证。

## 恢复旧 nanzi-ai 服务

1. 停止 `nanzi-travel-api.service`。
2. 从 `/opt/backups/nanzi-ai/<时间戳>` 核对旧应用、systemd 和 Nginx 归档。
3. 恢复原 Nginx 链接和 systemd 单元。
4. 保持 5000 不直接对公网开放，仅通过 Nginx 验证。
5. 运行 `nginx -t` 后重载 Nginx，并检查旧服务日志。
