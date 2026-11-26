import assert from "node:assert/strict";
import fs from "node:fs";
import http from "node:http";
import net from "node:net";
import path from "node:path";
import { spawn } from "node:child_process";
import { after, before, test } from "node:test";
import { fileURLToPath } from "node:url";
import { chromium, firefox, webkit } from "playwright";
import { chapterNumber, withNumberGaps } from "../lib/chapter-number.js";

const appRoot = fileURLToPath(new URL("..", import.meta.url));
const stateKey = "moonread-state-v1";
const dseManifest = JSON.parse(fs.readFileSync(path.join(appRoot, "content/generated/manifest.json"), "utf8"));
const engine = { chromium, firefox, webkit }[process.env.MOONREAD_BROWSER || "chromium"];
if (!engine) throw new Error("MOONREAD_BROWSER must be chromium, firefox, or webkit");

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
  try {
    await waitForHttp(`${baseUrl}/`);
  } catch (cause) {
    throw new Error(`MoonRead test server did not start (exit ${server.exitCode ?? "pending"}):\n${serverOutput.trim() || "No server output"}`, { cause });
  }
  browser = await engine.launch({ executablePath: engine.executablePath() });
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

async function withPage(viewport, fn, { seeded = true, hasTouch = false } = {}) {
  const context = await browser.newContext({ viewport, locale: "th-TH", hasTouch });
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

test("saved library shows loading instead of an empty state before hydration", async () => {
  await withPage({ width: 390, height: 844 }, async (page) => {
    let release;
    const held = new Promise((resolve) => { release = resolve; });
    await page.route("**/_next/static/**/*.js", async (route) => { await held; await route.continue(); });
    try {
      await page.goto(`${baseUrl}/history`, { waitUntil: "commit" });
      await page.getByText("กำลังโหลดประวัติการอ่าน…", { exact: true }).waitFor();
      assert.equal(await page.locator(".empty").count(), 0);
      // Settle the visible document's fonts before replacing it. JS stays held.
      await page.evaluate(() => document.fonts.ready.then(() => true));
      await page.goto(`${baseUrl}/shelf`, { waitUntil: "commit" });
      await page.getByText("กำลังโหลดที่คั่นตอน…", { exact: true }).waitFor();
      assert.equal(await page.locator(".empty").count(), 0);
      release();
      await page.locator(".mark-group a[href$='ch002?review=1']").waitFor();
      await page.evaluate(() => document.fonts.ready.then(() => true));
      await page.goto(`${baseUrl}/history`);
      await page.locator(".history-grid a[href$='ch003']").waitFor();
      await page.evaluate(() => document.fonts.ready.then(() => true));
    } finally { release(); }
  });
});

test("saved night palette is visible before the reader JavaScript loads", async () => {
  await withPage({ width: 390, height: 844 }, async (page) => {
    let release;
    const held = new Promise((resolve) => { release = resolve; });
    await page.route("**/_next/static/**/*.js", async (route) => { await held; await route.continue(); });
    try {
      await page.goto(`${baseUrl}/read/ch002`, { waitUntil: "commit" });
      await page.locator(".reader-page[data-reader-preparing]").waitFor();
      await page.waitForFunction(() => getComputedStyle(document.querySelector(".reader-page")).backgroundColor === "rgb(15, 22, 36)");
      assert.equal(await page.locator("html").getAttribute("data-initial-reader-theme"), "night");
      assert.equal(await page.locator(".settings-trigger").count(), 0);
      release();
      await page.locator(".reader-page.theme-night:not([data-reader-preparing])").waitFor();
      await page.getByRole("button", { name: "ตั้งค่าการอ่าน" }).click();
      await page.getByRole("button", { name: "กระดาษ" }).click();
      await page.waitForFunction(() => getComputedStyle(document.querySelector(".reader-page")).backgroundColor === "rgb(247, 240, 223)");
    } finally { release(); }
  });
});

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
    for (const query of ["005", "0005", "5", "ตอนที่ ๕"]) {
      await input.fill(query);
      await page.waitForTimeout(150);
      assert.equal(await sheet.locator(".ch-row").count(), 1, `query ${query} must match exactly episode 5`);
      assert.match(await sheet.locator(".ch-row").innerText(), /005/);
    }
    await input.fill("หมอก");
    await page.waitForTimeout(150);
    assert.ok((await sheet.locator(".ch-row").count()) >= 1, "title substring must still match");
    await input.fill("");
    assert.equal(await sheet.locator(".ch-row:not([data-gap])").count(), dseManifest.summary.available, "blank query must show every available chapter");

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
    const button = '.reader-topbar button[aria-label="ตั้งค่าการอ่าน"]';
    await page.locator(button).click();
    await page.locator(".scrim .sheet").waitFor({ state: "visible" });
    await page.keyboard.press("Escape");
    await page.waitForTimeout(150);
    assert.ok(await activeIn(page, button), "mobile settings button must regain focus after Escape");
  });
});

const horrorBook = "/books/horror-game-developer";

test("continue reading restores the passage after reload and viewport change", async () => {
  await withPage({ width: 390, height: 800 }, async (page) => {
    const href = `${horrorBook}/read/ch003`;
    await page.goto(`${baseUrl}${href}`, { waitUntil: "networkidle" });
    const block = 35;
    await page.evaluate((index) => {
      const rect = document.querySelector(".reader-article").children[index].getBoundingClientRect();
      window.scrollTo({ top: scrollY + rect.top - document.querySelector(".reader-topbar").offsetHeight, behavior: "instant" });
    }, block);
    const saved = () => page.waitForFunction(([key, index]) => JSON.parse(localStorage.getItem(key) || "{}").progress?.["horror-game-developer"]?.position?.block === index, [stateKey, block]);
    await saved();
    await page.goto(`${baseUrl}/history`);
    await page.locator(`.resume[href="${href}"]`).click();
    await page.waitForURL(`**${href}`);
    await page.setViewportSize({ width: 820, height: 900 });
    await page.reload({ waitUntil: "networkidle" });
    await page.waitForFunction((index) => {
      const bar = document.querySelector(".reader-topbar").offsetHeight;
      const rect = document.querySelector(".reader-article").children[index].getBoundingClientRect();
      return rect.top <= bar + 10 && rect.bottom > bar;
    }, block);
    await page.goto(`${baseUrl}${horrorBook}`, { waitUntil: "networkidle" });
    await page.getByRole("link", { name: "เริ่มใหม่จากตอนแรก" }).click();
    await page.waitForURL(`**${horrorBook}/read/ch001`);
    assert.equal(await page.evaluate(() => scrollY), 0);
  }, { seeded: false });
});

