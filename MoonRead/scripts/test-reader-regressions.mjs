import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import net from "node:net";
import path from "node:path";
import { spawn } from "node:child_process";
import { after, before, test } from "node:test";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const appRoot = fileURLToPath(new URL("..", import.meta.url));
const stateKey = "moonread-state-v1";

const seed = {
  progress: {
    "horror-game-developer": {
      chapterId: "ch003",
      number: 3,
      title: "บทที่ 3: ทดสอบ",
      href: "/books/horror-game-developer/read/ch003",
      percent: 42,
      updatedAt: Date.now(),
    },
  },
  bookmarks: {
    "horror-game-developer": [
      { id: "ch002", number: 2, title: "บทที่ 2: ทดสอบ", href: "/books/horror-game-developer/read/ch002" },
    ],
  },
  favorites: ["horror-game-developer"],
  reader: {
    theme: "night",
    fontSize: 22,
    lineHeight: 2.0,
    width: 760,
    paragraphSpacing: 1.25,
    fontFamily: "serif",
    autoAdvance: false,
  },
};

function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = typeof address === "object" && address ? address.port : 3060;
      server.close(() => resolve(port));
    });
  });
}

function waitForHttp(url, timeoutMs = 45000) {
  const startedAt = Date.now();
  return new Promise((resolve, reject) => {
    const probe = () => {
      const request = http.get(url, (response) => {
        response.resume();
        if (response.statusCode && response.statusCode < 500) return resolve();
        if (Date.now() - startedAt > timeoutMs) return reject(new Error(`Timed out waiting for ${url}`));
        setTimeout(probe, 400);
      });
      request.on("error", () => {
        if (Date.now() - startedAt > timeoutMs) return reject(new Error(`Timed out waiting for ${url}`));
        setTimeout(probe, 400);
      });
    };
    probe();
  });
}

const buildIdPath = path.join(appRoot, ".next", "BUILD_ID");
if (!fs.existsSync(buildIdPath)) {
  throw new Error(`MoonRead build missing at ${buildIdPath}; run "npm run build" before "npm run test:reader"`);
}

let server;
let browser;
let baseUrl;
let serverOutput = "";
const unexpected = [];

before(async () => {
  const port = await getFreePort();
  baseUrl = `http://127.0.0.1:${port}`;
  server = spawn(
    process.execPath,
    [path.join(appRoot, "node_modules", "next", "dist", "bin", "next"), "start", "--hostname", "127.0.0.1", "--port", String(port)],
    { cwd: appRoot, windowsHide: true, stdio: ["ignore", "pipe", "pipe"] }
  );
  server.stdout.on("data", (chunk) => { serverOutput += chunk.toString(); });
  server.stderr.on("data", (chunk) => { serverOutput += chunk.toString(); });
  await waitForHttp(`${baseUrl}/`);
  browser = await chromium.launch({ executablePath: chromium.executablePath() });
});

after(async () => {
  if (browser) await browser.close().catch(() => {});
  if (server) {
    if (process.platform === "win32") {
      await new Promise((resolve) => {
        const cleanup = spawn("taskkill", ["/PID", String(server.pid), "/T", "/F"], { windowsHide: true });
        cleanup.once("close", resolve);
        cleanup.once("error", resolve);
      });
    } else if (server.exitCode === null) {
      await new Promise((resolve) => { server.once("close", resolve); server.kill(); });
    }
  }
  if (unexpected.length) console.error("Unexpected browser errors:", JSON.stringify(unexpected, null, 2));
  assert.deepEqual(unexpected, [], "every reader test must be free of unexpected browser errors or external requests");
});

async function withPage(viewport, fn, { seeded = true } = {}) {
  const context = await browser.newContext({ viewport, locale: "th-TH" });
  if (seeded) {
    await context.addInitScript(([key, payload]) => {
      try {
        if (!window.localStorage.getItem(key)) window.localStorage.setItem(key, payload);
      } catch {}
    }, [stateKey, JSON.stringify(seed)]);
  }
  await context.route("**/*", (route) => {
    let host = "";
    try { host = new URL(route.request().url()).hostname; } catch { host = ""; }
    const url = route.request().url();
    if (url.startsWith("http") && !["127.0.0.1", "localhost"].includes(host)) {
      unexpected.push({ kind: "external-request", url });
      return route.abort();
    }
    return route.continue();
  });
  const page = await context.newPage();
  page.on("pageerror", (error) => unexpected.push({ kind: "pageerror", text: String(error).slice(0, 200), url: page.url() }));
  page.on("console", (message) => {
    if (message.type() === "error") unexpected.push({ kind: "console", text: message.text().slice(0, 200), url: page.url() });
  });
  try {
    return await fn(page);
  } finally {
    await context.close();
  }
}

