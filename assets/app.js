/* Scoperta — shared app logic (index + trip pages, all locales).
   Page texts live in HTML (SEO); JS-only strings come from assets/i18n/<locale>.js */
(function () {
  "use strict";

  var CFG = window.SCOPERTA_CONFIG || {};
  var T = window.SCOPERTA_I18N || {};
  var LOCALE = document.documentElement.getAttribute("data-locale") || "cs";

  var $ = function (sel, root) { return (root || document).querySelector(sel); };
  var $$ = function (sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); };

  var KIND_ICONS = {
    origin: "🏠", activity: "🥾", lunch: "🍽️", treat: "🍨",
    viewpoint: "🌄", destination: "📍"
  };

  var WEATHER_ICONS = {
    clear: "☀️", partly: "⛅", cloudy: "☁️", fog: "🌫️",
    drizzle: "🌦️", rain: "🌧️", snow: "❄️", storm: "⛈️"
  };

  var state = { shareUrl: null, map: null, leafletPromise: null };

  function track(name) {
    window.ScopertaAnalytics?.track(name);
  }

  function fetchTrip(name, url, options) {
    const complete = CFG.API_BASE === "https://api.chargechill.app" ? window.ScopertaAnalytics?.network(name) : undefined;
    return fetch(url, options).then(response => {
      // Responses reached through a redirect do not describe the registered API route.
      if (!response.redirected && (!response.url || response.url === url)) complete?.(response.status);
      return response;
    }, error => {
      complete?.(0);
      throw error;
    });
  }

  /* ── Helpers ────────────────────────────────────────────────── */

  function todayISO() {
    var d = new Date();
    var m = String(d.getMonth() + 1).padStart(2, "0");
    var day = String(d.getDate()).padStart(2, "0");
    return d.getFullYear() + "-" + m + "-" + day;
  }

  function tripCount() {
    try {
      var raw = localStorage.getItem("scoperta.trips");
      if (!raw) { return 0; }
      var o = JSON.parse(raw);
      return o.d === todayISO() ? (o.n || 0) : 0;
    } catch (e) { return 0; }
  }

  function bumpTripCount() {
    try {
      localStorage.setItem("scoperta.trips", JSON.stringify({ d: todayISO(), n: tripCount() + 1 }));
    } catch (e) {}
  }

  function fmtHours(min) {
    var r = T.result || {};
    if (min == null) { return ""; }
    var h = Math.floor(min / 60), m = Math.round(min % 60);
    if (h <= 0) { return m + " " + (r.min || "min"); }
    return h + " " + (r.hoursShort || "h") + (m ? " " + m + " " + (r.min || "min") : "");
  }

  function fmtArrival(v) {
    if (!v) { return ""; }
    if (v.indexOf("T") !== -1) {
      var d = new Date(v);
      if (!isNaN(d)) {
        return d.toLocaleTimeString(LOCALE, { hour: "2-digit", minute: "2-digit" });
      }
    }
    return v;
  }

  /* ── Leaflet (lazy) ─────────────────────────────────────────── */

  function loadLeaflet() {
    if (window.L) { return Promise.resolve(); }
    if (state.leafletPromise) { return state.leafletPromise; }
    state.leafletPromise = new Promise(function (resolve, reject) {
      var css = document.createElement("link");
      css.rel = "stylesheet";
      css.href = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css";
      document.head.appendChild(css);
      var js = document.createElement("script");
      js.src = "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js";
      js.onload = resolve;
      js.onerror = reject;
      document.head.appendChild(js);
    });
    return state.leafletPromise;
  }

  function drawMap(stops) {
    var el = $("#map");
    if (!el) { return; }
    loadLeaflet().then(function () {
      if (state.map) { state.map.remove(); state.map = null; }
      var pts = stops
        .filter(function (s) { return s.coordinate && typeof s.coordinate.lat === "number"; })
        .map(function (s) { return s; });
      if (!pts.length) { el.hidden = true; return; }
      el.hidden = false;
      var map = window.L.map(el, { scrollWheelZoom: false });
      state.map = map;
      window.L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      }).addTo(map);
      var latlngs = [];
      pts.forEach(function (s, i) {
        var ll = [s.coordinate.lat, s.coordinate.lon];
        latlngs.push(ll);
        var icon = window.L.divIcon({
          className: "",
          html: '<div class="map-marker">' + (i + 1) + "</div>",
          iconSize: [28, 28],
          iconAnchor: [14, 14]
        });
        window.L.marker(ll, { icon: icon, title: s.title || "" }).addTo(map)
          .bindPopup('<strong>' + escapeHtml(s.title || "") + "</strong>");
      });
      window.L.polyline(latlngs, { color: "#1E5A3C", weight: 3, opacity: 0.8, dashArray: "6 8" }).addTo(map);
      map.fitBounds(window.L.latLngBounds(latlngs).pad(0.15));
    }).catch(function () { el.hidden = true; });
  }

  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  /* ── Itinerary rendering (shared by index + trip pages) ─────── */

  function renderItinerary(it) {
    var r = T.result || {};
    $("#result-title").textContent = it.title || "";
    $("#result-summary").textContent = it.summary || "";

    var meta = $("#result-meta");
    meta.innerHTML = "";
    if (it.totalDistanceKm != null) {
      var m1 = document.createElement("span");
      m1.textContent = "🚗 " + Math.round(it.totalDistanceKm) + " " + (r.km || "km") + " " + (r.metaDistance || "");
      meta.appendChild(m1);
    }
    if (it.totalDurationMin != null) {
      var m2 = document.createElement("span");
      m2.textContent = "⏱️ " + fmtHours(it.totalDurationMin) + " " + (r.metaDuration || "");
      meta.appendChild(m2);
    }

    // weather chip (optional field — older shared trips won't have it)
    var w = it.weather;
    if (w && typeof w === "object") {
      var chip = document.createElement("span");
      chip.className = "weather-chip";
      var parts = [WEATHER_ICONS[w.code] || "🌤️"];
      if (w.tempMinC != null && w.tempMaxC != null) {
        parts.push(Math.round(w.tempMinC) + "–" + Math.round(w.tempMaxC) + " °C");
      } else if (w.tempMaxC != null) {
        parts.push(Math.round(w.tempMaxC) + " °C");
      }
      if (w.precipitationChancePct != null && w.precipitationChancePct >= 30) {
        parts.push("💧 " + Math.round(w.precipitationChancePct) + " %");
      }
      chip.textContent = parts.join(" ");
      if (w.summary) { chip.title = w.summary; }
      meta.insertBefore(chip, meta.firstChild);
    }

    // packing list card (optional field)
    var packing = $("#packing");
    if (packing) {
      var packItems = Array.isArray(it.packingList) ? it.packingList : [];
      packing.innerHTML = "";
      if (packItems.length) {
        var ph = document.createElement("h3");
        ph.textContent = r.packTitle || "";
        packing.appendChild(ph);
        var pul = document.createElement("ul");
        packItems.forEach(function (item) {
          var pli = document.createElement("li");
          pli.textContent = item;
          pul.appendChild(pli);
        });
        packing.appendChild(pul);
        packing.hidden = false;
      } else {
        packing.hidden = true;
      }
    }

    var list = $("#timeline");
    list.innerHTML = "";
    var stops = it.stops || [];
    stops.forEach(function (s, i) {
      var li = document.createElement("li");
      var dot = document.createElement("span");
      dot.className = "dot";
      dot.textContent = String(i + 1);
      li.appendChild(dot);

      var card = document.createElement("article");
      card.className = "stop-card";

      var head = document.createElement("div");
      head.className = "stop-head";
      var ico = document.createElement("span");
      ico.className = "kind-ico";
      ico.setAttribute("aria-hidden", "true");
      ico.textContent = KIND_ICONS[s.kind] || "📍";
      head.appendChild(ico);
      var h3 = document.createElement("h3");
      h3.textContent = s.title || "";
      head.appendChild(h3);
      var times = [];
      if (s.arrivalTime) { times.push(fmtArrival(s.arrivalTime)); }
      if (s.durationMin) { times.push("~" + s.durationMin + " " + (r.min || "min")); }
      if (times.length) {
        var tEl = document.createElement("span");
        tEl.className = "times";
        tEl.textContent = times.join(" · ");
        head.appendChild(tEl);
      }
      card.appendChild(head);

      if (s.detail) {
        var p = document.createElement("p");
        p.className = "detail";
        p.textContent = s.detail;
        card.appendChild(p);
      }

      var badges = [];
      if (s.dogNote) { badges.push({ label: (T.badges || {}).dog || "🐕", note: s.dogNote }); }
      if (s.kidsNote) { badges.push({ label: (T.badges || {}).kids || "👨‍👩‍👧", note: s.kidsNote }); }
      if (badges.length) {
        var bWrap = document.createElement("div");
        bWrap.className = "badges";
        badges.forEach(function (b) {
          var el = document.createElement("span");
          el.className = "badge";
          el.textContent = b.label + " — " + b.note;
          bWrap.appendChild(el);
        });
        card.appendChild(bWrap);
      }

      card.addEventListener("click", function () {
        track("stop_clicked");
      });

      li.appendChild(card);
      list.appendChild(li);
    });

    var tips = $("#tips");
    if (tips) {
      if (it.tips) {
        tips.hidden = false;
        $("#tips-text").textContent = it.tips;
      } else {
        tips.hidden = true;
      }
    }

    drawMap(stops);
    $("#result").hidden = false;
  }

  /* ── Result actions ─────────────────────────────────────────── */

  function initResultActions() {
    var shareBtn = $("#share-btn");
    if (shareBtn) {
      shareBtn.addEventListener("click", function () {
        var url = state.shareUrl || location.href;
        var sh = T.share || {};
        if (navigator.share) {
          navigator.share({ title: sh.title || "Scoperta", url: url }).then(function () {
            track("share_clicked");
          }).catch(function () {});
        } else if (navigator.clipboard) {
          navigator.clipboard.writeText(url).then(function () {
            track("share_clicked");
            flash(shareBtn, sh.copied || "✔");
          });
        } else {
          window.prompt(sh.copyFail || "Link:", url);
          track("share_clicked");
        }
      });
    }
    var printBtn = $("#print-btn");
    if (printBtn) {
      printBtn.addEventListener("click", function () {
        track("print_clicked");
        window.print();
      });
    }
    var variantBtn = $("#variant-btn");
    if (variantBtn) {
      variantBtn.addEventListener("click", function () {
        track("variant_clicked");
        openPaywall();
      });
    }
  }

  function flash(btn, msg) {
    var old = btn.textContent;
    btn.textContent = msg;
    setTimeout(function () { btn.textContent = old; }, 2200);
  }

  /* ── Paywall ────────────────────────────────────────────────── */

  function openPaywall() {
    var pw = $("#paywall");
    if (!pw) { return; }
    $("#paywall-main").hidden = false;
    $("#paywall-fallback").hidden = true;
    pw.hidden = false;
    document.body.style.overflow = "hidden";
    track("paywall_viewed");
  }

  function closePaywall() {
    var pw = $("#paywall");
    if (pw) { pw.hidden = true; }
    document.body.style.overflow = "";
  }

  function initPaywall() {
    var pw = $("#paywall");
    if (!pw) { return; }
    $$(".close, [data-close]", pw).forEach(function (b) {
      b.addEventListener("click", closePaywall);
    });
    pw.addEventListener("click", function (e) {
      if (e.target === pw) { closePaywall(); }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { closePaywall(); }
    });
    $$(".plan-btn", pw).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var plan = btn.getAttribute("data-plan");
        track("checkout_clicked");
        var url = plan === "yearly" ? CFG.STRIPE_URL_YEARLY : CFG.STRIPE_URL_MONTHLY;
        if (!url || url === "#") {
          $("#paywall-main").hidden = true;
          $("#paywall-fallback").hidden = false;
        } else {
          window.location.href = url;
        }
      });
    });
  }

  /* ── Trip form (index pages) ────────────────────────────────── */

  function showError(msg) {
    var el = $("#form-error");
    el.textContent = msg;
    el.hidden = false;
    el.scrollIntoView({ block: "nearest", behavior: "smooth" });
  }

  function initForm() {
    var form = $("#trip-form");
    if (!form) { return; }

    // default date = today
    var dateInput = $("#date");
    dateInput.value = todayISO();
    dateInput.min = todayISO();

    // form_started (first interaction)
    var started = false;
    form.addEventListener("focusin", function () {
      if (!started) { started = true; track("form_started"); }
    });

    // companions chips
    $$(".chip", form).forEach(function (chip) {
      chip.addEventListener("click", function () {
        var on = chip.getAttribute("aria-pressed") === "true";
        chip.setAttribute("aria-pressed", on ? "false" : "true");
      });
    });

    // pace segmented
    $$(".segmented button", form).forEach(function (btn) {
      btn.addEventListener("click", function () {
        $$(".segmented button", form).forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        btn.setAttribute("aria-pressed", "true");
      });
    });

    // radius only when "area" empty
    var area = $("#area");
    var radiusField = $("#radius-field");
    var radius = $("#radius");
    var radiusOut = $("#radius-out");
    function syncRadius() {
      radiusField.hidden = area.value.trim().length > 0;
      radiusOut.textContent = radius.value;
    }
    area.addEventListener("input", syncRadius);
    radius.addEventListener("input", syncRadius);
    syncRadius();

    var loadingTimer = null;

    function stopLoading() {
      if (loadingTimer) { clearInterval(loadingTimer); loadingTimer = null; }
      $("#loading").hidden = true;
      $("#submit-btn").disabled = false;
    }

    function startLoading() {
      var msgs = T.loading || ["…"];
      var i = 0;
      var msgEl = $("#loading-msg");
      msgEl.textContent = msgs[0];
      loadingTimer = setInterval(function () {
        i = (i + 1) % msgs.length;
        msgEl.textContent = msgs[i];
      }, 3500);
      $("#loading").hidden = false;
      $("#submit-btn").disabled = true;
      $("#loading").scrollIntoView({ block: "start", behavior: "smooth" });
    }

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      $("#form-error").hidden = true;

      // fake-door: 2nd submit the same day -> paywall (server limits 3/IP anyway)
      if (tripCount() >= 1) {
        openPaywall();
        return;
      }

      var companions = $$('.chip[aria-pressed="true"]', form).map(function (c) {
        return c.getAttribute("data-value");
      });
      var paceBtn = $('.segmented button[aria-pressed="true"]', form);
      var areaVal = area.value.trim();
      var payload = {
        origin: $("#origin").value.trim(),
        companions: companions,
        date: dateInput.value || todayISO(),
        pace: paceBtn ? paceBtn.getAttribute("data-pace") : "relaxed",
        locale: LOCALE
      };
      if (areaVal) { payload.area = areaVal; }
      else { payload.radiusKm = parseInt(radius.value, 10); }

      track("itinerary_requested");

      $("#result").hidden = true;
      startLoading();

      var ctrl = new AbortController();
      var timeout = setTimeout(function () { ctrl.abort(); }, CFG.REQUEST_TIMEOUT_MS || 150000);

      fetchTrip("generate_request", (CFG.API_BASE || "") + "/api/v1/daytrip/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        signal: ctrl.signal
      }).then(function (resp) {
        clearTimeout(timeout);
        if (resp.ok) { return resp.json(); }
        return resp.json().catch(function () { return {}; }).then(function (body) {
          var err = new Error("api");
          err.status = resp.status;
          err.reason = body && body.reason;
          throw err;
        });
      }).then(function (data) {
        stopLoading();
        bumpTripCount();
        state.shareUrl = data.shareUrl || null;
        track("itinerary_generated");
        renderItinerary(data.itinerary || {});
        $("#result").scrollIntoView({ block: "start", behavior: "smooth" });
      }).catch(function (err) {
        clearTimeout(timeout);
        stopLoading();
        var E = T.errors || {};
        var code, msg;
        if (err.name === "AbortError") { code = "timeout"; msg = E.timeout; }
        else if (err.status === 422) { code = 422; msg = err.reason || E.badPlace; }
        else if (err.status === 429) { code = 429; msg = err.reason || E.limit; }
        else if (err.status === 503) { code = 503; msg = err.reason || E.capacity; }
        else if (err.status) { code = err.status; msg = err.reason || E.generic; }
        else { code = "network"; msg = E.network; }
        track("itinerary_failed");
        showError(msg || E.generic || "Error");
      });
    });
  }

  /* ── Shared trip page ───────────────────────────────────────── */

  function initTripPage() {
    var page = $("#trip-page");
    if (!page) { return; }
    var status = $("#trip-status");
    var token = new URLSearchParams(location.search).get("token");
    var tt = T.trip || {};

    // keep ?token when switching languages
    if (token) {
      $$(".lang-switch a").forEach(function (a) {
        a.href = a.getAttribute("href").split("?")[0] + "?token=" + encodeURIComponent(token);
      });
    }

    if (!token) { return; } // static explainer in HTML stays visible

    $("#trip-intro").hidden = true;
    status.textContent = tt.loading || "…";
    status.hidden = false;

    fetchTrip("shared_trip_request", (CFG.API_BASE || "") + "/api/v1/shared/trip/" + encodeURIComponent(token))
      .then(function (resp) {
        if (resp.status === 404) { var e = new Error("nf"); e.notFound = true; throw e; }
        if (!resp.ok) { throw new Error("api"); }
        return resp.json();
      })
      .then(function (data) {
        var it = data;
        if (typeof data.routeJson === "string") { it = JSON.parse(data.routeJson); }
        if (it && it.itinerary) { it = it.itinerary; }
        status.hidden = true;
        state.shareUrl = location.href;
        renderItinerary(it || {});
      })
      .catch(function (err) {
        status.textContent = err.notFound ? (tt.notFound || "Not found") : (tt.loadFail || "Error");
        status.hidden = false;
      });
  }

  /* ── Language switcher tracking ─────────────────────────────── */

  function initLangSwitch() {
    $$(".lang-switch a").forEach(function (a) {
      a.addEventListener("click", function () {
        track("lang_switched");
      });
    });
  }

  /* ── Boot ───────────────────────────────────────────────────── */

  function boot() {
    window.ScopertaAnalytics?.start();
    initLangSwitch();
    initPaywall();
    initResultActions();
    initForm();
    initTripPage();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
