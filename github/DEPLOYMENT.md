# 部署指南 (Deployment Guide)

本项目分为 **前端 (Frontend)** 和 **后端 (Backend)** 两部分，需要分别部署。

## 架构说明
- **前端 (client/)**: 纯静态网页 (HTML/JS/CSS)。部署在 **GitHub Pages**。
- **后端 (backend/)**: Python Flask 应用。部署在 **Render** (免费容器服务)。

---

## 第一步：上传代码到 GitHub
1. 在 GitHub 创建一个新的仓库 (Repository)。
2. 将本地代码推送到该仓库。

## 第二步：部署后端 (Render)
1. 注册/登录 [Render.com](https://render.com)。
2. 点击 **New +** -> **Web Service**。
3. 选择 "Build and deploy from a Git repository"，连接你的 GitHub 仓库。
4. 配置如下：
   - **Name**: 随便填 (例如 `supertrend-api`)
   - **Root Directory**: `backend` (非常重要！填 backend)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt` (自动填充)
   - **Start Command**: `gunicorn server:app` (自动填充，或填 `gunicorn server:app --workers 1 --threads 4 --timeout 120`)
   - **Instance Type**: Free
5. 点击 **Create Web Service**。
6. 等待部署完成。你会获得一个 URL，例如 `https://supertrend-api.onrender.com`。
   > **注意**: 免费版 Render 会在 15 分钟无请求后休眠。再次访问时可能需要 1 分钟启动。

## 第三步：连接前后端
1. 打开本地 `client/index.html`。
2. 找到代码中的 `API_URL` 配置项 (约第 375 行)。
3. 将其修改为 Render 提供的 URL：
   ```javascript
   // const API_URL = 'http://localhost:8001/api/dashboard'; // 本地
   const API_URL = 'https://你的项目名.onrender.com/api/dashboard'; // 线上
   ```
4. 保存并提交代码 (Commit & Push) 到 GitHub。

## 第四步：部署前端 (GitHub Pages)
1. 打开你的 GitHub 仓库页面。
2. 进入 **Settings** -> **Pages**。
3. 在 **Build and deployment** 下：
   - **Source**: Deploy from a branch
   - **Branch**: `main` (或 master), 文件夹选择 `/ (root)`
4. 点击 **Save**。
5. 等待几分钟，GitHub 会生成一个链接，例如 `https://你的用户名.github.io/仓库名/`。
6. 你的最终访问地址是：`https://你的用户名.github.io/仓库名/client/` (因为网页在 client 目录下)。

---

## 常见问题
- **数据加载慢？** Render 免费实例会休眠，第一次加载可能需要 50 秒唤醒后端。
- **没有数据？** 检查 `client/index.html` 里的 `API_URL` 是否是 HTTPS，且地址正确。
