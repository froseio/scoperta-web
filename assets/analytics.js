// First-party product events. The only input accepted from the UI is an action name.
// Network events come from the two explicit API call sites, never a global fetch hook.
(() => {
  "use strict";
  const supportedOrigin = ["https://scoperta.app", "http://127.0.0.1:5173"].includes(location.origin);
  const namespace = "scoperta.analytics.v1.";
  const choiceKey = namespace + "choice";
  const queuePrefix = namespace + "event.";
  const tabKey = namespace + "session";
  const endpoint = "https://tassello.app/api/browser/scoperta";
  const week = 7 * 86400_000;
  const actions = new Set(["screen_view", "form_started", "itinerary_requested", "itinerary_generated",
    "itinerary_failed", "stop_clicked", "share_clicked", "print_clicked", "variant_clicked",
    "paywall_viewed", "checkout_clicked", "lang_switched"]);
  let screen, locale, timer, pending, delay = 1000;
  let controller;
  function choice() {
    try { return localStorage.getItem(choiceKey); } catch { return null; }
  }
  function granted(value) { return typeof value === "string" && value.startsWith("yes:"); }
  function entries() {
    return Object.keys(localStorage).filter(k => k.startsWith(queuePrefix));
  }
  function read(key) {
    try { return JSON.parse(localStorage.getItem(key)); } catch { return null; }
  }
  function context() {
    const consent = choice();
    if (!supportedOrigin || !screen || !granted(consent)) return null;
    try {
      const now = Date.now();
      let s = JSON.parse(sessionStorage.getItem(tabKey) || "null");
      if (!s || s.consent !== consent || now < s.last || now - s.last > 1800_000) {
        let device = "unknown";
        if (typeof matchMedia === "function") {
          const coarse = matchMedia("(pointer: coarse)").matches;
          device = coarse ? (matchMedia("(min-width: 768px)").matches ? "tablet" : "handheld") : "desktop";
        }
        s = {consent, session: crypto.randomUUID(), started: now, device, locale};
      }
      s.last = now;
      // Preserve the order of actions that occur within one browser clock tick.
      s.lastEvent = Math.max(now, (s.lastEvent ?? now - 1) + 1);
      sessionStorage.setItem(tabKey, JSON.stringify(s));
      return {consent, session: s.session, started: s.started, device: s.device, language: s.locale, time: s.lastEvent};
    } catch { return null; }
  }
  function schedule(ms) {
    clearTimeout(timer);
    if (granted(choice())) timer = setTimeout(flush, ms);
  }
  function enqueue(c, name, metadata = {}) {
    if (!c || choice() !== c.consent) return;
    try {
      const event = {id: crypto.randomUUID(), name, time: c.time, screen, locale, ...metadata};
      const keys = entries().sort();
      // Event keys start with epoch milliseconds. Bound the offline journal before writing.
      for (const key of keys.slice(0, Math.max(0, keys.length - 127))) localStorage.removeItem(key);
      localStorage.setItem(queuePrefix + c.time + "." + event.id, JSON.stringify({
        consent: c.consent, session: c.session, started: c.started, device: c.device, language: c.language, event,
      }));
      if (!pending && !timer) schedule(150);
    } catch { /* Storage or randomness unavailable: collection stays inactive. */ }
  }
  function track(name) { if (actions.has(name)) enqueue(context(), name); }
  function network(name) {
    if (name !== "generate_request" && name !== "shared_trip_request") return () => {};
    const c = context();
    const started = performance.now();
    return status => enqueue(c, name, {status, duration: Math.min(600_000, Math.max(0, Math.round(performance.now() - started)))});
  }
  async function flush() {
    clearTimeout(timer); timer = null;
    const consent = choice();
    if (pending || !granted(consent)) return;
    pending = true;
    try {
      const batch = [];
      for (const key of entries().sort()) {
        const row = read(key);
        if (!row || row.consent !== consent || row.started < Date.now() - week) {
          localStorage.removeItem(key);
        } else if (batch.length === 0 || row.session === batch[0].row.session) {
          batch.push({key, row});
          if (batch.length === 12) break;
        }
      }
      if (!batch.length || choice() !== consent) return;
      controller = new AbortController();
      const timeout = setTimeout(() => controller?.abort(), 12_000);
      let response;
      try {
        response = await fetch(endpoint, {
          method: "POST", credentials: "omit", referrerPolicy: "no-referrer", redirect: "error",
          keepalive: true, signal: controller.signal, headers: {"Content-Type": "application/json"},
          body: JSON.stringify({installation: consent.slice(4), session: batch[0].row.session,
            started: batch[0].row.started, device: batch[0].row.device, locale: batch[0].row.language, events: batch.map(entry => entry.row.event)}),
        });
      } finally { clearTimeout(timeout); }
      if (response.status === 202 || response.status === 400 || response.status === 413) {
        for (const entry of batch) localStorage.removeItem(entry.key);
        delay = 1000;
      } else {
        delay = Math.min(delay * 2, 60_000);
      }
    } catch { delay = Math.min(delay * 2, 60_000); }
    finally {
      controller = null; pending = false;
      try { if (granted(choice()) && entries().length) schedule(delay); } catch { /* storage disabled */ }
    }
  }
  function start() {
    if (!supportedOrigin || !globalThis.crypto?.randomUUID) return;
    const bar = document.querySelector("#cookie-bar");
    const settings = document.querySelector("#analytics-choice");
    if (!bar || !settings) return;
    screen = document.querySelector("#trip-form") ? "planner" : document.querySelector("#trip-page") ? "shared_trip" : "privacy";
    locale = document.documentElement.getAttribute("data-locale");
    if (!["cs", "en", "de", "it"].includes(locale)) return;
    function refresh() { const value = choice(); bar.hidden = value === "denied" || granted(value); }
    function deny() {
      try {
        localStorage.setItem(choiceKey, "denied");
        for (const key of entries()) localStorage.removeItem(key);
        sessionStorage.removeItem(tabKey);
      } finally { controller?.abort(); clearTimeout(timer); timer = null; refresh(); }
    }
    settings.hidden = false;
    settings.addEventListener("click", () => { bar.hidden = false; document.querySelector("#cookie-accept").focus(); });
    document.querySelector("#cookie-accept").addEventListener("click", () => {
      try {
        if (!granted(choice())) {
          localStorage.setItem(choiceKey, "yes:" + crypto.randomUUID());
          track("screen_view");
        }
      } catch { /* No persistent choice means no tracking. */ }
      refresh();
    });
    document.querySelector("#cookie-decline").addEventListener("click", () => { try { deny(); } catch { /* storage disabled */ } });
    addEventListener("storage", e => {
      if (e.key === choiceKey || e.key === null) {
        if (!granted(choice())) { controller?.abort(); clearTimeout(timer); timer = null; }
        refresh();
      }
    });
    addEventListener("online", flush);
    document.addEventListener("visibilitychange", () => { if (document.hidden) void flush(); });
    refresh();
    track("screen_view");
  }
  window.ScopertaAnalytics = {start, track, network};
})();
