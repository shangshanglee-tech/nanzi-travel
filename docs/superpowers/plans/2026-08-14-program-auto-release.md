# Program Auto Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Push a verified `release` branch to deploy the API safely and upload a WeChat experience build without automatically submitting it for review.

**Architecture:** A GitHub Actions workflow performs test gates and then opens an SSH session using a dedicated `nanzi-deploy` account. The account may invoke one root-owned release wrapper with a fixed release archive path. The wrapper backs up, deploys, verifies health, and rolls back on failed health checks. A second workflow job uploads `miniprogram/` through `miniprogram-ci` only after the API job succeeds.

**Tech Stack:** GitHub Actions, OpenSSH, Bash, Ubuntu systemd/Nginx, Django tests, Node test runner, WeChat `miniprogram-ci`.

## Global Constraints

- Trigger only from `release` and manual `workflow_dispatch`; never on arbitrary pull requests.
- Never store `DEPLOY_*` or `WECHAT_*` secrets in Git, generated archives, or logs.
- Do not start, stop, delete, or modify `nanzi-ai.service`.
- Do not run content-import commands in the release workflow.
- Auto-upload a WeChat experience build only; do not submit or publish the WeChat release.
- Do not execute destructive database migrations in this release path.

---

### Task 1: Prepare release-safe server wrappers and limited deployment account

**Files:**
- Create: `deploy/scripts/github-release.sh`
- Create: `deploy/scripts/bootstrap-github-deploy-user.sh`
- Modify: `deploy/scripts/deploy.sh`
- Modify: `deploy/scripts/rollback.sh`
- Test: `deploy/tests/test_github_release_files.sh`

**Interfaces:**
- Consumes: `/tmp/nanzi-travel-release-<commit>.tar.gz` uploaded by Actions.
- Produces: `sudo /usr/local/sbin/nanzi-github-release /tmp/nanzi-travel-release-<commit>.tar.gz <commit>` for the `nanzi-deploy` Linux account.
- Produces: `RELEASE_DIR=/opt/nanzi-travel/releases/<timestamp>` in wrapper output, with no secret values.

- [ ] **Step 1: Write failing shell assertions for restricted paths and the wrapper contract**

Create `deploy/tests/test_github_release_files.sh`:

```bash
#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/../.." && pwd)"
grep -q 'nanzi-github-release' "$root/deploy/scripts/bootstrap-github-deploy-user.sh"
grep -q 'tar -xzf' "$root/deploy/scripts/github-release.sh"
grep -q 'rollback.sh' "$root/deploy/scripts/github-release.sh"
grep -q 'nanzi-ai.service' "$root/deploy/scripts/bootstrap-github-deploy-user.sh" && exit 1 || true
```

- [ ] **Step 2: Run it and verify it fails because the scripts do not exist**

Run: `bash deploy/tests/test_github_release_files.sh`

Expected: non-zero exit due to missing scripts.

- [ ] **Step 3: Implement a root-owned release wrapper**

`github-release.sh` must validate all of the following before deployment:

```bash
[[ "${EUID}" -eq 0 ]]
[[ "$archive" == /tmp/nanzi-travel-release-*.tar.gz ]]
[[ -f "$archive" ]]
[[ "$commit" =~ ^[0-9a-f]{7,40}$ ]]
```

Extract to `mktemp -d /tmp/nanzi-travel-release-XXXXXX`, run `backup.sh`, then `deploy.sh "$source_dir"`. Request `http://127.0.0.1:8001/healthz`; if it fails, invoke `rollback.sh`, request the same health endpoint again, return non-zero, and leave the temporary source directory only until the workflow completes. Print only the release/backup paths and commit.

- [ ] **Step 4: Implement the account bootstrap script**

Create a `nanzi-deploy` account with `/usr/sbin/nologin`, an SSH authorized-keys directory, and a root-owned `/usr/local/sbin/nanzi-github-release` copied from `github-release.sh` with mode `0750`. Install `/etc/sudoers.d/nanzi-deploy` mode `0440` containing exactly:

```text
nanzi-deploy ALL=(root) NOPASSWD: /usr/local/sbin/nanzi-github-release /tmp/nanzi-travel-release-*.tar.gz [0-9a-f]*
```

