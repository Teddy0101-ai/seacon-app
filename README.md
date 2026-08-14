# 航运特训 · Seacon

《主流船型必须搞懂的知识白皮书》v2.1 的学习 App。

## 当前状态

- 旧题库已于 2026-08-14 全部删除，当前题目数为 **0**。
- 保留 **11 个单元 / 56 节课**的多邻国式学习路径骨架，所有课程节点暂时禁用。
- 保留 **392 条术语速查**，支持中文、英文、缩写、别名和类别筛选。
- 旧设备中的完成记录、错题和间隔复习记录会在打开新版时自动失效。
- 纯静态 PWA，可安装到 iPhone 主屏并离线使用。

删除范围包括原 `build_data.py` 内的全部题目、原 `content_v21.py` 补充题库以及生成后的 `data.js` 题目数据。Git 历史仍可追溯旧版本，但当前源码和线上构建不会重新带出旧题。

## 文件结构

```text
seacon-app/
├─ index.html              页面骨架
├─ app.css                 样式
├─ app.js                  路径、空题库状态、术语搜索
├─ data.js                 课程路径构建产物（0 道题）
├─ terms.js                术语库构建产物
├─ terms_v2.json           白皮书原始术语
├─ terms_v21.py            v2.1 术语补充、去重与别名
├─ build_data.py           生成 11 单元 / 56 节空路径
├─ build_assets.py         生成术语、PWA 清单、缓存与图标
├─ manifest.webmanifest    PWA 清单
├─ sw.js                   Service Worker
├─ vercel.json             Vercel 配置
└─ icons/                  应用图标
```

## 本地构建

```bash
python build_data.py
python build_assets.py
```

`build_data.py` 带有硬断言：当前清空版本只要出现任何题目就会构建失败，避免旧题误回线上。

## 部署

仓库是纯静态项目，Vercel Framework Preset 选择 `Other`，Build Command 和 Output Directory 均留空。推送到 GitHub `main` 后由 Vercel 自动部署。

每次修改 `index.html`、`app.css`、`app.js`、`data.js` 或 `terms.js` 后，都要重新运行 `build_assets.py`，让 Service Worker 缓存版本号更新。

## 下一步重新出题

重新设计题目时，应直接重写 `build_data.py` 的课程内容，不要恢复旧题库文件。先确定每节课的明确学习目标、前置知识和通关标准，再开始写题；旧版 Git 历史只用于查错，不作为新题素材默认复用。