test("returning to the TOC preserves the passage for Back and book resume", async () => {
  await withPage({ width: 390, height: 800 }, async (page) => {
    const href = `${horrorBook}/read/ch003`;
    await page.goto(`${baseUrl}${href}`, { waitUntil: "networkidle" });
    const block = 35;
    await page.evaluate((index) => {
      const rect = document.querySelector(".reader-article").children[index].getBoundingClientRect();
      scrollTo({ top: scrollY + rect.top - document.querySelector(".reader-topbar").offsetHeight, behavior: "instant" });
    }, block);
    const leave = async () => {
      await page.getByRole("link", { name: "กลับไปสารบัญ" }).click();
      await page.waitForURL((url) => url.pathname === `${horrorBook}/chapters` && url.hash === "#chapter-ch003");
      await page.locator(".toc-list").waitFor();
      assert.equal((await storedState(page)).progress["horror-game-developer"].position.block, block);
    };
    const restored = () => page.waitForFunction((index) => {
      const bar = document.querySelector(".reader-topbar");
      const rect = document.querySelector(".reader-article")?.children[index]?.getBoundingClientRect();
      return rect && rect.top <= bar.offsetHeight + 10 && rect.bottom > bar.offsetHeight;
    }, block);
    await leave();
    await page.goBack();
    await page.waitForURL(`**${href}`);
    await restored();
    await leave();
    await page.goto(`${baseUrl}${horrorBook}`, { waitUntil: "networkidle" });
    await page.getByRole("link", { name: /อ่านต่อ ตอน 003/ }).click();
    await page.waitForURL(`**${href}`);
    await restored();
  }, { seeded: false });
});

test("Back after leaving via TOC restores the visible chapter, including a skip-link fragment", async () => {
  await withPage({ width: 390, height: 800 }, async (page) => {
    const chapter = `${horrorBook}/read/ch020`;
    const manifest = JSON.parse(fs.readFileSync(path.join(appRoot, "content/generated/books/horror-game-developer/manifest.json"), "utf8"));
    const title = manifest.chapters.find(({ href }) => href === chapter).title;
    await page.goto(`${baseUrl}${horrorBook}/read/ch019`, { waitUntil: "networkidle" });
    const contents = page.getByRole("button", { name: "เปิดสารบัญ" });
    await contents.click();
    await page.getByRole("dialog").locator(`a[href="${chapter}"]`).click();
    await page.waitForURL(`**${chapter}`);
    // The history entry updates before React commits the fetched chapter.
    await page.getByRole("heading", { level: 1, name: title, exact: true }).waitFor();
    await page.locator(".skip-content").focus();
    await page.keyboard.press("Enter");
    await page.waitForURL(`**${chapter}#main-content`);
    await page.waitForFunction(() => {
      const target = document.getElementById("main-content");
      const bar = document.querySelector(".reader-topbar");
      return document.activeElement === target && target.getBoundingClientRect().top >= bar.getBoundingClientRect().bottom;
    });
    await page.evaluate(() => scrollTo({ top: 2200, behavior: "instant" }));
    const block = await page.evaluate(() => {
      const inset = document.querySelector(".reader-topbar").offsetHeight + 8;
      return [...document.querySelector(".reader-article").children].findIndex((node) => node.getBoundingClientRect().bottom > inset);
    });
    assert.ok(block > 0, "the reader must be partway through the chapter before leaving");
    await page.getByRole("link", { name: "กลับไปสารบัญ" }).click();
    await page.waitForURL((url) => url.pathname === `${horrorBook}/chapters` && url.hash === "#chapter-ch020");
    await page.waitForFunction(() => document.activeElement?.id === "chapter-ch020");
    const saved = (await storedState(page)).progress["horror-game-developer"];
    assert.equal(saved?.chapterId, "ch020");
    assert.equal(saved?.position?.block, block);
    await page.goBack();
    await page.waitForURL(`**${chapter}#main-content`);
    await page.getByRole("heading", { level: 1, name: title, exact: true }).waitFor();
    await page.waitForFunction((index) => {
      const inset = (document.querySelector(".reader-topbar")?.offsetHeight ?? 0) + 8;
      const rect = document.querySelector(".reader-article")?.children[index]?.getBoundingClientRect();
      return scrollY > 2100 && rect?.top <= inset + 2 && rect.bottom > inset - 2;
    }, block);
    assert.match(await page.locator(".reader-kicker").textContent(), /020/);
  }, { seeded: false });
});

test("the focused TOC return row puts its bookmark and Discover next in keyboard order", async () => {
  await withPage({ width: 1440, height: 900 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch002`, { waitUntil: "networkidle" });
    await page.getByRole("link", { name: "กลับไปสารบัญ" }).press("Enter");
    await page.waitForURL("**/chapters?range=1#chapter-ch002");
    const exit = page.getByRole("link", { name: "ค้นพบเรื่องอื่น" });
    await exit.waitFor();
    await page.waitForFunction(() => document.activeElement?.id === "chapter-ch002");
    await page.keyboard.press("Tab");
    assert.equal(await page.getByRole("button", { name: "คั่นหน้า ตอน 002" }).evaluate((button) => document.activeElement === button), true);
    await page.keyboard.press("Tab");
    assert.equal(await exit.evaluate((link) => document.activeElement === link), true);
    await page.keyboard.press("Enter");
    await page.waitForURL(`${baseUrl}/`);
    await page.locator('.rail a[href="/read/ch002"]').waitFor();
    assert.equal(await page.evaluate(() => scrollY), 0);
  }, { seeded: false });
});

test("auto advance is opt-in and opening settings cancels the countdown", async () => {
  await withPage({ width: 390, height: 840 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch001`, { waitUntil: "networkidle" });
    const settings = page.getByRole("button", { name: "ตั้งค่าการอ่าน" });
    await settings.click();
    const toggle = page.getByRole("button", { name: "เลื่อนตอนถัดไปอัตโนมัติ" });
    assert.equal(await toggle.getAttribute("aria-pressed"), "false");
    assert.equal(await page.getByRole("slider", { name: "ขนาดตัวอักษร" }).count(), 1);
    await toggle.click();
    await page.keyboard.press("Escape");
    await page.evaluate(() => scrollTo({ top: document.documentElement.scrollHeight, behavior: "instant" }));
    await page.getByRole("button", { name: "ยกเลิก" }).waitFor();
    await settings.click();
    await page.waitForTimeout(5300);
    assert.ok(page.url().endsWith("/read/ch001"), "settings must not be dismissed by auto advance");
    assert.equal(await page.getByRole("dialog").isVisible(), true);
    await page.keyboard.press("Escape");
    await page.locator(".reader-end").getByRole("link", { name: "อ่านต่อ" }).click();
    await page.waitForURL("**/read/ch002");
  }, { seeded: false });
});