Do not grant wildcard `sudo`, shell, systemctl, or access to `/etc/nanzi-travel`.

- [ ] **Step 5: Keep the release script compatible with the wrapper source directory**

Ensure `deploy.sh` continues to receive a repository root containing `backend/`; do not add data imports. Ensure `rollback.sh` preserves its existing default rollback-to-previous-release behavior.

- [ ] **Step 6: Run static tests**

Run: `bash deploy/tests/test_github_release_files.sh && bash deploy/tests/test_deploy_files.sh`

Expected: exit 0.

- [ ] **Step 7: Commit server release foundation**

```bash
git add deploy/scripts deploy/tests
git commit -m "feat: add restricted GitHub release wrapper"
```

### Task 2: Add CI test and server deployment workflow

**Files:**
- Create: `.github/workflows/release.yml`
- Create: `.github/workflows/tests.yml`
- Test: `.github/workflows/release.yml` via `actionlint`

**Interfaces:**
- Consumes GitHub secrets `DEPLOY_HOST`, `DEPLOY_USER`, `DEPLOY_SSH_PRIVATE_KEY`.
- Consumes the `nanzi-github-release` sudo wrapper from Task 1.
- Produces a GitHub deployment log with commit, backup/release paths, and HTTP health result.

- [ ] **Step 1: Write failing workflow validation**

Add a repository script assertion in `deploy/tests/test_github_release_files.sh`:

```bash
grep -q '^name: Release' "$root/.github/workflows/release.yml"
grep -q 'concurrency:' "$root/.github/workflows/release.yml"
grep -q 'DEPLOY_SSH_PRIVATE_KEY' "$root/.github/workflows/release.yml"
grep -q 'curl --fail.*healthz' "$root/.github/workflows/release.yml"
```

- [ ] **Step 2: Run the assertion and verify it fails**

Run: `bash deploy/tests/test_github_release_files.sh`

Expected: non-zero exit because the workflow does not exist.

- [ ] **Step 3: Implement `.github/workflows/tests.yml`**

Run on pull requests and pushes to `release`:

```yaml
- run: node --test miniprogram/tests/*.test.js
- run: |
    cd backend
    python -m pip install --requirement requirements.lock
    python manage.py test catalog.tests -v 1
    python manage.py check
```

- [ ] **Step 4: Implement the API deployment job**

In `.github/workflows/release.yml`, trigger on `push.branches: [release]` and `workflow_dispatch`; set `concurrency.group: nanzi-production-release`. Repeat the Task 2 tests before deployment. Create `nanzi-travel-release-${{ github.sha }}.tar.gz` with `git archive`. Use an SSH agent populated from `DEPLOY_SSH_PRIVATE_KEY`, copy archive to `/tmp/`, then execute:

```bash
sudo /usr/local/sbin/nanzi-github-release \
  /tmp/nanzi-travel-release-${GITHUB_SHA}.tar.gz "${GITHUB_SHA}"
curl --fail --retry 5 --retry-delay 2 https://api.nanzitravel.com/healthz
```

Mask all secrets. Do not print SSH configuration or secret names with values.

- [ ] **Step 5: Validate workflow syntax**

Run: `actionlint .github/workflows/tests.yml .github/workflows/release.yml`.

Expected: exit 0. If `actionlint` is unavailable, install it only in the CI job and run the shell static tests locally.

- [ ] **Step 6: Commit CI and API deployment workflow**

```bash
git add .github deploy/tests
git commit -m "ci: deploy verified release branch automatically"
```

### Task 3: Upload WeChat experience builds after API deployment succeeds

**Files:**
- Create: `scripts/upload-wechat-experience.mjs`
- Modify: `miniprogram/package.json`
- Modify: `.github/workflows/release.yml`
- Modify: `.gitignore`
- Test: `miniprogram/tests/upload-wechat-experience.test.js`

**Interfaces:**
- Consumes environment variables `WECHAT_APPID`, `WECHAT_PRIVATE_KEY_PATH`, `GITHUB_RUN_NUMBER`, and `GITHUB_SHA`.
- Produces a `miniprogram-ci upload` invocation with version `0.1.<run number>` and description `release <short sha>`.
- Never invokes WeChat submit-audit or release APIs.

