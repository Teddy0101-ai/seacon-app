// 航运特训 · 离线缓存（版本号由构建脚本按内容哈希生成，改代码自动失效旧缓存）
const V = 'seacon-drill-13185d92e9';
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
