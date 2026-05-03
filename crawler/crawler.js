/**
 * Crawl a single site (same registrable domain), extract text, POST to FastAPI.
 *
 * Usage: node crawler.js <domain-or-url>
 * Env:   MAX_PAGES (default 100), INGEST_URL (default http://localhost:8000/ingest-website)
 */

import { PlaywrightCrawler, EnqueueStrategy, log } from "crawlee";

const INGEST_URL =
  process.env.INGEST_URL || "http://localhost:8000/ingest-website";
const MAX_PAGES = Math.min(
  Math.max(1, parseInt(process.env.MAX_PAGES || "100", 10)),
  50000,
);

const domainArg = process.argv[2];
if (!domainArg?.trim()) {
  console.error("[crawler] usage: node crawler.js <domain-or-url>");
  process.exit(1);
}

function startUrlFromDomain(d) {
  const t = d.trim();
  if (t.startsWith("http://") || t.startsWith("https://")) {
    return t.endsWith("/") ? t : `${t}/`;
  }
  return `https://${t.replace(/^\/+/, "")}/`;
}

const startUrl = startUrlFromDomain(domainArg);

/** Skip downloads (PDF etc.) so Playwright does not treat navigation as a file. */
const BINARY_PATH = /\.(pdf|zip|rar|7z|tar|gz|tgz|docx?|xlsx?|pptx?|csv|exe|dmg)(\?|#|$)/i;

function skipBinaryRequest(req) {
  const u = req?.url || "";
  if (!u) return false;
  try {
    const path = new URL(u).pathname || "";
    return BINARY_PATH.test(u) || BINARY_PATH.test(path);
  } catch {
    return BINARY_PATH.test(u);
  }
}

const LINK_EXCLUDE = [
  "**/*.pdf",
  "**/*.zip",
  "**/*.rar",
  "**/*.7z",
  "**/*.doc",
  "**/*.docx",
  "**/*.xls",
  "**/*.xlsx",
  "**/*.ppt",
  "**/*.pptx",
];

function cleanText(raw) {
  if (!raw) return "";
  return raw
    .replace(/\u00a0/g, " ")
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean)
    .join("\n")
    .replace(/\n{3,}/g, "\n\n")
    .trim();
}

/** Read DOM text; retry once if the client router replaces the document mid-run. */
async function extractVisibleText(page, lg, url) {
  const runEvaluate = () =>
    page.evaluate(() => {
      const kill = document.querySelectorAll(
        "nav, footer, script, style, noscript, iframe, svg",
      );
      kill.forEach((el) => el.remove());

      const pick = [];
      const seen = new Set();
      const add = (el) => {
        const t = (el.innerText || "").trim();
        if (t && t.length > 2 && !seen.has(t)) {
          seen.add(t);
          pick.push(t);
        }
      };

      document.querySelectorAll("main, article").forEach(add);
      document
        .querySelectorAll("h1, h2, h3, h4, h5, h6, p")
        .forEach(add);

      return pick.join("\n\n");
    });

  for (let attempt = 0; attempt < 3; attempt += 1) {
    try {
      return await runEvaluate();
    } catch (e) {
      const msg = e?.message || String(e);
      const retry =
        /Execution context was destroyed|detached Frame/i.test(msg) &&
        attempt < 2;
      if (retry) {
        lg.warning(`[crawler] extract retry ${attempt + 1} ${url}`);
        await new Promise((r) => setTimeout(r, 1000));
      } else {
        throw e;
      }
    }
  }
}

let pagesDone = 0;

const crawler = new PlaywrightCrawler({
  maxRequestsPerCrawl: MAX_PAGES,
  maxConcurrency: 2,
  requestHandlerTimeoutSecs: 60,

  async requestHandler({ page, request, enqueueLinks, log: lg }) {
    const url = request.loadedUrl || request.url;
    if (skipBinaryRequest({ url })) {
      lg.info(`[crawler] skip binary URL: ${url}`);
      return;
    }

    lg.info(`[crawler] fetching ${url}`);

    try {
      await page.waitForLoadState("domcontentloaded", { timeout: 30000 });
    } catch (e) {
      lg.warning(`[crawler] load timeout ${url}: ${e?.message || e}`);
    }
    try {
      await page.waitForLoadState("load", { timeout: 20000 });
    } catch {
      /* SPA may not fire full load */
    }
    await new Promise((r) => setTimeout(r, 800));

    let raw;
    try {
      raw = await extractVisibleText(page, lg, url);
    } catch (e) {
      lg.warning(`[crawler] extract failed ${url}: ${e?.message || e}`);
      raw = "";
    }

    const content = cleanText(raw);
    if (!content) {
      lg.warning(`[crawler] no text extracted: ${url}`);
    } else {
      const res = await fetch(INGEST_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url, content }),
      });
      if (!res.ok) {
        const errText = await res.text().catch(() => "");
        lg.error(
          `[crawler] ingest failed ${res.status} ${url}: ${errText.slice(0, 200)}`,
        );
      } else {
        pagesDone += 1;
        lg.info(`[crawler] ingested pages=${pagesDone} url=${url}`);
      }
    }

    await new Promise((r) => setTimeout(r, 300));
    await enqueueLinks({
      strategy: EnqueueStrategy.SameDomain,
      exclude: LINK_EXCLUDE,
      transformRequestFunction: (reqOpts) =>
        skipBinaryRequest(reqOpts) ? false : reqOpts,
    });
  },

  failedRequestHandler({ request, log: lg }, err) {
    const msg = err?.message || String(err);
    if (msg.includes("Download is starting")) {
      lg.warning(`[crawler] skipped file download: ${request.url}`);
      return;
    }
    lg.error(`[crawler] failed ${request.url}: ${msg}`);
  },
});

log.info(
  `[crawler] start ${startUrl} max_pages=${MAX_PAGES} ingest=${INGEST_URL}`,
);

await crawler.run([startUrl]);
log.info(`[crawler] done pages_ingested=${pagesDone}`);
