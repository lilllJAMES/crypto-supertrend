# Crypto SuperTrend Monitor (250 Coins Edition)

这是一个基于 **Python (Flask)** 后端和 **Vue.js 3** 前端的实时加密货币趋势监控系统。它能够监控市值排名前 **250** 的加密货币，并计算它们在不同时间周期（15m, 1H, 4H, 1D）的 SuperTrend 指标。

![Dashboard Preview](https://via.placeholder.com/800x400?text=Dashboard+Preview)

## ✨ 功能特点

*   **大规模监控**: 实时覆盖市值前 **250** 的热门加密货币（基于 CoinCap 市值排序 + OKX 交易量排序）。
*   **多周期趋势**: 同时计算和展示 15分钟、1小时、4小时、1天的 SuperTrend (ATR=10, Multiplier=3) 状态。
*   **智能排序**: 
    *   优先使用 CoinCap API 获取真实市值排名。
    *   自动将 **BTC (Bitcoin)** 置顶，方便查看大盘风向。
    *   若市值 API 异常，自动降级为按 OKX 24小时成交额排序。
*   **高性能后端**: 
    *   使用 Python `ThreadPoolExecutor` (10线程) 并发抓取数据。
    *   内置内存缓存 (In-Memory Cache)，避免频繁请求触发交易所频率限制。
    *   每 180秒 (3分钟) 自动刷新一次数据。
*   **现代化前端**:
    *   纯 Vue.js 3 (CDN 模式)，无需复杂的 Node.js 构建流程。
    *   响应式暗色主题 UI，适配桌面和移动端。
    *   支持按币种名称搜索。
    *   **Sparkline 迷你图**: 直观展示最近 24 小时的价格走势。

## 🛠️ 技术栈

### 后端 (Backend)
*   **语言**: Python 3.11+
*   **框架**: Flask (提供 API 接口)
*   **并发**: `concurrent.futures.ThreadPoolExecutor`
*   **数据处理**: Pandas, NumPy (计算 SuperTrend 和 ATR)
*   **部署**: Gunicorn (生产环境 WSGI 服务器)

### 前端 (Client)
*   **框架**: Vue.js 3 (Composition API)
*   **样式**: 原生 CSS 3 (Grid/Flexbox), 仿 Tailwind 风格
*   **图表**: SVG 迷你趋势图

## 🚀 快速开始

### 1. 本地运行 (Local Development)

**后端启动:**
```bash
cd backend
pip install -r requirements.txt
python server.py
# 服务将运行在 http://localhost:8001
```

**前端启动:**
直接在浏览器中打开 `client/index.html` 即可。
*注意：如果遇到 CORS 跨域问题，请修改 backend/server.py 中的 CORS 设置或使用简单的 HTTP 服务器运行前端。*

### 2. 部署上线 (Deployment)

本项目设计为前后端分离部署：

*   **后端**: 推荐部署到 **Render** (Web Service)。
    *   Build Command: `pip install -r requirements.txt`
    *   Start Command: `gunicorn server:app`
    *   Root Directory: `backend`
*   **前端**: 推荐部署到 **GitHub Pages**。
    *   上传 `client` 目录中的内容。
    *   **重要**: 修改 `client/index.html` 中的 `API_URL` 变量，将其指向你 Render 后端的 URL (例如 `https://your-app.onrender.com/api/dashboard`)。

详细部署教程请参考仓库内的 [DEPLOYMENT.md](DEPLOYMENT.md) 文件。

## 📂 目录结构

```
.
├── backend/                # Python 后端代码
│   ├── server.py           # 核心服务逻辑
│   ├── requirements.txt    # Python 依赖
│   ├── Procfile            # Render 部署配置
│   └── runtime.txt         # Python 版本声明
├── client/                 # 前端代码
│   └── index.html          # 主页面 (Vue App)
├── architecture_report.html # 系统架构说明文档
├── DEPLOYMENT.md           # 详细部署指南
└── README.md               # 项目说明
```

## ⚠️ 免责声明
本项目仅供学习和研究使用，不构成任何投资建议。加密货币市场风险巨大，请自行承担交易风险。
