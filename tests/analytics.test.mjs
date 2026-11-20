import assert from "node:assert/strict";
import test from "node:test";
import {readFileSync} from "node:fs";
import {randomUUID} from "node:crypto";
import {runInNewContext} from "node:vm";

const script = readFileSync(new URL("../assets/analytics.js", import.meta.url), "utf8");
const storage = () => Object.create({
  getItem(k) {return this[k] ?? null;}, setItem(k,v) {this[k]=v;}, removeItem(k) {delete this[k];},
});
function tab({local = storage(), session = storage(), origin = "http://127.0.0.1:5173", status = () => 202} = {}) {
  const sent = [], handlers = new Map(), nodes = new Map();
  const el = id => {
    if (!nodes.has(id)) nodes.set(id, {hidden:true,focus(){},addEventListener(name, f) {this[name] = f;}});
    return nodes.get(id);
  };
  const env = {window:{}, location:{origin}, document:{
    querySelector:el, documentElement:{getAttribute:()=>"cs"}, addEventListener(){},
  }, localStorage:local, sessionStorage:session, crypto:{randomUUID}, performance, AbortController,
  setTimeout, clearTimeout, addEventListener:(name,f)=>handlers.set(name,f),
  fetch: async (url, init) => {sent.push({url,init,body:JSON.parse(init.body)});return {status:status()};},
  };
  runInNewContext(script,env);
  const app = env.window.ScopertaAnalytics;
  app.start();
  return {app, local, session, sent, click:id=>el(id).click?.(), flush:()=>handlers.get("online")?.(), notify:() =>handlers.get("storage")?.({key:"scoperta.analytics.v1.choice"})};
}

test("opt-in gates pages and interaction, redacts inputs, separates planning traffic", async () => {
  const t=tab();
  t.app.track("form_started"); await t.flush();
  assert.equal(t.sent.length,0);
  t.click("#cookie-accept");
  t.app.track("form_started",{origin:"synthetic sensitive address"});
  t.app.track("user provided event");
  t.app.network("generate_request")(204);
  t.app.network("tassello")(200);
  await t.flush();
  const {body, init, url} = t.sent[0];
  assert.deepEqual(body.events.map(x=>x.name).sort(),["form_started","generate_request","screen_view"]);
  assert.equal(url,"https://tassello.app/api/browser/scoperta");
  assert.equal(init.credentials,"omit");assert.equal(init.referrerPolicy,"no-referrer");
  assert.ok(!init.body.includes("synthetic sensitive address"));
  assert.ok(!init.body.includes("user provided event"));
  t.click("#cookie-decline");
});
test("transient failure survives reload; revocation blocks pending requests and rotates identity", async () => {
  const old=tab({status:()=>503});
  old.click("#cookie-accept"); old.app.track("form_started"); await old.flush();
  const before=old.sent[0].body, finish=old.app.network("generate_request");
  const next=tab({local:old.local,session:old.session});
  await next.flush();
  assert.equal(next.sent[0].body.installation,before.installation);
  for (const e of before.events) assert.ok(next.sent[0].body.events.some(x=>x.id===e.id));
  next.click("#cookie-decline");old.notify();
  next.click("#cookie-accept");finish(200);await next.flush();
  assert.notEqual(next.sent[1].body.installation,before.installation);
  assert.notEqual(next.sent[1].body.session,before.session);
  assert.deepEqual(next.sent[1].body.events.map(x=>x.name),["screen_view"]);
  next.click("#cookie-decline");old.notify();
});
test("unsupported origins never collect or send", async () => {
  const t=tab({origin:"https://unexpected.invalid"});
  t.click("#cookie-accept");t.app.track("form_started");await t.flush();
  assert.equal(t.sent.length,0);assert.equal(Object.keys(t.local).length,0);
});