test("a failed chapter request keeps the current passage and can be retried", async () => {
  await withPage({ width: 320, height: 800 }, async (page) => {
    const next = `${horrorBook}/read/ch020`;
    await page.goto(`${baseUrl}${horrorBook}/read/ch019`, { waitUntil: "networkidle" });
    await page.evaluate(() => scrollTo({ top: 1200, behavior: "instant" }));
    const y = await page.evaluate(() => scrollY);
    await page.getByRole("button", { name: "เปิดสารบัญ" }).click();
    const panel = page.getByRole("dialog");
    const current = panel.locator('[aria-current="page"]');
    assert.equal(await current.evaluate((row) => {
      const viewport = row.parentElement.getBoundingClientRect();
      const rect = row.getBoundingClientRect();
      return rect.top >= viewport.top && rect.bottom <= viewport.bottom;
    }), true);
    await page.mouse.move(3, 200);
    await page.mouse.wheel(0, 500);
    await panel.getByRole("textbox", { name: "ค้นหาตอน" }).fill("๒๐");
    const data = "**/reader-data/horror-game-developer/ch020";
    await page.route(data, async (route) => route.fulfill({ status: 503, body: "Unavailable" }));
    // An expected network failure is not a page runtime exception.
    const beforeErrors = unexpected.length;
    await panel.locator(`a[href="${next}"]`).click();
    const retry = page.getByRole("button", { name: "ลองอีกครั้ง" });
    await retry.waitFor();
    assert.equal(await panel.getByRole("textbox", { name: "ค้นหาตอน" }).inputValue(), "๒๐");
    assert.match(await panel.getByRole("alert").textContent(), /เปิดหน้าไม่ได้.*20/);
    const errors = unexpected.splice(beforeErrors);
    assert.ok(errors.every((error) => error.kind === "console" && /503/.test(error.text)));
    assert.ok(page.url().endsWith("/ch019"));
    assert.equal(await page.evaluate(() => scrollY), y);
    await page.unroute(data);
    await retry.click();
    await page.waitForURL(`**${next}`);
    await page.waitForFunction(() => document.activeElement === document.querySelector("h1"));
    await page.goBack();
    await page.waitForURL("**/read/ch019");
    await page.waitForFunction(() => document.querySelector(".reader-kicker").textContent.includes("019") && scrollY > 1000);
    await page.goForward();
    await page.waitForFunction(() => document.querySelector(".reader-kicker").textContent.includes("020"));
  }, { seeded: false });
});

test("printed Deep Sea Embers numbers agree with search without changing stable links", async () => {
  const synthetic = Object.freeze({ number: 145, title: "บทที่ ๑๔๖: ทดสอบ", href: "/read/ch145" });
  assert.equal(chapterNumber(synthetic), 146, "the displayed number is independent of the stable path");
  assert.equal(synthetic.href, "/read/ch145");
  await withPage({ width: 390, height: 800 }, async (page) => {
    await page.goto(`${baseUrl}/chapters`, { waitUntil: "networkidle" });
    await page.getByRole("searchbox", { name: "ค้นหาตอน" }).fill("บทที่ ๑๕");
    const chapter = page.locator(".toc-list .chapter-link");
    assert.equal(await chapter.getAttribute("href"), "/read/ch015");
    assert.equal(await chapter.locator(".num").textContent(), "015");
    await chapter.click();
    await page.waitForURL("**/read/ch015");
    assert.match(await page.locator(".reader-kicker").textContent(), /015/);
    await page.getByRole("button", { name: "เปิดสารบัญ" }).click();
    await page.getByRole("textbox", { name: "ค้นหาตอน" }).fill("15");
    assert.equal(await page.locator('.sheet-toc .ch-row[aria-current="page"]').getAttribute("href"), "/read/ch015");
  }, { seeded: false });
});

test("long contents show a manageable range but search all published chapters", async () => {
  await withPage({ width: 390, height: 800 }, async (page) => {
    const longBook = "/books/investing-in-my-crippled-wife";
    const manifest = JSON.parse(fs.readFileSync(path.join(appRoot, `content/generated${longBook}/manifest.json`), "utf8"));
    const last = manifest.chapters.filter((chapter) => chapter.status === "available").at(-1);
    await page.goto(`${baseUrl}${longBook}/chapters`, { waitUntil: "networkidle" });
    const rows = page.locator(".toc-list .ch-row");
    assert.equal(await rows.count(), 50);
    await page.getByRole("combobox", { name: "เรียงตอน" }).selectOption("recent");
    assert.equal(await rows.first().locator(".chapter-link").getAttribute("href"), last.href);
    assert.equal(await rows.count(), (chapterNumber(last) - 1) % 50 + 1);
    await page.getByRole("searchbox", { name: "ค้นหาตอน" }).fill("๑๕");
    assert.equal(await rows.count(), 1);
    assert.equal(await rows.first().locator(".chapter-link").getAttribute("href"), `${longBook}/read/ch015`);
  }, { seeded: false });
});

test("search and contents restore results and the visible page after Back", async () => {
  for (const width of [390, 1366]) {
    await withPage({ width, height: 844 }, async (page) => {
      await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
      const search = page.locator(".hero-search input");
      await search.fill("Horror");
      await search.press("Enter");
      await page.waitForURL((url) => url.searchParams.get("q") === "Horror" && url.hash === "#catalog");
      await page.locator(`#catalog .book-card a[href="${horrorBook}"]`).click();
      await page.waitForURL(`**${horrorBook}`);
      await page.evaluate(() => document.fonts.ready.then(() => true));
      await page.goBack();
      assert.equal(await search.inputValue(), "Horror");
      assert.equal(await page.locator("#catalog .book-card a").count(), 1);
      // Verify restored results with their actual fonts before navigating away.
      await page.evaluate(() => document.fonts.ready.then(() => true));
      await page.goForward();
      await page.locator(".detail-info h1").waitFor();
      await page.evaluate(() => document.fonts.ready.then(() => true));
      await page.goto(`${baseUrl}${horrorBook}/chapters`, { waitUntil: "networkidle" });
      const toc = page.getByRole("searchbox", { name: "ค้นหาตอน" });
      await page.getByRole("combobox", { name: "เรียงตอน" }).selectOption("recent");
      await page.waitForURL((url) => url.searchParams.get("order") === "recent");
      await toc.fill("๒๐");
      await page.waitForURL((url) => url.searchParams.get("order") === "recent" && url.searchParams.get("chapter") === "๒๐");
      await toc.press("Enter");
      await page.waitForURL("**/read/ch020");
      await page.goBack();
      await page.waitForURL((url) => url.searchParams.get("order") === "recent" && url.searchParams.get("chapter") === "๒๐");
      await page.waitForFunction(() => document.activeElement?.getAttribute("href")?.endsWith("/read/ch020"));
      await page.waitForFunction(() => document.querySelector(".toc-tools select")?.value === "recent");
      assert.equal(await toc.inputValue(), "๒๐");
      assert.equal(await page.getByRole("combobox", { name: "เรียงตอน" }).inputValue(), "recent");
    }, { seeded: false });
  }
});

