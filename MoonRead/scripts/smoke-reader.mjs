import fs from "node:fs/promises";
import http from "node:http";
import net from "node:net";
import path from "node:path";
import { spawn } from "node:child_process";
import { chromium } from "playwright";

const root = process.cwd();
const outputDir = path.join(root, "output", "playwright");

function getFreePort() {
  return new Promise((resolve, reject) => {
    const server = net.createServer();
    server.on("error", reject);
    server.listen(0, "127.0.0.1", () => {
      const address = server.address();
      const port = typeof address === "object" && address ? address.port : 3025;
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
        if (response.statusCode && response.statusCode < 500) {
          resolve();
          return;
        }

        if (Date.now() - startedAt > timeoutMs) {
          reject(new Error(`Timed out waiting for ${url}`));
          return;
        }

        setTimeout(probe, 400);
      });

      request.on("error", () => {
        if (Date.now() - startedAt > timeoutMs) {
          reject(new Error(`Timed out waiting for ${url}`));
          return;
        }

        setTimeout(probe, 400);
      });
    };

    probe();
  });
}

function startServer(port) {
  const child = spawn(
    "cmd.exe",
    ["/c", "node", "node_modules\\next\\dist\\bin\\next", "start", "--hostname", "127.0.0.1", "--port", String(port)],
    {
      cwd: root,
      windowsHide: true,
      stdio: ["ignore", "pipe", "pipe"],
    }
  );

  let output = "";
  child.stdout.on("data", (chunk) => {
    output += chunk.toString();
  });
  child.stderr.on("data", (chunk) => {
    output += chunk.toString();
  });

  return { child, getOutput: () => output };
}

