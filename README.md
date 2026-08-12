# 航运特训 · Seacon

《主流船型必须搞懂的知识白皮书》的**闯关训练版**。分模块、小步快跑，用来把知识真正记住。

- **9 个单元 / 32 节课 / 117 道题** — 每节 3—6 题，一次 2 分钟
- 题型：判断、选择、填空、配对
- **344 条术语速查**，中英文都能搜
- 答错自动进**错题本**，答对才移出
- 经验值、连续天数、每日 5 颗心
- **可装到 iPhone 主屏当原生 App，断网也能用**

零构建、零依赖、纯静态。没有后端，没有任何网络请求，进度全部存在本机浏览器里。

---

## 一、部署到 Vercel

本仓库是**纯静态**的，不需要任何构建步骤。

1. 打开 <https://vercel.com/new>
2. 在 **Import Git Repository** 里找到 `Teddy0101-ai/seacon-app`，点 **Import**
   - 第一次用要先点 **Adjust GitHub App Permissions** 授权 Vercel 访问这个仓库
3. 三项设置：

   | 项 | 填什么 |
   |---|---|
   | Framework Preset | **Other** |
   | Build Command | **留空**（把 Override 开关关掉） |
   | Output Directory | **留空** |

4. 点 **Deploy**

一分钟出 `https://xxx.vercel.app`。

**之后每次 `git push`，Vercel 会自动重新部署**——这是选 GitHub 而不是拖拽的唯一理由，但也是最重要的理由。

### 更新内容的完整流程

```bash
# 1. 改题目
#    编辑 build_data.py

# 2. 重新生成（两个都要跑，缺一不可）
python build_data.py
python build_assets.py

# 3. 推上去，Vercel 自动部署
git add -A && git commit -m "更新题库" && git push
```

---

## 二、装到 iPhone 主屏

1. 用 **Safari**（必须是 Safari，Chrome 不行）打开部署好的网址
2. 点底部中间的**分享**按钮 ⬆️
3. 往下滑，选**「添加到主屏幕」**
4. 完成

之后从主屏图标进入就是**全屏模式**——没有地址栏、没有浏览器按钮，和原生 App 一样。
第一次打开后会自动缓存，**之后断网也能用**。

---

## 三、⚠️ 部署前必读：这是公开的

**Vercel 免费版部署出来的网址是公开的，任何人拿到链接都能打开。**

这个 App 已经做了处理：
- **不含**公司未公开的船队逐船明细、代表项目船名与合同金额
- 术语库在构建时会自动剔除含内部项目信息的句子（见 `build_assets.py` 的 `BLOCK` 列表）
- 案例里的市场数字（日租金、OPEX、船价、运费率）均为**示意值**

如果之后要加入内部数据，**必须先解决访问控制**，可选：
- Vercel 的 Password Protection / Vercel Authentication（Pro 计划功能）
- 或部署到公司内网

---

## 四、文件结构

```
seacon-app/
├─ index.html              页面骨架
├─ app.css                 样式
├─ app.js                  逻辑（闯关引擎、错题本、术语搜索）
├─ data.js                 课程题库（构建产物）
├─ terms.js                术语库（构建产物）
├─ manifest.webmanifest    PWA 清单
├─ sw.js                   Service Worker（离线缓存）
├─ vercel.json             部署配置与响应头
├─ icons/                  应用图标
├─ build_data.py           生成 data.js
└─ build_assets.py         生成 terms.js / manifest / sw.js / 图标
```

---

## 五、改内容

**改题目** → 编辑 `build_data.py`，然后：

```bash
python build_data.py
python build_assets.py     # 必须一起跑，见下方说明
```

题型写法：

```python
tf("这句话对不对？", 1, "解释")                      # 判断：1=对 0=错
mc("问题？", ["选项A","选项B","选项C"], 1, "解释")    # 选择：最后一个数是正确选项的下标
bank("句子里挖 ___ 空", ["A","B","C"], 2, "解释")     # 填空
pair([["左1","右1"],["左2","右2"]], "提示")           # 配对
```

**改术语** → 改白皮书那边的 `terms_v2.json`，再跑 `build_assets.py`。

> **⚠️ 每次改完代码都必须重跑 `build_assets.py`。**
> Service Worker 的缓存版本号是按文件内容哈希生成的——不重跑，用户浏览器会一直用旧缓存，
> 你改的东西不会生效。这个坑本地实测踩过。

---

## 六、怎么练最有效

- **每天一节，连续比时长重要。** 32 节课够刷一个月。
- **答错不要跳过。** 错题本里的题才是你真正的知识边界。
- 一个单元刷完，回头把错题清一遍，比从头重刷一遍效率高得多。
- 术语忘了直接去「术语」页搜，不用回头翻课。

顺序建议：先做**单元 1（先认人）**——不先把船东、租家、货主、船级社这些角色分清楚，
后面的单元会一直卡。

---

Seacon Shipping / GVMI · 内部培训用
内容源自《主流船型必须搞懂的知识白皮书》v2.0