test("reader keeps the visible paragraph when settings and viewport reflow", async () => {
  await withPage({ width: 390, height: 844 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch002`, { waitUntil: "networkidle" });
    const visible = () => page.evaluate(() => {
      const inset = document.querySelector(".reader-topbar").offsetHeight + 8;
      return [...document.querySelector(".reader-article").children].findIndex((el) => el.getBoundingClientRect().bottom > inset);
    });
    await page.evaluate(() => scrollTo({ top: 4200, behavior: "instant" }));
    const before = await visible();
    await page.getByRole("button", { name: "ตั้งค่าการอ่าน" }).click();
    await page.getByRole("slider", { name: "ขนาดตัวอักษร" }).press("End");
    await page.getByRole("slider", { name: "ระยะบรรทัด" }).press("End");
    await page.keyboard.press("Escape");
    assert.ok(Math.abs((await visible()) - before) <= 1);
    await page.setViewportSize({ width: 520, height: 844 });
    await page.waitForFunction((expected) => {
      const inset = document.querySelector(".reader-topbar").offsetHeight + 8;
      const idx = [...document.querySelector(".reader-article").children].findIndex((el) => el.getBoundingClientRect().bottom > inset);
      return Math.abs(idx - expected) <= 1;
    }, before);
  }, { seeded: false });
});

test("reading progress and the Thai history title stay consistent after typography changes", async () => {
  await withPage({ width: 390, height: 664 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch001`, { waitUntil: "networkidle" });
    await page.evaluate(() => {
      const paragraph = document.querySelectorAll(".reader-article .reader-paragraph")[3].getBoundingClientRect();
      const inset = document.querySelector(".reader-topbar").offsetHeight + 8;
      scrollTo({ top: scrollY + paragraph.top + paragraph.height / 3 - inset, behavior: "instant" });
    });
    await page.waitForFunction(() => parseInt(document.querySelector(".reader-progress-value").textContent, 10) > 0);
    const before = await page.locator(".reader-progress-value").textContent();
    await page.getByRole("button", { name: "ตั้งค่าการอ่าน" }).click();
    await page.getByRole("button", { name: /Noto Serif Thai/ }).click();
    const size = page.getByRole("slider", { name: "ขนาดตัวอักษร" });
    await size.press("End");
    for (let i = 0; i < 3; i++) await size.press("ArrowLeft");
    await page.keyboard.press("Escape");
    await page.evaluate(async () => { await document.fonts.ready; await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))); });
    assert.equal(await page.locator(".reader-progress-value").textContent(), before);
    await page.goto(`${baseUrl}/history`, { waitUntil: "networkidle" });
    const entry = page.locator('.resume[href="/read/ch001"]');
    assert.equal(await entry.locator(".t").textContent(), "เถ้าถ่านแห่งทะเลลึก");
    assert.equal(await entry.locator(".progress-row > span").first().textContent(), before);
    await entry.click();
    await page.waitForURL("**/read/ch001");
    await page.waitForFunction((expected) => document.querySelector(".reader-progress-value")?.textContent === expected, before);
  }, { seeded: false });
});

test("reading progress stays visible beside a long title on narrow screens", async () => {
  for (const width of [320, 390]) {
    await withPage({ width, height: 800 }, async (page) => {
      await page.goto(`${baseUrl}/books/a-gacha-addicts-fusionpunk-life/read/ch072`, { waitUntil: "networkidle" });
      await page.evaluate(() => scrollTo({ top: 1800, behavior: "instant" }));
      await page.waitForFunction(() => {
        const value = document.querySelector(".reader-progress-value");
        if (!value || parseInt(value.textContent, 10) <= 0) return false;
        const bounds = value.getBoundingClientRect();
        const panel = value.closest(".reader-top-title").getBoundingClientRect();
        return bounds.left >= panel.left && bounds.right <= panel.right + 1 && value.scrollWidth <= value.clientWidth + 1;
      });
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), width);
    }, { seeded: false });
  }
});

test("explicit search supports the displayed author and offers close title suggestions", async () => {
  await withPage({ width: 1366, height: 900 }, async (page) => {
    await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
    const header = page.locator(".appbar-search input");
    await header.fill("Yuan Tong");
    await header.press("Enter");
    await page.waitForFunction(() => document.activeElement?.id === "catalog-title");
    assert.equal(await page.locator("#catalog .book-card a").getAttribute("href"), "/book");
    await page.keyboard.press("Tab");
    assert.equal(await page.evaluate(() => document.activeElement?.getAttribute("href")), "/book");
    const search = page.locator(".hero-search input");
    await search.fill("Deep Sea Embres");
    assert.equal(await page.getByRole("region", { name: "เรื่องที่ชื่อใกล้เคียง" }).locator(".book-card a").getAttribute("href"), "/book");
  }, { seeded: false });
});

test("catalog restores the selected genre and order when returning from a story", async () => {
  await withPage({ width: 390, height: 844 }, async (page) => {
    await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
    const filters = page.locator(".catalog-filters");
    await filters.locator("summary").click();
    await page.getByRole("combobox", { name: "เรียงลำดับ" }).selectOption("chapters");
    await page.getByRole("button", { name: "แฟนตาซี", exact: true }).click();
    await page.waitForURL((url) => url.searchParams.get("genre") === "แฟนตาซี" && url.searchParams.get("sort") === "chapters");
    await page.getByRole("button", { name: /^แสดง \d+ เรื่อง$/ }).click();
    const links = page.locator("#catalog .book-card a");
    const before = await links.evaluateAll((items) => items.map((item) => item.getAttribute("href")));
    assert.ok(before.length > 0 && before.length < 8);
    await links.first().click();
    await page.locator(".detail-info h1").waitFor();
    await page.evaluate(() => document.fonts.ready.then(() => true));
    await page.goBack({ waitUntil: "domcontentloaded" });
    await page.waitForURL((url) => url.pathname === "/" && url.searchParams.get("genre") === "แฟนตาซี" && url.searchParams.get("sort") === "chapters");
    await links.first().waitFor({ state: "visible" });
    assert.deepEqual(await links.evaluateAll((items) => items.map((item) => item.getAttribute("href"))), before);
    if (await filters.getAttribute("open") === null) await filters.locator("summary").click();
    assert.equal(await page.getByRole("combobox", { name: "เรียงลำดับ" }).inputValue(), "chapters");
    assert.equal(await page.getByRole("button", { name: "แฟนตาซี", exact: true }).getAttribute("aria-pressed"), "true");
  }, { seeded: false });
});

