import assert from "node:assert/strict";
import test from "node:test";

async function render(pathname = "/") {
  const workerUrl = new URL("../dist/server/index.js", import.meta.url);
  workerUrl.searchParams.set("test", `${process.pid}-${Date.now()}-${pathname}`);
  const { default: worker } = await import(workerUrl.href);
  return worker.fetch(
    new Request(`http://localhost${pathname}`, { headers: { accept: "text/html" } }),
    { ASSETS: { fetch: async () => new Response("Not found", { status: 404 }) } },
    { waitUntil() {}, passThroughOnException() {} },
  );
}

test("server-renders the design system overview", async () => {
  const response = await render();
  assert.equal(response.status, 200);
  assert.match(response.headers.get("content-type") ?? "", /^text\/html\b/i);
  const html = await response.text();
  assert.match(html, /Somoim Design System/);
  assert.match(html, /모임 경험을/);
  assert.match(html, /Foundations/);
  assert.match(html, /Components/);
  assert.doesNotMatch(html, /codex-preview|Your site is taking shape/);
});

test("server-renders the core documentation routes", async () => {
  for (const [path, expected] of [
    ["/foundations", "Typography"],
    ["/components", "Participated Gathering Card"],
    ["/components/textbox", "Variants &amp; states"],
    ["/roadmap", "확장 원칙"],
  ]) {
    const response = await render(path);
    assert.equal(response.status, 200, path);
    const html = await response.text();
    assert.match(html, new RegExp(expected));
    assert.doesNotMatch(html, /현재 화면에서 확인된|1차 문서 범위|Figma에서 확인됨|작업형 문서/);
  }
});