async function main() {
  await fs.mkdir(outputDir, { recursive: true });

  const manifest = JSON.parse(await fs.readFile(path.join(root, "content", "generated", "manifest.json"), "utf8"));
  const library = JSON.parse(await fs.readFile(path.join(root, "content", "generated", "library.json"), "utf8"));
  const available = manifest.chapters.filter((chapter) => chapter.status === "available");
  const first = available[0];
  const latest = available.at(-1);
  const horrorBook = library.books.find((book) => book.slug === "horror-game-developer");
  const infiniteBook = library.books.find((book) => book.slug === "infinite-regressor-stories");
  const horrorBookTitle = "นักพัฒนาเกมสยองขวัญ";
  let strongChapter = first;
  let emChapter = first;
  for (const chapter of available) {
    const chapterMarkdown = await fs.readFile(
      path.join(root, "content", "generated", "chapters", `${chapter.id}.md`),
      "utf8"
    );
    if (strongChapter === first && /\*\*[^*]+\*\*/.test(chapterMarkdown)) {
      strongChapter = chapter;
    }
    if (emChapter === first && /(^|[^*])\*[^*]+\*/.test(chapterMarkdown)) {
      emChapter = chapter;
    }
    if (strongChapter !== first && emChapter !== first) {
      break;
    }
  }
  const firstBlocked = manifest.chapters.find((chapter) => chapter.status !== "available");
  const logoSvg = await fs.readFile(path.join(root, "public", "images", "moonread-logo.svg"), "utf8");
  const port = Number(process.env.MOONREAD_SMOKE_PORT || (await getFreePort()));
  const baseUrl = `http://127.0.0.1:${port}`;
  const server = startServer(port);

  try {
    await waitForHttp(`${baseUrl}/`);

    const browser = await chromium.launch({ executablePath: chromium.executablePath() });
    const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
    const consoleErrors = [];

    page.on("console", (message) => {
      if (message.type() === "error") {
        consoleErrors.push(message.text());
      }
    });

    await page.goto(`${baseUrl}/`, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(outputDir, "moonread-home-desktop.png"), fullPage: true });
    const hasHomeNavLink = await page.locator('nav[aria-label="Primary navigation"]').getByRole("link", { name: "ค้นพบ" }).isVisible();
    const homeEvidence = await page.evaluate(({ hBookTitle }) => ({
      title: document.title,
      hasMoonRead: document.body.textContent.includes("MoonRead"),
      hasBookName: document.body.innerText.includes("Deep Sea Embers"),
      hasHorrorBook: document.body.innerText.includes(hBookTitle),
      hasLibraryHero: Boolean(document.querySelector(".hero")),
      siteTheme: document.documentElement.dataset.siteTheme,
      logoSrc: document.querySelector(".brand img")?.getAttribute("src") || "",
    }), { hBookTitle: horrorBookTitle });
    homeEvidence.hasHomeNavLink = hasHomeNavLink;

    await page.getByRole("button", { name: /^(สลับเป็นโหมดมืด|โหมดมืด)$/ }).click();
    const darkTheme = await page.evaluate(() => document.documentElement.dataset.siteTheme);

    await page.goto(`${baseUrl}/chapters`, { waitUntil: "networkidle" });
    const chapterEvidence = await page.evaluate(({ blockedLabel, availableLabel }) => ({
      hasAvailableChapter: availableLabel ? document.body.innerText.includes(availableLabel) : false,
      hasBlockedChapter: blockedLabel ? document.body.innerText.includes(blockedLabel) : true,
      hasSectionTitle: document.body.innerText.includes("สารบัญ Deep Sea Embers"),
    }), {
      blockedLabel: firstBlocked ? `ตอน ${String(firstBlocked.number).padStart(3, "0")} ยังไม่พร้อมอ่าน` : "",
      availableLabel: first?.title || "",
    });

    await page.goto(`${baseUrl}/read/${first.id}`, { waitUntil: "networkidle" });
    await page.locator(".reader-topbar").waitFor({ state: "visible", timeout: 15000 });
    await page.locator(".reader-topbar").getByRole("button", { name: "ตั้งค่าการอ่าน" }).click();
    await page.getByRole("button", { name: "กลางคืน" }).click();
    const readerEvidence = await page.evaluate(({ chapterTitle }) => ({
      hasSettings: document.body.innerText.includes("ตั้งค่าการอ่าน"),
      hasChapterTitle: document.body.innerText.includes(chapterTitle),
      readerThemePersisted: localStorage.getItem("moonread-state-v1")?.includes('"theme":"night"') || false,
    }), { chapterTitle: first.title });

    await page.goto(`${baseUrl}/read/${strongChapter.id}`, { waitUntil: "networkidle" });
    const strongCount = await page.evaluate(() => document.querySelectorAll(".reader-paragraph strong").length);
    await page.goto(`${baseUrl}/read/${emChapter.id}`, { waitUntil: "networkidle" });
    const emCount = await page.evaluate(() => document.querySelectorAll(".reader-paragraph em").length);
    const emphasisEvidence = { strongCount, emCount };

    let horrorEvidence = { hasBook: false, hasFirstChapter: false, hasReader: false, available: 0 };
    if (horrorBook?.firstChapter) {
      await page.goto(`${baseUrl}${horrorBook.href}`, { waitUntil: "networkidle" });
      await page.goto(`${baseUrl}${horrorBook.firstChapter.href}`, { waitUntil: "networkidle" });
      await page.locator(".reader-topbar").waitFor({ state: "visible", timeout: 15000 });
      horrorEvidence = await page.evaluate(({ chapterTitle, bookTitle }) => ({
        hasBook: document.body.innerText.includes(bookTitle),
        hasFirstChapter: document.body.innerText.includes(chapterTitle),
        hasReader: Boolean(document.querySelector(".reader-article")),
        available: Number(document.body.innerText.includes("MoonRead")),
      }), { chapterTitle: horrorBook.firstChapter.title, bookTitle: horrorBookTitle });
      horrorEvidence.available = horrorBook.summary.available;
    }

    let infiniteChaptersEvidence = {
      hasToc: false,
      hasFirstChapter: false,
      hasAvailableCount: false,
      hasAppbar: false,
      hasTocRows: false,
      hasLegacyHeader: false,
    };
    if (infiniteBook?.firstChapter) {
      await page.goto(`${baseUrl}${infiniteBook.chaptersHref}`, { waitUntil: "networkidle" });
      infiniteChaptersEvidence = await page.evaluate(({ chapterTitle, available }) => ({
        hasToc: document.body.innerText.includes("สารบัญ I'm an Infinite Regressor"),
        hasFirstChapter: document.body.innerText.includes(chapterTitle),
        hasAvailableCount: document.body.innerText.includes(`${available} ตอนที่พร้อมอ่าน`),
        hasAppbar: Boolean(document.querySelector(".appbar")),
        hasTocRows: document.querySelectorAll(".toc-list .ch-row").length === available,
        hasLegacyHeader: Boolean(document.querySelector(".site-header")),
      }), { chapterTitle: infiniteBook.firstChapter.title, available: infiniteBook.summary.available });
    }

    const ogEvidence = await page.evaluate(() => ({
      hasOgTitle: Boolean(document.querySelector('meta[property="og:title"]')),
      hasOgImage: Boolean(document.querySelector('meta[property="og:image"]')),
      hasTwitterCard: Boolean(document.querySelector('meta[name="twitter:card"]')),
    }));

    // Clear console errors before 404 test — the intentional 404 navigation
    // will generate expected "Failed to load resource" errors
    const preNotFoundErrorCount = consoleErrors.length;
    await page.goto(`${baseUrl}/this-page-does-not-exist-404`, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(outputDir, "moonread-404.png"), fullPage: true });
    const notFoundEvidence = await page.evaluate(() => ({
      hasNotFoundClass: Boolean(document.querySelector(".not-found")),
      hasIllustration: Boolean(document.querySelector(".not-found-art img")),
      hasHeading: document.body.innerText.includes("ไม่พบหน้านี้"),
      hasHomeLink: Boolean(document.querySelector('.not-found a[href="/"]')),
    }));

    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(`${baseUrl}/read/${first.id}`, { waitUntil: "networkidle" });
    await page.screenshot({ path: path.join(outputDir, "moonread-reader-mobile.png"), fullPage: false });
    const mobileEvidence = await page.evaluate(() => ({
      width: window.innerWidth,
      hasTopbar: Boolean(document.querySelector(".reader-topbar")),
      overflowX: document.documentElement.scrollWidth > window.innerWidth + 2,
    }));

    await browser.close();

    // Only count console errors that happened before the intentional 404 test
    const unexpectedErrors = consoleErrors.slice(0, preNotFoundErrorCount);

    const result = {
      ok:
        unexpectedErrors.length === 0 &&
        homeEvidence.hasMoonRead &&
        homeEvidence.hasHomeNavLink &&
        homeEvidence.hasBookName &&
        homeEvidence.hasHorrorBook &&
        homeEvidence.hasLibraryHero &&
        homeEvidence.siteTheme === "light" &&
        homeEvidence.logoSrc.includes("moonread-logo") &&
        logoSvg.includes("#F0F0F0") &&
        logoSvg.includes("#EBC05F") &&
        logoSvg.includes("#121926") &&
        darkTheme === "dark" &&
        chapterEvidence.hasAvailableChapter &&
        chapterEvidence.hasBlockedChapter &&
        chapterEvidence.hasSectionTitle &&
        readerEvidence.hasSettings &&
        readerEvidence.hasChapterTitle &&
        readerEvidence.readerThemePersisted &&
        emphasisEvidence.strongCount > 0 &&
        emphasisEvidence.emCount > 0 &&
        horrorEvidence.hasBook &&
        horrorEvidence.hasFirstChapter &&
        horrorEvidence.hasReader &&
        horrorEvidence.available === horrorBook.summary.available &&
        infiniteChaptersEvidence.hasToc &&
        infiniteChaptersEvidence.hasFirstChapter &&
        infiniteChaptersEvidence.hasAvailableCount &&
        infiniteChaptersEvidence.hasAppbar &&
        infiniteChaptersEvidence.hasTocRows &&
        !infiniteChaptersEvidence.hasLegacyHeader &&
        mobileEvidence.hasTopbar &&
        !mobileEvidence.overflowX &&
        ogEvidence.hasOgTitle &&
        ogEvidence.hasOgImage &&
        notFoundEvidence.hasNotFoundClass &&
        notFoundEvidence.hasIllustration &&
        notFoundEvidence.hasHeading &&
        notFoundEvidence.hasHomeLink,
      consoleErrors: unexpectedErrors,
      notFoundConsoleErrors: consoleErrors.slice(preNotFoundErrorCount),
      homeEvidence,
      logoFileHasBrandColors:
        logoSvg.includes("#F0F0F0") && logoSvg.includes("#EBC05F") && logoSvg.includes("#121926"),
      darkTheme,
      chapterEvidence,
      readerEvidence,
      emphasisEvidence,
      horrorEvidence,
      infiniteChaptersEvidence,
      mobileEvidence,
      ogEvidence,
      notFoundEvidence,
      screenshots: [
        "output/playwright/moonread-home-desktop.png",
        "output/playwright/moonread-reader-mobile.png",
        "output/playwright/moonread-404.png",
      ],
    };

    await fs.writeFile(path.join(outputDir, "moonread-smoke-result.json"), `${JSON.stringify(result, null, 2)}\n`, "utf8");
    console.log(JSON.stringify(result, null, 2));

    if (!result.ok) {
      process.exitCode = 1;
    }
  } finally {
    if (process.platform === "win32") {
      spawn("taskkill", ["/PID", String(server.child.pid), "/T", "/F"], { windowsHide: true });
    } else {
      server.child.kill();
    }

    await fs.writeFile(path.join(outputDir, "server.log"), server.getOutput(), "utf8");
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