test("reader clearly shows controls loading and the first available tap opens settings", async () => {
  await withPage({ width: 390, height: 844 }, async (page) => {
    let release;
    const held = new Promise((resolve) => { release = resolve; });
    await page.route("**/_next/static/**/*.js", async (route) => { await held; await route.continue(); });
    try {
      await page.goto(`${baseUrl}/read/ch003`, { waitUntil: "commit" });
      await page.locator(".reader-controls-loading").waitFor();
      assert.equal(await page.locator(".settings-trigger").count(), 0);
      release();
      await page.locator(".settings-trigger").click();
      await page.getByRole("dialog").waitFor();
    } finally { release(); }
  }, { seeded: false });
});

test("chapter search submits and shows server results before JavaScript is ready", async () => {
  await withPage({ width: 390, height: 844 }, async (page) => {
    const book = "/books/a-gacha-addicts-fusionpunk-life";
    let release;
    const held = new Promise((resolve) => { release = resolve; });
    await page.route("**/_next/static/**/*.js", async (route) => { await held; await route.continue(); });
    try {
      await page.goto(`${baseUrl}${book}`, { waitUntil: "commit" });
      const field = page.getByRole("searchbox", { name: "ค้นหาตอน" });
      await field.waitFor();
      assert.equal(await field.isEnabled(), true);
      assert.ok(await page.locator('.toc-list a[href]').count() > 0);
      await field.fill("075");
      await field.press("Enter");
      await page.waitForURL((url) => url.searchParams.get("chapter") === "075", { waitUntil: "commit" });
      const result = page.locator(`.toc-list a[href="${book}/read/ch075"]`);
      await result.waitFor();
      assert.equal(await page.locator(".toc-list a[href]").count(), 1);
      assert.equal(await field.inputValue(), "075");
      assert.equal(await page.getByRole("combobox", { name: "เรียงตอน" }).isDisabled(), true);
      release();
      await page.waitForFunction(() => !document.querySelector('.toc-tools select').disabled);
      assert.equal(await field.inputValue(), "075");
      await result.click();
      await page.waitForURL(`**${book}/read/ch075`);
    } finally { release(); }
  }, { seeded: false });
});

test("keyboard page scrolling keeps a reading overlap and Tab finds the visible end action", async () => {
  await withPage({ width: 1440, height: 900 }, async (page) => {
    await page.goto(`${baseUrl}/books/ten-day-ultimatum/read/ch001`, { waitUntil: "networkidle" });
    const original = 2000;
    await page.evaluate((y) => scrollTo({ top: y, behavior: "instant" }), original);
    await page.keyboard.press("PageDown");
    const viewport = await page.evaluate(() => ({
      y: scrollY, height: innerHeight, bar: document.querySelector(".reader-topbar").offsetHeight,
      line: parseFloat(getComputedStyle(document.querySelector(".reader-article")).lineHeight),
    }));
    assert.ok(viewport.y > original + 400);
    assert.ok(viewport.height - viewport.bar - (viewport.y - original) >= viewport.line * 2 - 1);
    await page.keyboard.press("PageUp");
    assert.ok(Math.abs(await page.evaluate(() => scrollY) - original) <= 1);
    await page.keyboard.press("End");
    const action = page.locator(".reader-end a.primary");
    await page.waitForFunction(() => document.querySelector(".reader-end a.primary")?.getBoundingClientRect().bottom <= innerHeight);
    await page.keyboard.press("Tab");
    assert.equal(await action.evaluate((el) => el === document.activeElement), true);
    await page.keyboard.press("Enter");
    await page.waitForURL("**/read/ch002");
  }, { seeded: false });
});

test("keyboard readers can return from the chapter footer to sticky tools without scrolling", async () => {
  await withPage({ width: 1440, height: 900 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch001`, { waitUntil: "networkidle" });
    await page.keyboard.press("End");
    await page.waitForFunction(() => document.documentElement.scrollHeight - innerHeight - scrollY < 2);
    await page.keyboard.press("Tab");
    assert.equal(await activeIn(page, ".reader-end a.primary"), true);
    await page.keyboard.press("Tab");
    assert.equal(await activeIn(page, ".reader-bottom-nav a.next"), true);
    await page.keyboard.press("Tab");
    assert.equal(await activeIn(page, ".reader-tools-return a"), true);
    const bottom = await page.evaluate(() => scrollY);
    await page.keyboard.press("Enter");
    assert.equal(await activeIn(page, "#reader-tools"), true);
    assert.equal(await page.evaluate(() => scrollY), bottom);
    await page.keyboard.press("Tab");
    assert.equal(await activeIn(page, ".reader-top-actions button:first-child"), true);
  }, { seeded: false });
});

test("mobile menu opens the top of the shelf and home pages", async () => {
  await withPage({ width: 412, height: 839 }, async (page) => {
    await page.goto(`${baseUrl}/?q=Horror#catalog`, { waitUntil: "networkidle" });
    await page.locator('.botnav a[href="/shelf"]').click();
    await page.waitForURL("**/shelf");
    assert.equal(await page.evaluate(() => scrollY), 0);
    assert.equal(await page.evaluate(() => document.querySelector(".shelf-heading .more").getBoundingClientRect().top > document.querySelector(".appbar").getBoundingClientRect().bottom), true);
    await page.locator(".appbar .brand").click();
    await page.waitForURL(`${baseUrl}/`);
    assert.equal(await page.evaluate(() => scrollY), 0);
    assert.equal(await page.evaluate(() => document.querySelector(".hero h1").getBoundingClientRect().top > document.querySelector(".appbar").getBoundingClientRect().bottom), true);
  }, { seeded: false });
});

test("Tab after keyboard chapter navigation keeps the reader at the new chapter heading", async () => {
  await withPage({ width: 1440, height: 900 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch002`, { waitUntil: "networkidle" });
    await page.locator(".reader-quick-next").press("Enter");
    await page.waitForURL("**/read/ch003");
    await page.waitForFunction(() => document.activeElement === document.querySelector(".reader-head h1"));
    await page.keyboard.press("Tab");
    assert.ok(await page.evaluate(() => document.querySelector(".reader-topbar").contains(document.activeElement)));
    assert.ok(await page.evaluate(() => scrollY < 100));
  }, { seeded: false });
});

test("printed chapter gaps stay non-navigable, and Enter jumps to an available chapter", async () => {
  const catalog = [{ id: "ch099", number: 99, title: "บทที่ 99: ก่อน", href: "/read/ch099" }, { id: "ch100", number: 100, title: "บทที่ 101: หลัง", href: "/read/ch100" }];
  assert.deepEqual(withNumberGaps(catalog), [catalog[0], { id: "gap-100", number: 100, title: "", status: "missing", inferredGap: true }, catalog[1]]);
  await withPage({ width: 390, height: 800 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch019`, { waitUntil: "networkidle" });
    await page.getByRole("button", { name: "เปิดสารบัญ" }).click();
    const input = page.getByRole("dialog").getByRole("textbox", { name: "ค้นหาตอน" });
    await input.fill("๒๐");
    await input.press("Enter");
    await page.waitForURL("**/read/ch020");
    assert.match(await page.locator(".reader-kicker").textContent(), /020/);
  }, { seeded: false });
});

