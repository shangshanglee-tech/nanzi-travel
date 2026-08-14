# GitHub 自动发布配置

本指南只配置“自动部署 API + 自动上传微信体验版”。它不会提交微信审核或发布正式小程序。

## 1. 创建私有仓库并推送代码

1. 在 GitHub 新建一个 **Private** 仓库，例如 `nanzi-travel`；不要勾选初始化 README。
2. 在本项目根目录添加 GitHub 地址，并把当前工作分支推上去：

```bash
git remote add github git@github.com:你的用户名/nanzi-travel.git
git push -u github feat/mini-program-v1
git push github feat/mini-program-v1:release
```

3. 在 GitHub 的 Branch protection rules 中保护 `release`：要求测试工作流通过，限制直接推送人员为你自己。

## 2. 创建仅用于发布的 SSH 密钥

在你的 Mac 终端执行。该密钥只用于 GitHub → 阿里云发布，不要复用个人 SSH 密钥：

```bash
ssh-keygen -t ed25519 -f ~/.ssh/nanzi_github_deploy -C "nanzi-github-deploy"
cat ~/.ssh/nanzi_github_deploy.pub
```

复制第二条命令输出的整行公钥。私钥文件 `~/.ssh/nanzi_github_deploy` 不要上传到仓库、不要通过聊天发送。

## 3. 在服务器创建受限发布账号

用现有管理员账号连接服务器并进入 root shell。把项目发布包上传到服务器临时目录后，在项目目录执行：

```bash
CONFIRM_GITHUB_DEPLOY_USER=1 deploy/scripts/bootstrap-github-deploy-user.sh
```

然后把步骤 2 得到的公钥追加到服务器：

```bash
install -d -o nanzi-deploy -g nanzi-deploy -m 0700 /home/nanzi-deploy/.ssh
printf '%s\n' '粘贴步骤2复制的整行公钥' >> /home/nanzi-deploy/.ssh/authorized_keys
chown nanzi-deploy:nanzi-deploy /home/nanzi-deploy/.ssh/authorized_keys
chmod 0600 /home/nanzi-deploy/.ssh/authorized_keys
```

验证账号只拥有受控发布权限：

```bash
sudo -l -U nanzi-deploy
```

输出应只包含 `/usr/local/sbin/nanzi-github-release` 这一个命令。不要修改旧的 `nanzi-ai.service`。

## 4. 设置 GitHub Actions Secrets

进入 GitHub 仓库：**Settings → Secrets and variables → Actions → New repository secret**，逐项添加：

| 名称 | 值 |
|---|---|
| `DEPLOY_HOST` | 阿里云服务器公网 IP 或主机名 |
| `DEPLOY_USER` | `nanzi-deploy` |
| `DEPLOY_SSH_PRIVATE_KEY` | `~/.ssh/nanzi_github_deploy` 私钥全文 |
| `WECHAT_APPID` | 小程序 AppID |
| `WECHAT_PRIVATE_KEY` | 微信公众平台生成的“小程序代码上传”私钥全文 |

微信私钥在微信公众平台的小程序开发设置中生成。生成后只将其粘贴进 GitHub Secret；不要保存在项目文件夹。

## 5. 首次演练

1. 进入 GitHub 的 **Actions → Release → Run workflow**，选择 `release`。
2. 观察顺序：测试通过 → 服务器备份 → API 部署 → `healthz` 成功 → 微信上传成功。
3. 在微信开发者工具或公众平台查看新的体验版；备注应形如 `release abc123d`。
4. 如 API 健康检查失败，工作流会尝试回滚；不要点击微信审核提交。

## 日常使用

把已经验证的功能合入并推送到 `release` 即可。GitHub Actions 完成后，再由管理员在微信后台决定是否提交审核和发布正式版本。
