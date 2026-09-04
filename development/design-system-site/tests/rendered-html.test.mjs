import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
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

test("server-renders the somoim prototype with collected groups", async () => {
  const response = await render("/somoim");
  assert.equal(response.status, 200);
  const html = await response.text();
  assert.match(html, /맞춤 모임/);
  assert.match(html, /잡학다食/);
  assert.match(html, /사유식탁/);
  assert.doesNotMatch(html, /자유독서단|책읽는 저녁/);
});

test("collected somoim data replaces board and gallery samples", async () => {
  const source = JSON.parse(await readFile(new URL("../app/somoim/groups.json", import.meta.url), "utf8"));
  assert.equal(source.length, 16);
  assert.equal(source.reduce((sum, group) => sum + group.events.length, 0), 37);
  assert.ok(source.reduce((sum, group) => sum + group.memberList.length, 0) > 0);
  assert.ok(source.reduce((sum, group) => sum + group.articles.length, 0) > 0);
  assert.ok(source.reduce((sum, group) => sum + group.photos.length, 0) > 0);

  const screens = await readFile(new URL("../app/somoim/screens.tsx", import.meta.url), "utf8");
  assert.doesNotMatch(screens, /즐거웠던 정기모임 후기|GALLERY_IMAGES/);
});