test("home search follows the URL, Back, and narrow history does not overflow", async () => {
  await withPage({ width: 1280, height: 900 }, async (page) => {
    await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
    const header = page.locator(".appbar-search input");
    for (const [query, href] of [["horror game developer", horrorBook], ["deep sea embers", "/book"]]) {
      await header.fill(query);
      await header.press("Enter");
      await page.waitForURL((url) => url.searchParams.get("q") === query);
      await page.locator(`.book-card a[href="${href}"]`).waitFor();
      assert.equal(await page.locator(".book-card").count(), 1);
    }
    await page.goBack();
    await page.locator('.book-card a[href*="horror-game-developer"]').waitFor();
    const local = page.locator(".hero-search input");
    await local.fill("คำค้นไม่อยู่ในคลัง123");
    await page.getByRole("heading", { name: "ไม่พบนิยายที่ค้นหา" }).waitFor();
    await page.reload();
    await page.getByRole("heading", { name: "ไม่พบนิยายที่ค้นหา" }).waitFor();
    await page.setViewportSize({ width: 320, height: 800 });
    await page.goto(`${baseUrl}/history`, { waitUntil: "networkidle" });
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), 320);
  });
});

test("the catalog and query results are available without JavaScript", async () => {
  const context = await browser.newContext({ javaScriptEnabled: false, viewport: { width: 390, height: 844 } });
  try {
    const page = await context.newPage();
    await page.goto(`${baseUrl}/`);
    assert.ok(await page.locator(".book-card a").count() > 1);
    await page.locator(".hero-search input").fill("horror game developer");
    await page.getByRole("button", { name: "ไปยังผลการค้นหา" }).click();
    await page.waitForURL("**/?q=*#catalog");
    assert.equal(await page.locator(".book-card a").count(), 1);
    assert.equal(await page.locator(".book-card a").getAttribute("href"), horrorBook);
  } finally { await context.close(); }
});

test("mobile discovery and book detail keep the first decision visible", async () => {
  for (const viewport of [{ width: 320, height: 667 }, { width: 390, height: 844 }]) {
    await withPage(viewport, async (page) => {
      await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
      const firstTitle = await page.locator(".book-card .t").first().boundingBox();
      const nav = await page.locator(".botnav").boundingBox();
      assert.ok(firstTitle.y + firstTitle.height < nav.y, "at least the first book title must be visible above the mobile menu");
      await page.locator(".catalog-filters summary").click();
      const chips = page.locator(".catalog-filters button.chip");
      const count = await chips.count();
      await chips.first().focus();
      for (let index = 0; index < count; index++) {
        await page.waitForFunction(() => document.activeElement.getBoundingClientRect().bottom <= document.querySelector(".botnav").getBoundingClientRect().top);
        await page.keyboard.press("Tab");
      }
      await page.goto(`${baseUrl}${horrorBook}`, { waitUntil: "networkidle" });
      const read = await page.getByRole("link", { name: "เริ่มอ่าน" }).boundingBox();
      const synopsis = await page.locator(".detail-preview").boundingBox();
      assert.ok(synopsis.y < read.y && read.y + read.height < nav.y);
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), viewport.width);
    }, { seeded: false });
  }
});

test("a search typed before hydration survives and submits the visible value", async () => {
  await withPage({ width: 390, height: 800 }, async (page) => {
    let release;
    const held = new Promise((resolve) => { release = resolve; });
    await page.route("**/_next/static/**/*.js", async (route) => { await held; await route.continue(); });
    try {
      await page.goto(`${baseUrl}/`, { waitUntil: "commit" });
      const field = page.locator(".hero-search input");
      await field.fill("คำขาด");
      release();
      await page.waitForLoadState("networkidle");
      assert.equal(await field.inputValue(), "คำขาด");
      await field.press("Enter");
      await page.waitForURL((url) => url.searchParams.get("q") === "คำขาด" && url.hash === "#catalog");
      assert.equal(await page.locator("#catalog .book-card a").getAttribute("href"), "/books/ten-day-ultimatum");
    } finally { release(); }
  }, { seeded: false });
});

test("opening book bookmarks on a short touch viewport clears the bottom navigation", async () => {
  await withPage({ width: 390, height: 664 }, async (page) => {
    await page.goto(`${baseUrl}${horrorBook}`, { waitUntil: "networkidle" });
    const marks = page.getByRole("button", { name: "ที่คั่น (1)" });
    await marks.scrollIntoViewIfNeeded();
    await marks.evaluate((button) => {
      const nav = document.querySelector(".botnav").getBoundingClientRect();
      scrollBy({ top: button.getBoundingClientRect().bottom - nav.top + 8, behavior: "instant" });
    });
    await marks.tap();
    const bookmark = page.locator(`.toc-list a[href="${horrorBook}/read/ch002?review=1"]`);
    assert.equal(await bookmark.evaluate((link) => {
      const row = link.getBoundingClientRect();
      const toolbar = document.querySelector(".appbar").getBoundingClientRect();
      const menu = document.querySelector(".botnav").getBoundingClientRect();
      return row.top >= toolbar.bottom && row.bottom <= menu.top && link.contains(document.elementFromPoint(row.x + row.width / 2, row.y + row.height / 2));
    }), true, "the saved chapter must be tappable before Playwright can scroll it into view");
    await bookmark.tap();
    await page.waitForURL(`**${horrorBook}/read/ch002?review=1`);
    await page.locator(".reader-review").waitFor();
  }, { hasTouch: true });
});

test("book and full contents share touch bookmarks and show complete chapter titles", async () => {
  await withPage({ width: 375, height: 590 }, async (page) => {
    await page.goto(`${baseUrl}/book#book-contents`, { waitUntil: "networkidle" });
    const titles = await page.locator(".toc-list .ct strong").evaluateAll((elements) => elements.slice(1, 4).map((title) => {
      const range = document.createRange();
      range.selectNodeContents(title);
      const box = title.getBoundingClientRect();
      const row = title.closest(".ch-row").getBoundingClientRect();
      const lines = [...range.getClientRects()];
      // Thai font metrics can extend past a line box without clipping the text.
      return { lines: lines.length, fits: getComputedStyle(title).overflow === "visible" && lines.every((line) => line.right <= box.right + 1 && line.top >= row.top && line.bottom <= row.bottom) };
    }));
    assert.equal(titles.length, 3);
    assert.ok(titles.every(({ fits }) => fits));
    assert.ok(titles.some(({ lines }) => lines > 1), "the mobile fixture must include a wrapped title");

    const saved = page.getByRole("button", { name: "คั่นหน้า ตอน 003" });
    await saved.tap();
    assert.equal(await saved.getAttribute("aria-pressed"), "true");
    await page.locator('.chapter-link[href="/read/ch002"]').tap();
    await page.waitForURL("**/read/ch002");
    await page.getByRole("link", { name: "กลับไปสารบัญ" }).tap();
    await page.waitForURL("**/chapters?range=1#chapter-ch002");
    await page.waitForFunction(() => document.activeElement?.id === "chapter-ch002");
    assert.equal(await saved.getAttribute("aria-pressed"), "true");
    const another = page.getByRole("button", { name: "คั่นหน้า ตอน 004" });
    await another.tap();
    assert.equal(await another.getAttribute("aria-pressed"), "true");
    assert.ok(page.url().includes("/chapters?"), "bookmarking must not navigate to the chapter");
    await page.locator('.botnav a[href="/shelf"]').tap();
    await page.locator('.mark-group a[href="/read/ch004?review=1"]').waitFor();
  }, { seeded: false, hasTouch: true });
});

