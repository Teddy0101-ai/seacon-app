# -*- coding: utf-8 -*-
"""生成 terms.js / manifest / sw.js / 图标 / vercel.json。"""
import io, json, os
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
# 术语库：优先用仓库内的副本，找不到再回退到白皮书项目目录
CAND = [os.path.join(HERE, "terms_v2.json"),
        os.path.join(HERE, "..", "seacon-shipping-whitepaper", "terms_v2.json")]
SCR = next((p for p in CAND if os.path.exists(p)), None)
if not SCR:
    raise SystemExit("找不到 terms_v2.json，请把它放在本目录下")
T = json.load(io.open(SCR, encoding="utf-8"))

# ── terms.js：只保留 App 用得到的字段 ────────────────────────
# 内容为全量（含公司船队与项目信息）——经内容所有者确认后放行。
# 若将来需要做公开版，把下面 BLOCK 填上关键词即可自动剔除相关句子。
BLOCK = ()
slim = []
for t in T:
    d = dict(t)
    if BLOCK:
        for k in ("d", "n", "u"):
            if d.get(k) and any(b in d[k] for b in BLOCK):
                d[k] = "。".join([s for s in d[k].split("。")
                                  if not any(b in s for b in BLOCK)]).strip("。")
                if d[k]: d[k] += "。"
                else: d.pop(k, None)
    o = {"t": d["t"], "c": d["c"]}
    for k in ("en", "cn", "d", "n", "u"):
        if d.get(k): o[k] = d[k]
    slim.append(o)
io.open(os.path.join(HERE, "terms.js"), "w", encoding="utf-8").write(
    "window.TERMS=" + json.dumps(slim, ensure_ascii=False, separators=(",", ":")) + ";")

# ── manifest ────────────────────────────────────────────────
manifest = {
    "name": "航运特训 · Seacon", "short_name": "航运特训",
    "description": "航运投资知识特训——分模块闯关，快速掌握船型、租约、保险、周期与测算。",
    "start_url": ".", "scope": ".", "display": "standalone",
    "orientation": "portrait", "background_color": "#ffffff", "theme_color": "#0b5c8a",
    "lang": "zh-CN", "categories": ["education", "productivity"],
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "icons/icon-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}
    ]
}
io.open(os.path.join(HERE, "manifest.webmanifest"), "w", encoding="utf-8").write(
    json.dumps(manifest, ensure_ascii=False, indent=2))

# ── Service Worker：离线可用 ─────────────────────────────────
# 缓存名必须随内容变化，否则改了代码用户还是拿到旧文件（本地实测踩过）
import hashlib
_h = hashlib.sha1()
for _f in ("index.html", "app.css", "app.js", "data.js", "terms.js"):
    _p = os.path.join(HERE, _f)
    if os.path.exists(_p):
        _h.update(io.open(_p, "rb").read())
VER = _h.hexdigest()[:10]

SW = """// 航运特训 · 离线缓存（版本号由构建脚本按内容哈希生成，改代码自动失效旧缓存）
const V = 'seacon-drill-%s';""" % VER + """
const FILES = ['./','./index.html','./app.css','./app.js','./data.js','./terms.js',
               './manifest.webmanifest','./icons/icon-192.png','./icons/icon-512.png',
               './icons/apple-touch-icon.png'];
self.addEventListener('install', e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(ks =>
    Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request).then(hit => hit || fetch(e.request).then(res => {
      const copy = res.clone();
      caches.open(V).then(c => c.put(e.request, copy)).catch(() => {});
      return res;
    }).catch(() => caches.match('./index.html')))
  );
});
"""
io.open(os.path.join(HERE, "sw.js"), "w", encoding="utf-8").write(SW)

# ── 图标：深蓝底 + 金色船体剖面（和白皮书同一套视觉语言）────────
def icon(px, maskable=False):
    im = Image.new("RGBA", (px, px), (11, 42, 69, 255))
    d = ImageDraw.Draw(im)
    s = px / 512.0
    pad = 0.18 if maskable else 0.0          # maskable 要留安全区
    k = 1 - pad * 2
    def X(v): return (pad + v / 512.0 * k) * px
    def Y(v): return (pad + v / 512.0 * k) * px
    # 水线
    d.rectangle([X(0), Y(330), X(512), Y(512)], fill=(29, 90, 134, 255))
    for i, yy in enumerate((352, 392, 432)):
        w = 190 - i * 30
        d.rounded_rectangle([X(256 - w), Y(yy), X(256 + w), Y(yy + 10 * s + 6)],
                            radius=6 * s, fill=(60, 130, 175, 255))
    # 船体（水线以上灰蓝、以下金色 —— 对应白皮书的红/灰双色壳）
    hull = [(X(96), Y(232)), (X(416), Y(232)), (X(392), Y(330)),
            (X(150), Y(330)), (X(120), Y(300))]
    d.polygon(hull, fill=(200, 163, 73, 255))
    d.rectangle([X(96), Y(232), X(416), Y(258)], fill=(236, 240, 243, 255))
    # 上层建筑 + 烟囱
    d.rounded_rectangle([X(130), Y(150), X(210), Y(232)], radius=8 * s, fill=(236, 240, 243, 255))
    d.rounded_rectangle([X(152), Y(96), X(186), Y(150)], radius=6 * s, fill=(200, 163, 73, 255))
    # 桅杆
    d.rectangle([X(330), Y(120), X(342), Y(232)], fill=(236, 240, 243, 255))
    return im

for px, name in ((192, "icon-192.png"), (512, "icon-512.png"), (180, "apple-touch-icon.png")):
    icon(px).save(os.path.join(HERE, "icons", name))
icon(512, True).save(os.path.join(HERE, "icons", "icon-maskable.png"))

# ── vercel.json ─────────────────────────────────────────────
vercel = {
    "$schema": "https://openapi.vercel.sh/vercel.json",
    "cleanUrls": True,
    "headers": [
        {"source": "/sw.js",
         "headers": [{"key": "Cache-Control", "value": "public, max-age=0, must-revalidate"}]},
        {"source": "/(.*)",
         "headers": [{"key": "X-Content-Type-Options", "value": "nosniff"},
                     {"key": "Referrer-Policy", "value": "no-referrer"},
                     {"key": "X-Frame-Options", "value": "SAMEORIGIN"}]}
    ]
}
io.open(os.path.join(HERE, "vercel.json"), "w", encoding="utf-8").write(
    json.dumps(vercel, ensure_ascii=False, indent=2))

print("terms.js  %d 条 / %.1f KB" % (len(slim), os.path.getsize(os.path.join(HERE, "terms.js")) / 1024))
for f in ("manifest.webmanifest", "sw.js", "vercel.json"):
    print("%-22s %.1f KB" % (f, os.path.getsize(os.path.join(HERE, f)) / 1024))
for f in os.listdir(os.path.join(HERE, "icons")):
    print("icons/%-16s %.1f KB" % (f, os.path.getsize(os.path.join(HERE, "icons", f)) / 1024))
