/* ═══════════════════════════════════════════════════════════
   航运特训 · 逻辑层
   状态全部落在 localStorage，纯前端，无后端、无网络请求
   ═══════════════════════════════════════════════════════════ */
(function () {
"use strict";
var $ = function (s) { return document.querySelector(s); };
var $$ = function (s) { return Array.prototype.slice.call(document.querySelectorAll(s)); };
var C = window.COURSE || [], TERMS = window.TERMS || [];
var KEY = "seacon-drill-v1";

/* ── 状态 ──────────────────────────────────────────────── */
var S = load();
function load() {
  var d = { xp: 0, streak: 0, last: "", done: {}, wrong: [] };
  try { var raw = localStorage.getItem(KEY); if (raw) d = Object.assign(d, JSON.parse(raw)); } catch (e) {}
  return d;
}
function save() { try { localStorage.setItem(KEY, JSON.stringify(S)); } catch (e) {} }
function today() { return new Date().toISOString().slice(0, 10); }

// 心数改成「每节课 5 颗」，不再按天锁死。
// 原来的做法有两个问题：① 每天最多只允许错 5 次，而错误恰恰是学习价值最高的事件；
// ② 心数归零后 run.hp 一直是 0，即使全部答对也过不了任何一节课，App 到第二天才能用。
// 现在错误的代价改成「当场回炉多做两遍」——这既不砖掉 App，又把重复放在了正确的位置。
delete S.hearts; delete S.hDay;

function bumpStreak() {
  var t = today();
  if (S.last === t) return;
  var y = new Date(Date.now() - 864e5).toISOString().slice(0, 10);
  S.streak = (S.last === y) ? S.streak + 1 : 1;
  S.last = t;
}

var allLessons = [];
C.forEach(function (u) { u.L.forEach(function (l, i) { allLessons.push(u.id + "-" + i); }); });

// 题目 id → 题目对象。错题本只存 id，不存对象本身——
// 对象经 localStorage 的 JSON 往返后会变成一个新副本，用 === 永远比不上原题，
// 于是跨会话答错同一题会重复堆积、复习答对也移不出去。存 id 就没这个问题。
var QMAP = {};
C.forEach(function (u) {
  u.L.forEach(function (l) { l.q.forEach(function (q) { if (q.id) QMAP[q.id] = q; }); });
});
function byId(w) { return QMAP[typeof w === "string" ? w : (w && (w.id || (w.q && w.q.id)))]; }
// 旧版本存的是对象，这里把遗留数据迁成 id，顺便去重
(function migrateWrong() {
  var seen = {}, out = [];
  (S.wrong || []).forEach(function (w) {
    var q = byId(w) || (w && w.q && QMAP[w.q.id]);
    var id = q && q.id;
    if (id && !seen[id]) { seen[id] = 1; out.push({ id: id, t: (w && w.t) || Date.now() }); }
  });
  if (out.length !== (S.wrong || []).length) { S.wrong = out; save(); } else { S.wrong = out; }
})();

function paintTop() {
  $("#sStreak").textContent = S.streak;
  $("#sXp").textContent = S.xp;
  $("#sHeart").textContent = S.wrong.length;
  $("#mStreak").textContent = S.streak + " 天";
  $("#mXp").textContent = S.xp + " XP";
  $("#mDone").textContent = Object.keys(S.done).length + " / " + allLessons.length;
  $("#mWrong").textContent = S.wrong.length + " 道";
}

/* ── 学习路径 ──────────────────────────────────────────── */
function paintPath() {
  var firstOpen = null;
  var h = C.map(function (u) {
    var dn = u.L.filter(function (_, i) { return S.done[u.id + "-" + i]; }).length;
    var nodes = u.L.map(function (l, i) {
      var id = u.id + "-" + i, done = !!S.done[id];
      // 顺序解锁：本单元前一节做完才开下一节
      var open = done || i === 0 || !!S.done[u.id + "-" + (i - 1)];
      if (open && !done && !firstOpen) firstOpen = id;
      var cls = done ? "done" : (open ? (firstOpen === id ? "now" : "") : "lock");
      var ic = done ? "★" : (open ? "▶" : "🔒");
      // 平移只能加在 btnwrap（小元素）上——加在 .node 上会把整行宽的容器一起推出屏幕
      var off = [0, 40, 56, 40, 0, -40, -56, -40][i % 8];
      return '<div class="node">' +
        '<div class="btnwrap" style="transform:translateX(' + off + 'px)">' +
        (firstOpen === id && !done ? '<div class="now-tag">从这里开始</div>' : "") +
        '<button class="nd ' + cls + '" data-l="' + id + '" ' + (open ? "" : "disabled") + '>' + ic + "</button>" +
        '<div class="ndlabel">' + esc(l.t) + "</div></div></div>";
    }).join("");
    return '<div class="uhead" style="background:' + u.c + '">' +
      '<span class="ic">' + u.i + "</span><div><b>" + esc(u.t) + "</b><span>" + esc(u.s) + "</span></div>" +
      '<span class="pg">' + dn + "/" + u.L.length + "</span></div>" +
      '<div class="path">' + nodes + "</div>";
  }).join("");
  $("#pathBox").innerHTML = h +
    '<div class="tiny" style="text-align:center;padding:26px 0 10px">全部 ' + allLessons.length +
    " 节 · " + C.reduce(function (a, u) { return a + u.L.reduce(function (b, l) { return b + l.q.length; }, 0); }, 0) +
    " 道题<br>每节 3—6 题，一次 2 分钟</div>";
}
function esc(s) {
  return String(s == null ? "" : s).replace(/[&<>"]/g, function (m) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[m];
  });
}

/* ── 课程引擎 ──────────────────────────────────────────── */
var run = null;

function start(lid, fromReview) {
  var qs;
  if (fromReview) {
    // 按答错时间最久的优先，最多 8 道
    qs = S.wrong.slice(0, 8).map(byId).filter(Boolean);
    if (!qs.length) return;
  } else {
    var p = lid.split("-"), u = C.filter(function (x) { return x.id === p[0]; })[0];
    if (!u) return;
    qs = u.L[+p[1]].q.slice();   // 复制一份：答错要往里插回炉题，不能改到原题库
  }
  // 心数每节课重置，不跨天累计
  run = { lid: lid, rev: !!fromReview, qs: qs, i: 0, ok: 0, first: 0, asked: 0,
          hp: 5, picked: null, checked: false, pairState: null, seen: {} };
  $("#lesson").classList.add("on");
  document.body.style.overflow = "hidden";
  paintQ();
}
function quit() {
  $("#lesson").classList.remove("on");
  document.body.style.overflow = "";
  run = null; paintTop(); paintPath(); paintReview();
}

function hearts(n) { return "❤️".repeat(Math.max(0, n)) + "🖤".repeat(Math.max(0, 5 - n)); }

function paintQ() {
  var q = run.qs[run.i];
  $("#lbar").style.width = (run.i / run.qs.length * 100) + "%";
  $("#lhearts").textContent = hearts(run.hp);
  run.picked = null; run.checked = false;
  var fb = $("#fb"); fb.className = "fb"; $("#fbmsg").style.display = "none";
  var act = $("#act"); act.className = "btn"; act.disabled = true;

  // 情景前情：多步决策题共用的一段叙述
  var pre = q.pre ? '<div class="scene">' + q.pre + "</div>" : "";

  var body = "";
  if (q.k === "tf") {
    act.textContent = "选一个答案";
    body = pre + '<div class="qtype">判断题</div><div class="qtext">' + q.q + "</div>" +
      '<div class="opts"><button class="opt" data-v="1">✓　对</button>' +
      '<button class="opt" data-v="0">✗　错</button></div>';
  } else if (q.k === "mc" || q.k === "bank" || q.k === "num") {
    act.textContent = "选一个答案";
    var label = q.k === "bank" ? "填空题" : (q.k === "num" ? "数量级判断" : "选择题");
    body = pre + '<div class="qtype">' + label + "</div>" +
      '<div class="qtext">' + q.q + "</div><div class=\"opts\">" +
      q.o.map(function (o, i) { return '<button class="opt" data-v="' + i + '">' + esc(o) + "</button>"; }).join("") +
      "</div>";
  } else if (q.k === "order") {
    // 排序题：按正确顺序依次点，点错立刻标红
    act.textContent = "按顺序全部点完";
    run.orderState = { picked: [], err: false };
    var items = q.o.map(function (o, i) { return { t: o, i: i }; });
    shuffle(items);
    body = pre + '<div class="qtype">排序题</div><div class="qtext">' + q.q + "</div>" +
      '<div class="orderslots" id="oslots"></div><div class="opts">' +
      items.map(function (x) { return '<button class="opt oi" data-v="' + x.i + '">' + esc(x.t) + "</button>"; }).join("") +
      "</div>";
  } else if (q.k === "pair") {
    act.textContent = "全部配对后继续";
    var L = q.p.map(function (p, i) { return { t: p[0], i: i }; });
    var R = q.p.map(function (p, i) { return { t: p[1], i: i }; });
    shuffle(R);
    run.pairState = { left: L, right: R, sel: null, matched: 0 };
    body = pre + '<div class="qtype">配对题</div><div class="qtext" style="font-size:18px">把左右两边连起来</div>' +
      '<div class="pairgrid"><div class="pcol">' +
      L.map(function (x) { return '<button class="pi" data-s="L" data-i="' + x.i + '">' + esc(x.t) + "</button>"; }).join("") +
      '</div><div class="pcol">' +
      R.map(function (x) { return '<button class="pi" data-s="R" data-i="' + x.i + '">' + esc(x.t) + "</button>"; }).join("") +
      "</div></div>";
  }
  $("#lbody").innerHTML = body;
  $("#lbody").scrollTop = 0;
}
function shuffle(a) { for (var i = a.length - 1; i > 0; i--) { var j = (Math.random() * (i + 1)) | 0; var t = a[i]; a[i] = a[j]; a[j] = t; } }

// 选项点击
$("#lbody").addEventListener("click", function (e) {
  if (!run) return;
  var q = run.qs[run.i];

  // 排序题：依次点击，顺序错了当场标红并记一次错
  var oi = e.target.closest(".oi");
  if (oi && q.k === "order" && !run.checked) {
    var st = run.orderState, want = st.picked.length;
    if (+oi.dataset.v === want) {
      oi.classList.add("gone"); st.picked.push(want);
      $("#oslots").innerHTML = st.picked.map(function (i, n) {
        return '<span class="oslot">' + (n + 1) + ". " + esc(q.o[i]) + "</span>";
      }).join("");
      if (st.picked.length === q.o.length) {
        var a3 = $("#act"); a3.disabled = false; a3.className = "btn on"; a3.textContent = "继续";
        run.picked = 1;
      }
    } else {
      st.err = true; oi.classList.add("err");
      setTimeout(function () { oi.classList.remove("err"); }, 480);
    }
    return;
  }

  var o = e.target.closest(".opt");
  if (o && !run.checked && q.k !== "order") {
    $$("#lbody .opt").forEach(function (x) { x.classList.remove("sel"); });
    o.classList.add("sel");
    run.picked = +o.dataset.v;
    var a = $("#act"); a.disabled = false; a.className = "btn on"; a.textContent = "检查";
    return;
  }

  var p = e.target.closest(".pi");
  if (p && q.k === "pair" && !run.checked) {
    var st = run.pairState;
    if (!st.sel) {
      $$("#lbody .pi").forEach(function (x) { x.classList.remove("sel"); });
      p.classList.add("sel"); st.sel = p; return;
    }
    if (st.sel === p) { p.classList.remove("sel"); st.sel = null; return; }
    if (st.sel.dataset.s === p.dataset.s) {   // 同侧改选
      $$("#lbody .pi").forEach(function (x) { x.classList.remove("sel"); });
      p.classList.add("sel"); st.sel = p; return;
    }
    if (st.sel.dataset.i === p.dataset.i) {   // 配对成功
      st.sel.classList.add("gone"); p.classList.add("gone");
      st.sel.classList.remove("sel"); st.sel = null; st.matched++;
      if (st.matched === q.p.length) {
        var a2 = $("#act"); a2.disabled = false; a2.className = "btn on"; a2.textContent = "继续";
        run.picked = 1;
      }
    } else {                                   // 配错
      var w1 = st.sel, w2 = p;
      w1.classList.add("err"); w2.classList.add("err");
      run.pairErr = true;
      setTimeout(function () { w1.classList.remove("err", "sel"); w2.classList.remove("err"); }, 520);
      st.sel = null;
    }
    return;
  }
});

// 检查 / 继续
$("#act").addEventListener("click", function () {
  if (!run) return;
  var q = run.qs[run.i];

  if (!run.checked) {
    run.checked = true;
    var right;
    if (q.k === "pair") right = !run.pairErr;
    else if (q.k === "order") right = !(run.orderState && run.orderState.err);
    else right = (run.picked === q.a);
    run.pairErr = false;

    if (q.k !== "pair" && q.k !== "order") {
      $$("#lbody .opt").forEach(function (x) {
        var v = +x.dataset.v;
        if (v === q.a) x.classList.add("ok");
        else if (v === run.picked) x.classList.add("err");
        x.classList.remove("sel");
      });
    }

    // 首答正确率：回炉重做的不计入，否则结算页会把「多做两遍才对」显示成高分
    if (!run.seen[q.id]) { run.asked++; if (right) run.first++; }

    var fb = $("#fb"), msg = $("#fbmsg");
    if (right) {
      run.ok++;
      fb.className = "fb ok";
      msg.innerHTML = '<span class="ic">✅</span><div><b>答对了</b>' +
        (q.w ? '<div class="why">' + q.w + "</div>" : "") + "</div>";
      // 复习模式答对才移出错题本（按 id 比较，跨会话也有效）
      if (run.rev) S.wrong = S.wrong.filter(function (w) { return w.id !== q.id; });
    } else {
      run.hp--;
      fb.className = "fb err";
      msg.innerHTML = '<span class="ic">❌</span><div><b>再看一眼</b>' +
        (q.w ? '<div class="why">' + q.w + "</div>" : "") + "</div>";
      if (q.id && !S.wrong.some(function (w) { return w.id === q.id; }))
        S.wrong.push({ id: q.id, t: Date.now() });
      // 当场回炉：把这道题插回本轮队列的 +3 和 +9 位——
      // 答错的代价是「多做两遍」，不是「今天不许再学」。
      // 隔 3 题、隔 9 题本身就是最短的两级间隔，重复被放在了正确的位置。
      if (!run.rev && !run.seen[q.id]) {
        run.seen[q.id] = 1;
        run.qs.splice(Math.min(run.i + 3, run.qs.length), 0, q);
        run.qs.splice(Math.min(run.i + 9, run.qs.length), 0, q);
      }
      $("#lhearts").textContent = hearts(run.hp);
    }
    msg.style.display = "flex";
    save();

    var a = $("#act");
    a.className = "btn " + (right ? "on" : "no");
    a.textContent = run.hp <= 0 ? "本轮结束" : (run.i === run.qs.length - 1 ? "完成" : "继续");
    a.disabled = false;
    return;
  }

  if (run.hp <= 0) { finish(false); return; }
  run.i++;
  if (run.i >= run.qs.length) { finish(true); return; }
  paintQ();
});

function finish(cleared) {
  var xp = cleared ? (10 + run.ok * 2) : run.ok * 2;
  S.xp += xp;
  if (cleared && !run.rev) { S.done[run.lid] = 1; bumpStreak(); }
  if (cleared && run.rev) bumpStreak();
  save();
  $("#lbar").style.width = "100%";
  $("#fb").className = "fb"; $("#fbmsg").style.display = "none";
  // 显示「首答正确率」而不是总正确率：回炉重做的不算。
  // 一个答错三次、回炉后蒙对的人，本来会看到 100%，那是最有害的一种反馈——
  // 它把「知道自己不会」的人变成「以为自己会」的人。
  var fr = run.asked ? Math.round(run.first / run.asked * 100) : 0;
  var redo = run.asked - run.first;
  $("#lbody").innerHTML =
    '<div class="done"><div class="big">' + (cleared ? "🎉" : "💪") + "</div>" +
    "<h2>" + (cleared ? "这一节拿下了" : "错太多了，先看看解析") + "</h2>" +
    "<p>" + (cleared
      ? (redo ? "有 " + redo + " 道是回炉之后才对的，它们已经进了错题本"
              : "全部一次答对，干净利落")
      : "错过的题都在错题本里，随时可以重来——不用等明天") + "</p>" +
    '<div class="rewards"><div class="rw"><b>获得经验</b><span>+' + xp + "</span></div>" +
    '<div class="rw g"><b>首答正确率</b><span>' + fr + "%</span></div></div>" +
    (redo ? '<p class="hint">首答正确率只算第一次的答案。' +
            '<b>回炉做对不等于会</b>——那道题真正的考验是三天以后。</p>' : "") +
    "</div>";
  var a = $("#act"); a.className = "btn on"; a.textContent = "回到路径"; a.disabled = false;
  a.onclick = function () { a.onclick = null; quit(); };
}

$("#quit").addEventListener("click", quit);
document.addEventListener("click", function (e) {
  var n = e.target.closest(".nd");
  if (n && n.dataset.l) start(n.dataset.l, false);
});

/* ── 错题本 ────────────────────────────────────────────── */
function paintReview() {
  var box = $("#reviewBox");
  if (!S.wrong.length) {
    box.innerHTML = '<div class="empty"><div class="big">🌱</div>还没有错题<br><span class="tiny">做几节课再回来看看</span></div>';
    return;
  }
  box.innerHTML = '<button class="btn on" id="revGo" style="margin-bottom:16px">开始复习 ' +
    Math.min(8, S.wrong.length) + " 道</button>" +
    S.wrong.slice(0, 30).map(function (w) {
      var q = byId(w);
      if (!q) return "";
      var stem = q.k === "pair" ? "配对：" + q.p.map(function (p) { return p[0]; }).join(" / ") : q.q;
      return '<div class="tcard"><div class="t">' + stem + '</div>' +
             (q.w ? '<div class="d">' + q.w + "</div>" : "") + "</div>";
    }).join("");
  $("#revGo").addEventListener("click", function () { start("review", true); });
}

/* ── 术语 ──────────────────────────────────────────────── */
function paintTerms(kw) {
  kw = (kw || "").trim().toLowerCase();
  var list = TERMS;
  if (kw) {
    list = TERMS.map(function (t) {
      var s = 0, lt = t.t.toLowerCase();
      if (lt === kw) s += 400; else if (lt.indexOf(kw) === 0) s += 220; else if (lt.indexOf(kw) >= 0) s += 130;
      if (t.cn && t.cn.toLowerCase().indexOf(kw) >= 0) s += 90;
      if (t.en && t.en.toLowerCase().indexOf(kw) >= 0) s += 70;
      if (t.d && t.d.toLowerCase().indexOf(kw) >= 0) s += 22;
      if (t.n && t.n.toLowerCase().indexOf(kw) >= 0) s += 12;
      return { t: t, s: s };
    }).filter(function (o) { return o.s > 0; }).sort(function (a, b) { return b.s - a.s; })
      .map(function (o) { return o.t; });
  }
  $("#termBox").innerHTML = list.slice(0, 60).map(function (t) {
    return '<div class="tcard"><div class="t">' + esc(t.t) +
      (t.cn ? "<span>" + esc(t.cn) + "</span>" : "") + "</div>" +
      (t.en ? '<div class="en">' + esc(t.en) + "</div>" : "") +
      (t.d ? '<div class="d">' + t.d + "</div>" : "") +
      (t.n ? '<div class="n">⚑ ' + t.n + "</div>" : "") + "</div>";
  }).join("") || '<div class="empty"><div class="big">🔍</div>没找到<br><span class="tiny">试试英文缩写，或换成中文</span></div>';
}
$("#tSearch").addEventListener("input", function () { paintTerms(this.value); });

/* ── 导航 ──────────────────────────────────────────────── */
$("#nav").addEventListener("click", function (e) {
  var b = e.target.closest("button[data-p]"); if (!b) return;
  $$(".nav button").forEach(function (x) { x.classList.toggle("on", x === b); });
  $$(".page").forEach(function (p) { p.classList.toggle("on", p.id === b.dataset.p); });
  window.scrollTo(0, 0);
  if (b.dataset.p === "pReview") paintReview();
  if (b.dataset.p === "pMe") paintTop();
});

$("#reset").addEventListener("click", function () {
  if (!confirm("清空全部进度、经验和错题本？此操作不可撤销。")) return;
  try { localStorage.removeItem(KEY); } catch (e) {}
  S = load(); save(); paintTop(); paintPath(); paintReview();
  alert("已重置");
});

/* ── 启动 ──────────────────────────────────────────────── */
$("#tCount").textContent = TERMS.length;
paintTop(); paintPath(); paintReview(); paintTerms("");

if ("serviceWorker" in navigator) {
  window.addEventListener("load", function () {
    navigator.serviceWorker.register("sw.js").catch(function () {});
  });
}
})();