function storedState(page) {
  return page.evaluate((key) => JSON.parse(window.localStorage.getItem(key) || "{}"), stateKey);
}

function activeIn(page, selector) {
  return page.evaluate((sel) => {
    const target = document.querySelector(sel);
    return Boolean(target && document.activeElement === target);
  }, selector);
}

test("seeded store hydrates without page errors", async () => {
  const before = unexpected.length;
  await withPage({ width: 1440, height: 1000 }, async (page) => {
    await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
    const favOn = await page.locator(".book-card .fav.on").count();
    assert.equal(favOn, 1, "favorite from storage must render on home");

    await page.goto(`${baseUrl}/books/horror-game-developer`, { waitUntil: "networkidle" });
    const actions = (await page.locator(".detail-actions").innerText()).replace(/\n+/g, " | ");
    assert.match(actions, /อ่านต่อ ตอน 003/, "resume action must come from stored progress");
    assert.match(await page.locator(".detail-stats").innerText(), /42%/, "progress percent must come from stored progress");

    await page.goto(`${baseUrl}/history`, { waitUntil: "networkidle" });
    assert.ok((await page.locator(".history-grid .resume").count()) >= 1, "history must list stored progress");

    await page.goto(`${baseUrl}/shelf`, { waitUntil: "networkidle" });
    assert.ok((await page.locator(".book-card").count()) >= 1, "shelf must list stored favorite");
    assert.ok((await page.locator(".toc-list .ch-row").count()) >= 1, "shelf must list stored bookmark");
  });
  assert.deepEqual(unexpected.slice(before), [], "no hydration or console errors on seeded pages");
});

test("reader settings are restored on first load and survive edits", async () => {
  await withPage({ width: 1440, height: 1000 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch001`, { waitUntil: "networkidle" });
    const main = page.locator("main.reader-page");
    assert.match((await main.getAttribute("class")) || "", /theme-night/, "stored night theme must apply to the reader surface");
    const fontSize = await main.evaluate((el) => getComputedStyle(el).getPropertyValue("--reader-font-size").trim());
    assert.equal(fontSize, "22px", "stored font size must apply on first load");

    await page.locator('.reader-topbar button[aria-label="ตั้งค่าการอ่าน"]').click();
    const sheet = page.locator(".scrim .sheet");
    await sheet.waitFor({ state: "visible" });
    assert.equal(await sheet.locator(".font-option.selected .font-option-label").innerText(), "Noto Serif Thai");
    await sheet.getByRole("button", { name: "ซีเปีย" }).click();
    await sheet.locator(".font-option", { hasText: "Sarabun" }).click();
    assert.match((await main.getAttribute("class")) || "", /theme-sepia/, "theme change must update the surface");

    await page.reload({ waitUntil: "networkidle" });
    assert.match((await page.locator("main.reader-page").getAttribute("class")) || "", /theme-sepia/, "edited theme must persist after reload");

    const state = await storedState(page);
    assert.equal(state.reader.theme, "sepia");
    assert.equal(state.reader.fontFamily, "sarabun");
    assert.equal(state.progress["horror-game-developer"].percent, 42, "reader edits must not drop stored progress");
    assert.equal(state.bookmarks["horror-game-developer"].length, 1, "reader edits must not drop stored bookmarks");
    assert.deepEqual(state.favorites, ["horror-game-developer"], "reader edits must not drop favorites");
    assert.equal(state.reader.fontSize, 22, "unrelated reader fields must be preserved");
  });
});

test("site theme restores on reload and stays in sync with storage and label", async () => {
  await withPage({ width: 1440, height: 1000 }, async (page) => {
    await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
    const toggle = page.locator(".appbar-tools button");
    assert.equal(await toggle.getAttribute("aria-label"), "โหมดมืด");
    await toggle.click();
    assert.equal(await page.evaluate(() => document.documentElement.dataset.siteTheme), "dark");
    assert.equal(await toggle.getAttribute("aria-label"), "โหมดสว่าง");
    assert.equal(await page.evaluate(() => localStorage.getItem("moonread-site-theme")), "dark");

    await page.reload({ waitUntil: "networkidle" });
    await page.waitForTimeout(300);
    assert.equal(await page.evaluate(() => document.documentElement.dataset.siteTheme), "dark", "stored dark theme must be restored");
    assert.equal(await page.locator(".appbar-tools button").getAttribute("aria-label"), "โหมดสว่าง", "toggle label must match restored theme");
    await page.locator(".appbar-tools button").click();
    assert.equal(await page.evaluate(() => document.documentElement.dataset.siteTheme), "light");
    assert.equal(await page.evaluate(() => localStorage.getItem("moonread-site-theme")), "light");
  });
});

test("toc search matches padded and unpadded episode numbers exactly", async () => {
  await withPage({ width: 1440, height: 1000 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch001`, { waitUntil: "networkidle" });
    await page.locator('.reader-topbar button[aria-label="เปิดสารบัญ"]').click();
    const sheet = page.locator(".scrim .sheet");
    await sheet.waitFor({ state: "visible" });
    const input = sheet.locator('input[aria-label="ค้นหาตอน"]');
    for (const query of ["005", "0005", "5"]) {
      await input.fill(query);
      await page.waitForTimeout(150);
      assert.equal(await sheet.locator(".ch-row").count(), 1, `query ${query} must match exactly episode 5`);
      assert.match(await sheet.locator(".ch-row").innerText(), /005/);
    }
    await input.fill("หมอก");
    await page.waitForTimeout(150);
    assert.ok((await sheet.locator(".ch-row").count()) >= 1, "title substring must still match");
    await input.fill("");
    assert.equal(await sheet.locator(".ch-row").count(), 281, "blank query must show every chapter");

    await page.goto(`${baseUrl}/books/horror-game-developer`, { waitUntil: "networkidle" });
    const detailInput = page.locator('.toc-tools input[aria-label="ค้นหาตอน"]');
    for (const query of ["5", "005"]) {
      await detailInput.fill(query);
      await page.waitForTimeout(150);
      assert.equal(await page.locator(".toc-list .ch-row").count(), 1, `book toc query ${query} must match exactly episode 5`);
    }
  });
});

