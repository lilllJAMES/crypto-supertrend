# crypto-supertrend
多币种趋势网页
[architecture_report.html](https://github.com/user-attachments/files/24725999/architecture_report.html)
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>架构设计报告 - Crypto SuperTrend</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <style>
        :root {
            --bg-color: #0d1117;
            --card-bg: #161b22;
            --text-main: #c9d1d9;
            --text-muted: #8b949e;
            --accent: #58a6ff;
            --border: #30363d;
            --success: #238636;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-main);
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
            padding: 40px 20px;
        }
        h1, h2, h3 { color: #fff; margin-top: 1.5em; }
        h1 { border-bottom: 1px solid var(--border); padding-bottom: 10px; }
        
        .card {
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
        }
        
        .badge {
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 8px;
        }
        .badge.python { background: #3776ab; color: white; }
        .badge.vue { background: #42b883; color: #35495e; }
        .badge.flask { background: #000; color: white; border: 1px solid #fff; }

        code {
            background: rgba(110, 118, 129, 0.4);
            padding: 0.2em 0.4em;
            border-radius: 6px;
            font-family: ui-monospace, SFMono-Regular, SF Mono, Menlo, Consolas, Liberation Mono, monospace;
        }

        .analogy-box {
            background: rgba(56, 139, 253, 0.1);
            border-left: 4px solid #58a6ff;
            padding: 16px;
            margin: 20px 0;
        }
        .analogy-title { font-weight: bold; color: #58a6ff; margin-bottom: 8px; display: block; }

        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 768px) { .grid-2 { grid-template-columns: 1fr; } }

        .flow-step {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .step-num {
            background: var(--accent);
            color: white;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 12px;
            font-size: 0.85em;
            font-weight: bold;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🏛️ 软件架构设计报告</h1>
            <p style="color: var(--text-muted);">Crypto SuperTrend Dashboard - 前后端分离重构版</p>
        </header>

        <!-- 1. 核心架构图 -->
        <section>
            <h2>1. 系统全景图</h2>
            <div class="card" style="text-align: center;">
                <div class="mermaid">
                graph LR
                    subgraph Client["🖥️ 前端 (浏览器)"]
                        Vue[Vue.js 页面]
                        User[用户交互]
                    end

                    subgraph Server["⚙️ 后端 (Python/Flask)"]
                        API[API 接口<br/>(Port 8001)]
                        Logic[业务逻辑]
                        Cache[(内存缓存)]
                    end

                    subgraph External["☁️ 外部服务"]
                        OKX[OKX 交易所]
                    end

                    User -->|打开页面| Vue
                    Vue -->|HTTP 请求| API
                    API -->|读取| Cache
                    Logic -->|后台定时抓取| OKX
                    Logic -->|计算指标| Cache
                </div>
                <p style="color: var(--text-muted); font-size: 0.9em; margin-top: 10px;">
                    系统采用经典的 <strong>Client-Server</strong> 架构，数据计算与界面展示完全解耦。
                </p>
            </div>
        </section>

        <!-- 2. 关键疑问解答 -->
        <section>
            <h2>2. 核心疑问解答</h2>
            <div class="card">
                <h3>Q: 为什么要启动 HTTP 服务器 (Port 8001)？</h3>
                <p>这就是你刚才问到的关键点。简单来说，它是连接“后台计算”和“前台展示”的<strong>唯一通道</strong>。</p>
                
                <div class="analogy-box">
                    <span class="analogy-title">🍽️ 餐厅比喻法</span>
                    <p><strong>Python 后端 = 厨房</strong>：厨师在里面疯狂炒菜（计算 SuperTrend 指标），虽然菜做好了，放在厨房桌上（内存 Cache），但外面的客人是拿不到的。</p>
                    <p><strong>Port 8001 = 传菜窗口</strong>：启动 HTTP 服务器，就等于打开了传菜窗口。只有窗口开了，服务员（API）才能把做好的菜（JSON 数据）递给外面的顾客（前端页面）。</p>
                </div>

                <div class="flow-step">
                    <div class="step-num">1</div>
                    <div><strong>监听 (Listen)</strong>: Python 程序守在 8001 端口，等待请求。</div>
                </div>
                <div class="flow-step">
                    <div class="step-num">2</div>
                    <div><strong>路由 (Route)</strong>: 收到 <code>/api/dashboard</code> 请求，知道要给数据。</div>
                </div>
                <div class="flow-step">
                    <div class="step-num">3</div>
                    <div><strong>响应 (Respond)</strong>: 把 Python 的字典数据转成 JSON 格式发出去。</div>
                </div>
            </div>
        </section>

        <!-- 3. 全栈技术详解 -->
        <section>
            <h2>3. 全栈技术详解 (Tech Stack Deep Dive)</h2>
            <p style="color: var(--text-muted); margin-bottom: 20px;">
                本项目融合了五大核心技术，从底层数据计算到顶层用户交互，各司其职。
            </p>
            
            <!-- Python -->
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0; color: #3572A5;">🐍 Python</h3>
                    <span class="badge python">后端核心</span>
                </div>
                <div class="grid-2">
                    <div>
                        <h4 style="color: #fff; font-size: 0.9em;">📚 基础知识</h4>
                        <p style="font-size: 0.9em; color: var(--text-muted);">
                            一种解释型、面向对象的高级编程语言。以其简洁的语法和强大的库支持（特别是数据分析领域）而闻名。
                        </p>
                    </div>
                    <div>
                        <h4 style="color: #fff; font-size: 0.9em;">🏗️ 项目中的作用</h4>
                        <ul style="font-size: 0.9em; color: var(--text-muted); padding-left: 20px;">
                            <li><strong>数据大脑</strong>：负责所有复杂的逻辑运算。</li>
                            <li><strong>API 服务</strong>：通过 Flask 框架搭建 Web 服务器 (Port 8001)。</li>
                            <li><strong>量化计算</strong>：利用 <code>Pandas</code> 计算 SuperTrend 指标。</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- HTML/CSS -->
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0; color: #e34c26;">🌐 HTML5 & CSS3</h3>
                    <span class="badge" style="background: #563d7c; color: white;">骨架与皮肤</span>
                </div>
                <div class="grid-2">
                    <div>
                        <h4 style="color: #fff; font-size: 0.9em;">📚 基础知识</h4>
                        <p style="font-size: 0.9em; color: var(--text-muted);">
                            <strong>HTML</strong> 是网页的骨架，定义了内容结构（标题、表格）。<br>
                            <strong>CSS</strong> 是网页的皮肤，负责排版、颜色、动画和响应式布局。
                        </p>
                    </div>
                    <div>
                        <h4 style="color: #fff; font-size: 0.9em;">🏗️ 项目中的作用</h4>
                        <ul style="font-size: 0.9em; color: var(--text-muted); padding-left: 20px;">
                            <li><strong>HTML</strong>：构建了仪表盘的表格结构 (<code>&lt;table&gt;</code>) 和控制按钮。</li>
                            <li><strong>CSS</strong>：实现了深色模式 (Dark Mode) 和响应式网格布局，以及红绿涨跌色的视觉反馈。</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- JavaScript -->
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0; color: #f1e05a;">⚡ JavaScript (JS)</h3>
                    <span class="badge" style="background: #f1e05a; color: black;">交互逻辑</span>
                </div>
                <div class="grid-2">
                    <div>
                        <h4 style="color: #fff; font-size: 0.9em;">📚 基础知识</h4>
                        <p style="font-size: 0.9em; color: var(--text-muted);">
                            Web 开发的脚本语言，运行在浏览器中。它让静态网页“活”起来，可以处理用户点击、发送网络请求、修改页面内容。
                        </p>
                    </div>
                    <div>
                        <h4 style="color: #fff; font-size: 0.9em;">🏗️ 项目中的作用</h4>
                        <ul style="font-size: 0.9em; color: var(--text-muted); padding-left: 20px;">
                            <li><strong>搬运工</strong>：使用 <code>fetch()</code> 从 Python 后端拉取数据。</li>
                            <li><strong>翻译官</strong>：将后端数据格式 (15m/1H) 转换为前端格式。</li>
                            <li><strong>绘图师</strong>：动态计算并绘制 SVG 迷你走势图 (Sparkline)。</li>
                        </ul>
                    </div>
                </div>
            </div>

            <!-- Vue.js -->
            <div class="card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <h3 style="margin: 0; color: #42b883;">💚 Vue.js</h3>
                    <span class="badge vue">MVVM 框架</span>
                </div>
                <div class="grid-2">
                    <div>
                        <h4 style="color: #fff; font-size: 0.9em;">📚 基础知识</h4>
                        <p style="font-size: 0.9em; color: var(--text-muted);">
                            一个渐进式 JavaScript 框架。核心特性是<strong>响应式数据绑定</strong>：数据变了，界面自动更新，无需手动操作 DOM。
                        </p>
                    </div>
                    <div>
                        <h4 style="color: #fff; font-size: 0.9em;">🏗️ 项目中的作用</h4>
                        <ul style="font-size: 0.9em; color: var(--text-muted); padding-left: 20px;">
                            <li><strong>双向绑定</strong>：将 <code>coins</code> 数组直接映射到 HTML 表格。</li>
                            <li><strong>即时响应</strong>：点击“看涨”按钮时，Vue 自动重新渲染列表，无需刷新页面。</li>
                            <li><strong>组件化</strong>：<code>&lt;trend-badge&gt;</code> 组件复用了趋势标签的代码。</li>
                        </ul>
                    </div>
                </div>
            </div>
        </section>

        <!-- 4. 数据流转逻辑 -->
        <section>
            <h2>4. 数据流转全过程</h2>
            <div class="card">
                <ol style="color: var(--text-main);">
                    <li><strong>启动阶段</strong>：运行 <code>start_server.bat</code>，配置代理，启动 Flask 服务器。</li>
                    <li><strong>后台抓取</strong>：后台线程每 150 秒醒来一次，并发请求 OKX 接口获取最新 K 线。</li>
                    <li><strong>计算落库</strong>：计算出每个币种在 15m/1H/4H/1D 的趋势，存入 <code>CACHE</code> 变量。</li>
                    <li><strong>前端请求</strong>：用户打开浏览器，Vue 应用每隔几秒询问一次 <code>http://localhost:8001/api/dashboard</code>。</li>
                    <li><strong>展示渲染</strong>：前端拿到 JSON 数据，映射成表格，画出迷你走势图。</li>
                </ol>
            </div>
        </section>
        
        <footer style="text-align: center; margin-top: 40px; color: var(--text-muted); font-size: 0.8em;">
            Generated by Trae AI Pair Programmer
        </footer>
    </div>

    <script>
        mermaid.initialize({ 
            startOnLoad: true, 
            theme: 'dark',
            securityLevel: 'loose'
        });
    </script>
</body>
</html>
