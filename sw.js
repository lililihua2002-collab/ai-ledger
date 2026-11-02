/* AI 记账 PWA Service Worker v3：HTML 走网络优先（保证更新及时），静态资源缓存优先 */
var CACHE = 'ai-ledger-v3';
var ASSETS = [
  './',
  './index.html',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png',
  './icons/apple-touch-icon.png'
];

self.addEventListener('install', function(e){
  e.waitUntil(caches.open(CACHE).then(function(c){ return c.addAll(ASSETS); }).then(function(){ return self.skipWaiting(); }));
});

self.addEventListener('activate', function(e){
  e.waitUntil(
    caches.keys().then(function(keys){
      return Promise.all(keys.filter(function(k){ return k !== CACHE; }).map(function(k){ return caches.delete(k); }));
    }).then(function(){ return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function(e){
  if(e.request.method !== 'GET') return;
  var url = new URL(e.request.url);
  var isHtml = e.request.mode === 'navigate' || /\.html$/.test(url.pathname) || url.pathname === location.pathname && url.search === '';
  e.respondWith(
    // HTML 网络优先：有新版本立即用新的，失败才回退缓存（保证 App 更新及时送达）
    (isHtml ? fetch(e.request).then(function(res){
      if(res.ok){
        var clone = res.clone();
        caches.open(CACHE).then(function(c){ c.put(e.request, clone); });
      }
      return res;
    }).catch(function(){ return caches.match(e.request).then(function(h){ return h || caches.match('./index.html'); }); })
    // 其他资源缓存优先
    : caches.match(e.request).then(function(hit){
      if(hit) return hit;
      return fetch(e.request).then(function(res){
        if(res.ok){
          var clone = res.clone();
          caches.open(CACHE).then(function(c){ c.put(e.request, clone); });
        }
        return res;
      });
    }))
  );
});