test("reader sheets trap focus, close on Escape and restore the opener", async () => {
  await withPage({ width: 1440, height: 1000 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch001`, { waitUntil: "networkidle" });
    const topbarSettings = '.reader-topbar button[aria-label="ตั้งค่าการอ่าน"]';
    await page.locator(topbarSettings).click();
    const settingsSheet = page.locator(".scrim .sheet");
    await settingsSheet.waitFor({ state: "visible" });
    assert.equal(await settingsSheet.getAttribute("role"), "dialog", "sheet must expose dialog role");
    assert.equal(await settingsSheet.getAttribute("aria-modal"), "true");
    assert.ok(await page.evaluate(() => {
      const sheet = document.querySelector(".scrim .sheet");
      return Boolean(sheet && sheet.contains(document.activeElement));
    }), "focus must move into the sheet on open");
    await page.keyboard.press("Escape");
    await page.waitForTimeout(150);
    assert.equal(await page.locator(".scrim .sheet").count(), 0, "Escape must close the sheet");
    assert.ok(await activeIn(page, topbarSettings), "focus must return to the settings button");

    const tocButton = '.reader-topbar button[aria-label="เปิดสารบัญ"]';
    await page.locator(tocButton).click();
    const tocSheet = page.locator(".scrim .sheet");
    await tocSheet.waitFor({ state: "visible" });
    for (let i = 0; i < 12; i += 1) {
      await page.keyboard.press("Tab");
      const inside = await page.evaluate(() => {
        const sheet = document.querySelector(".scrim .sheet");
        return Boolean(sheet && sheet.contains(document.activeElement));
      });
      assert.ok(inside, `Tab ${i + 1} must stay inside the sheet`);
    }
    const firstFocusable = await tocSheet.evaluate((sheet) => {
      const items = [...sheet.querySelectorAll('a[href],button:not([disabled]),input:not([disabled])')];
      items[0]?.focus();
      return items.length;
    });
    assert.ok(firstFocusable > 1);
    await page.keyboard.press("Shift+Tab");
    const wrapped = await page.evaluate(() => {
      const sheet = document.querySelector(".scrim .sheet");
      return Boolean(sheet && sheet.contains(document.activeElement));
    });
    assert.ok(wrapped, "Shift+Tab from the first control must wrap inside the sheet");
    await page.keyboard.press("Escape");
    assert.ok(await activeIn(page, tocButton), "focus must return to the TOC button");
  });

  await withPage({ width: 390, height: 844 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch001`, { waitUntil: "networkidle" });
    const fab = '.reader-fabs button[aria-label="ตั้งค่าการอ่าน"]';
    await page.locator(fab).click();
    await page.locator(".scrim .sheet").waitFor({ state: "visible" });
    await page.keyboard.press("Escape");
    await page.waitForTimeout(150);
    assert.ok(await activeIn(page, fab), "mobile FAB must regain focus after Escape");
  });
});