- [ ] **Step 1: Write a failing upload configuration test**

Create `miniprogram/tests/upload-wechat-experience.test.js` that imports `buildUploadConfig` and verifies:

```js
assert.deepEqual(
  buildUploadConfig({appid: "wx123", privateKeyPath: "/tmp/key", runNumber: "17", sha: "abc123def"}),
  {appid: "wx123", privateKeyPath: "/tmp/key", version: "0.1.17", desc: "release abc123d"},
);
```

- [ ] **Step 2: Run it and verify it fails**

Run: `node --test miniprogram/tests/upload-wechat-experience.test.js`

Expected: fail because `buildUploadConfig` does not exist.

- [ ] **Step 3: Implement the minimal upload script and package dependency**

Add `miniprogram-ci` as a development dependency in `miniprogram/package.json`. Implement `buildUploadConfig` and an executable path that validates all required environment variables, loads the private key from a temporary file, then calls `ci.upload({project: 'miniprogram', ...config})`. Do not write the key under the repository tree.

- [ ] **Step 4: Extend the release workflow with a dependent upload job**

Set `needs: deploy-api`. In GitHub Actions, write `${{ secrets.WECHAT_PRIVATE_KEY }}` to a `mktemp` file with mode `0600`, run `npm install` in `miniprogram/`, invoke the script, and delete the temporary key using an `always()` cleanup step. The upload job must not run when `deploy-api` fails.

- [ ] **Step 5: Verify behavior locally**

Run: `node --test miniprogram/tests/*.test.js`.

Expected: all tests pass. Do not run a real upload locally.

- [ ] **Step 6: Commit WeChat experience upload automation**

```bash
git add miniprogram scripts .github .gitignore
git commit -m "ci: upload WeChat experience build after deployment"
```

### Task 4: Configure secrets and perform a controlled production rehearsal

**Files:**
- Create: `docs/deployment/github-actions-setup.md`
- Modify: `README.md` if it exists
- Test: GitHub Actions manual `workflow_dispatch` run

**Interfaces:**
- Requires the user to enter five GitHub Actions secrets in repository settings.
- Requires the user to add the generated SSH public key to `/home/nanzi-deploy/.ssh/authorized_keys` on the server through a root session.
- Produces an auditable successful GitHub Actions run and a visible WeChat experience version.

- [ ] **Step 1: Document exact manual setup steps without secret values**

Document: create private GitHub repository; add remote; create `release`; create an ed25519 key pair only for deployment; server root runs `CONFIRM_GITHUB_DEPLOY_USER=1 deploy/scripts/bootstrap-github-deploy-user.sh`; add public key; add the five Secrets; generate WeChat upload private key from the WeChat public platform; configure the AppID secret.

- [ ] **Step 2: Add GitHub repository secrets**

In GitHub repository Settings → Secrets and variables → Actions, add `DEPLOY_HOST`, `DEPLOY_USER=nanzi-deploy`, `DEPLOY_SSH_PRIVATE_KEY`, `WECHAT_APPID`, and `WECHAT_PRIVATE_KEY`. Confirm each secret name appears only in the workflow, never in tracked files as a value.

- [ ] **Step 3: Run a manual rehearsal from the Actions page**

Use `workflow_dispatch` for `release`. Verify in order: tests pass; backup directory is created; a new `/opt/nanzi-travel/releases/` directory becomes current; `https://api.nanzitravel.com/healthz` returns `{"status":"ok"}`; a new WeChat experience build appears with the commit identifier.

- [ ] **Step 4: Test safe failure handling**

On a short-lived non-release branch, intentionally fail a test and verify the test workflow fails without any server deploy job. Do not use a deliberately broken production deployment as a test.

- [ ] **Step 5: Commit the setup guide**

```bash
git add docs/deployment README.md
git commit -m "docs: explain GitHub Actions release setup"
```

## Plan Self-Review

- Spec coverage: Tasks 1–2 cover test gate, backup, deployment, serialized runs, health check, and rollback. Task 3 covers only experience uploads. Task 4 covers account/secrets setup and controlled validation.
- No content import appears in any task.
- No workflow invokes WeChat audit submission or official release.
- Server account permissions are limited to a root-owned fixed command; no root key or root login is required by GitHub Actions.