test("the first touch on the sticky bookmark confirms the saved passage", async () => {
  await withPage({ width: 375, height: 590 }, async (page) => {
    await page.goto(`${baseUrl}/read/ch001`, { waitUntil: "networkidle" });
    await page.evaluate(() => scrollTo({ top: 1400, behavior: "instant" }));
    const bookmark = page.getByRole("button", { name: "คั่นหน้า" });
    const bounds = await bookmark.boundingBox();
    assert.ok(bounds && bounds.y >= 0 && bounds.y + bounds.height <= 590);
    const { x, y } = { x: bounds.x + bounds.width / 2, y: bounds.y + bounds.height / 2 };
    const before = await page.evaluate(() => scrollY);
    await page.touchscreen.tap(x, y);
    const notice = page.locator(".reader-bookmark-notice");
    await notice.filter({ hasText: /^คั่นตอนแล้ว$/ }).waitFor();
    assert.equal(await bookmark.getAttribute("aria-pressed"), "true");
    assert.equal(await page.evaluate(() => scrollY), before);
    const state = await storedState(page);
    assert.ok(state.bookmarks["deep-sea-embers"][0].position.block > 0);
    await page.touchscreen.tap(x, y);
    await notice.filter({ hasText: /^นำที่คั่นออกแล้ว$/ }).waitFor();
    assert.equal(await bookmark.getAttribute("aria-pressed"), "false");
    assert.deepEqual((await storedState(page)).bookmarks["deep-sea-embers"], []);
  }, { seeded: false, hasTouch: true });
});

test("opening a bookmark without other progress starts a saved reading session", async () => {
  await withPage({ width: 375, height: 620 }, async (page) => {
    await page.goto(`${baseUrl}/book#book-contents`, { waitUntil: "networkidle" });
    await page.locator(".toc-list .ch-star").first().tap();
    await page.getByRole("button", { name: "ที่คั่น (1)" }).tap();
    const bookmark = page.locator('.toc-list a[href="/read/ch001?bookmark=1"]');
    assert.match(await bookmark.textContent(), /อ่านจากที่คั่น/);
    await bookmark.tap();
    await page.waitForURL(`${baseUrl}/read/ch001`);
    assert.equal(await page.locator(".reader-review").count(), 0);
    await page.locator(".reader-quick-next").tap();
    await page.waitForURL(`${baseUrl}/read/ch002`);
    // A touch on a cold chapter can take the native link instead of the
    // enhanced transition. Wait for the new chapter, not keyboard focus.
    await page.locator(".reader-kicker").filter({ hasText: "002" }).waitFor();
    await page.getByRole("button", { name: "คั่นหน้า" }).waitFor();
    await page.evaluate(() => scrollTo({ top: 1000, behavior: "instant" }));
    await page.waitForFunction(() => parseInt(document.querySelector(".reader-progress-value")?.textContent, 10) > 0);
    await page.goto(`${baseUrl}/history`);
    await page.locator('.resume[href="/read/ch002"]').tap();
    await page.waitForFunction(() => scrollY > 950);
  }, { seeded: false, hasTouch: true });
});

test("reviewing another bookmarked chapter can deliberately move the saved position", async () => {
  await withPage({ width: 320, height: 640 }, async (page) => {
    await page.goto(`${baseUrl}/shelf`, { waitUntil: "networkidle" });
    const href = `${horrorBook}/read/ch002`;
    const bookmark = page.locator(`a[href="${href}?review=1"]`);
    assert.match(await bookmark.textContent(), /อ่านทวน · เก็บจุดอ่านเดิม/);
    await bookmark.click();
    await page.locator(".reader-review").waitFor();
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth), 320);
    await page.evaluate(() => scrollTo({ top: 1400, behavior: "instant" }));
    assert.equal((await storedState(page)).progress["horror-game-developer"].chapterId, "ch003");
    const visibleBlock = () => page.evaluate(() => {
      const inset = document.querySelector(".reader-topbar").offsetHeight + 8;
      return [...document.querySelector(".reader-article").children].findIndex((node) => node.getBoundingClientRect().bottom > inset);
    });
    const block = await visibleBlock();
    await page.getByRole("button", { name: "บันทึกจุดอ่านที่นี่" }).click();
    await page.waitForURL(`${baseUrl}${href}`);
    await page.locator(".reader-review").waitFor({ state: "detached" });
    assert.equal((await storedState(page)).progress["horror-game-developer"].chapterId, "ch002");
    assert.equal(await visibleBlock(), block);
    await page.goto(`${baseUrl}/shelf`, { waitUntil: "networkidle" });
    const current = page.locator(`a[href="${href}?bookmark=1"]`);
    assert.match(await current.textContent(), /อ่านจากที่คั่น/);
    await current.click();
    await page.waitForURL(`${baseUrl}${href}`);
    assert.equal(await page.locator(".reader-review").count(), 0);
  });
});

test("mobile search exposes the story, detail supports favorites, and bookmark review keeps resume", async () => {
  await withPage({ width: 360, height: 732 }, async (page) => {
    const book = "/books/ten-day-ultimatum";
    await page.goto(`${baseUrl}/`);
    await page.locator(".hero-search input").fill("คำขาด");
    await page.getByRole("button", { name: "ไปยังผลการค้นหา" }).click();
    await page.waitForURL("**/?q=*#catalog");
    const item = page.locator(`#catalog a[href="${book}"]`);
    await page.waitForFunction(() => {
      const title = document.querySelector("#catalog .book-card .t")?.getBoundingClientRect();
      const nav = document.querySelector(".botnav")?.getBoundingClientRect();
      return title && nav && title.top >= 65 && title.bottom < nav.top;
    });
    await item.click();
    await page.getByText("เรื่องย่อฉบับเต็ม", { exact: true }).click();
    const synopsis = page.locator(".section.about");
    await synopsis.waitFor({ state: "visible" });
    assert.match(await synopsis.textContent(), /คนแปลกหน้าสิบคน/);
    await page.getByRole("button", { name: "บันทึกเรื่องโปรด" }).click();
    assert.equal(await page.getByRole("button", { name: "บันทึกแล้ว" }).getAttribute("aria-pressed"), "true");

    await page.goto(`${baseUrl}${book}/read/ch002`, { waitUntil: "networkidle" });
    const bookmarkedBlock = await page.evaluate(() => {
      scrollTo({ top: 1400, behavior: "instant" });
      const inset = document.querySelector(".reader-topbar").offsetHeight + 8;
      return [...document.querySelector(".reader-article").children].findIndex((node) => node.getBoundingClientRect().bottom > inset);
    });
    const restoredBookmark = () => page.waitForFunction((index) => {
      const inset = document.querySelector(".reader-topbar").offsetHeight + 8;
      const rect = document.querySelector(".reader-article")?.children[index]?.getBoundingClientRect();
      return scrollY > 1000 && rect?.top <= inset + 2 && rect.bottom > inset - 2;
    }, bookmarkedBlock);
    await page.getByRole("button", { name: "คั่นหน้า" }).click();
    await page.goto(`${baseUrl}${book}/read/ch003`, { waitUntil: "networkidle" });
    await page.evaluate(() => scrollTo({ top: 1000, behavior: "instant" }));
    await page.getByRole("button", { name: "เปิดสารบัญ" }).click();
    await page.getByRole("dialog").locator(`a[href="${book}/read/ch002?review=1"]`).click();
    await page.locator(".reader-review").waitFor();
    await restoredBookmark();
    await page.evaluate(() => scrollTo({ top: 1000, behavior: "instant" }));
    const quickReturn = page.locator(".reader-topbar").getByRole("link", { name: "กลับไปอ่านต่อ ตอน 003" });
    assert.ok((await quickReturn.boundingBox()).y < 140, "return must stay in the sticky toolbar after scrolling");
    await page.locator(".reader-end").getByRole("link", { name: "กลับไปอ่านต่อ" }).click();
    await page.waitForFunction(() => document.querySelector(".reader-kicker")?.textContent.includes("003") && scrollY > 950);
    await page.getByRole("link", { name: "กลับไปสารบัญ" }).click();
    await page.waitForURL((url) => url.pathname === `${book}/chapters`);
    const marked = page.locator(`.toc-list a[href="${book}/read/ch002?review=1"]`);
    await marked.waitFor();
    await page.locator('.toc-list .ch-row:has(a[href$="/read/ch002?review=1"]) button[aria-pressed="true"]').waitFor();
    await page.goto(`${baseUrl}/shelf`);
    await page.locator(`a[href="${book}/read/ch002?review=1"]`).click();
    await page.locator(".reader-review").waitFor();
    await restoredBookmark();
    await page.evaluate(() => scrollTo({ top: 900, behavior: "instant" }));
    await page.goto(`${baseUrl}${book}`, { waitUntil: "networkidle" });
    await page.getByRole("link", { name: /อ่านต่อ ตอน 003/ }).click();
    await page.waitForFunction(() => document.querySelector(".reader-kicker")?.textContent.includes("003") && scrollY > 950);
  }, { seeded: false });
});

test("malformed favorites do not discard valid progress, and separate tabs merge edits", async () => {
  await withPage({ width: 1200, height: 840 }, async (page) => {
    await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
    await page.evaluate((key) => {
      const state = JSON.parse(localStorage.getItem(key));
      localStorage.setItem(key, JSON.stringify({ ...state, favorites: {} }));
    }, stateKey);
    await page.reload({ waitUntil: "networkidle" });
    assert.equal(await page.locator('.resume[href$="/read/ch003"]').count(), 1);
    const second = await page.context().newPage();
    await second.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
    await page.locator(".book-card .fav").nth(0).click();
    await second.locator(".book-card .fav").nth(1).click();
    assert.equal((await storedState(page)).favorites.length, 2);
    await page.waitForFunction(() => document.querySelectorAll('.fav[aria-pressed="true"]').length === 2);
  });
});

test("authored newlines separate status rows and item details without changing text", async () => {
  const examples = [
    { route: "/books/a-gacha-addicts-fusionpunk-life/read/ch039", marker: "★★ [ฟีเวอร์พรีเมียม!] ★★", minLines: 10 },
    { route: "/books/a-gacha-addicts-fusionpunk-life/read/ch039", marker: "「ตั๋วเสริมพลังโจ๊กเกอร์พรีเมียม」", minLines: 5 },
    { route: "/books/investing-in-my-crippled-wife/read/ch015", marker: "[ข้อมูลส่วนบุคคล]", minLines: 6 },
    { route: "/books/investing-in-my-crippled-wife/read/ch063", marker: "═".repeat(36), minLines: 15 },
  ];
  for (const width of [1440, 390]) {
    await withPage({ width, height: 1000 }, async (page) => {
      for (const example of examples) {
        await page.goto(`${baseUrl}${example.route}`, { waitUntil: "networkidle" });
        await page.evaluate(() => document.fonts.ready);
        const paragraph = page.locator(".reader-paragraph").filter({ hasText: example.marker }).first();
        const authoredText = await paragraph.textContent();
        await paragraph.scrollIntoViewIfNeeded();
        const lines = await paragraph.evaluate((element) => {
          const nodes = [];
          const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
          while (walker.nextNode()) nodes.push(walker.currentNode);
          const rectAt = (offset) => {
            for (const node of nodes) {
              if (offset < node.textContent.length) {
                const range = document.createRange();
                range.setStart(node, offset);
                range.setEnd(node, offset + 1);
                const rect = range.getBoundingClientRect();
                return { x: rect.x, y: rect.y };
              }
              offset -= node.textContent.length;
            }
            throw new Error("Authored character is missing from the rendered paragraph");
          };
          let offset = 0;
          return element.textContent.split("\n").flatMap((line) => {
            const row = line.trim() ? [{ text: line, first: rectAt(offset + line.search(/\S/)), last: rectAt(offset + line.trimEnd().length - 1) }] : [];
            offset += line.length + 1;
            return row;
          });
        });
        assert.ok(lines.length >= example.minLines, "fixture must retain its authored status/item lines");
        for (let index = 1; index < lines.length; index += 1) {
          assert.ok(lines[index].first.y > lines[index - 1].last.y + 1,
            `${width}px ${example.route}: authored line ${index + 1} must start below the preceding line, not run into it`);
        }
        assert.equal(await paragraph.textContent(), authoredText, "layout must not rewrite status text, numbers or item effects");
        assert.ok(await paragraph.evaluate((element) => element.scrollWidth <= element.clientWidth + 1),
          `${width}px ${example.route}: a long unbroken status rule must wrap inside its paragraph`);
        assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 2), false,
          "long status lines must still wrap without horizontal overflow");
      }
    });
  }
});
