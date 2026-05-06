/**
 * Crawl a single site (same registrable domain), extract text, POST to FastAPI.
 *
 * Usage: node crawler.js <domain-or-url>
 * Env:   MAX_PAGES (default 100), INGEST_URL (default http://localhost:8000/ingest-website),
 *        CRAWL_SETTLE_MS (default 3500) — post-load wait for SPA paint.
 *        SKIP_SITEMAP=1 — skip /sitemap.xml seeding.
 *        CRAWL_SINGLE_PAGE=1 — only the URL you pass (no sitemap, no following links).
 */

import { PlaywrightCrawler, EnqueueStrategy, log } from "crawlee";

const DEBUG =
  process.env.DEBUG === "1" || process.env.STUPA_DEBUG === "1";
function dbg(...args) {
  if (DEBUG) console.log("[crawler-debug]", ...args);
}

const INGEST_URL =
  process.env.INGEST_URL || "http://localhost:8000/ingest-website";
const MAX_PAGES = Math.min(
  Math.max(1, parseInt(process.env.MAX_PAGES || "100", 10)),
  50000,
);

const SINGLE_PAGE =
  process.env.CRAWL_SINGLE_PAGE === "1" ||
  process.env.CRAWL_SINGLE_PAGE === "true";
const EFFECTIVE_MAX_PAGES = SINGLE_PAGE ? 1 : MAX_PAGES;

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

function dedupeKey(u) {
  try {
    const x = new URL(u);
    x.hash = "";
    const path = (x.pathname || "/").replace(/\/+$/, "") || "/";
    return `${x.origin}${path}${x.search}`;
  } catch {
    return u;
  }
}

/** Same-origin URLs from /sitemap.xml (and index only if child is page sitemap). */
async function collectSitemapSeeds(start) {
  if (process.env.SKIP_SITEMAP === "1") return [];
  let origin;
  try {
    origin = new URL(start).origin;
  } catch {
    return [];
  }
  const candidates = [`${origin}/sitemap.xml`, `${origin}/sitemap_index.xml`];
  const urls = [];
  const seen = new Set([dedupeKey(start)]);

  const consumeXml = async (mapUrl) => {
    const r = await fetch(mapUrl, { redirect: "follow" });
    if (!r.ok) return false;
    const xml = await r.text();
    const locs = [...xml.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/gi)].map(
      (m) => m[1].trim(),
    );
    const childSitemaps = locs.filter((u) => /\.xml(\?|$)/i.test(u));
    const pageLocs = locs.filter((u) => !/\.xml(\?|$)/i.test(u));

    if (childSitemaps.length && pageLocs.length === 0) {
      for (const child of childSitemaps.slice(0, 12)) {
        try {
          if (new URL(child).origin !== origin) continue;
          const r2 = await fetch(child, { redirect: "follow" });
          if (!r2.ok) continue;
          const inner = await r2.text();
          for (const m of inner.matchAll(/<loc>\s*([^<\s]+)\s*<\/loc>/gi)) {
            const u = m[1].trim();
            if (/\.xml(\?|$)/i.test(u)) continue;
            try {
              if (new URL(u).origin !== origin) continue;
              const k = dedupeKey(u);
              if (seen.has(k)) continue;
              seen.add(k);
              urls.push(u);
            } catch {
              /* */
            }
          }
        } catch {
          /* */
        }
      }
      return urls.length > 0;
    }

    for (const u of pageLocs) {
      try {
        if (new URL(u).origin !== origin) continue;
        const k = dedupeKey(u);
        if (seen.has(k)) continue;
        seen.add(k);
        urls.push(u);
      } catch {
        /* */
      }
    }
    return urls.length > 0;
  };

  for (const mapUrl of candidates) {
    try {
      if (await consumeXml(mapUrl)) break;
    } catch {
      /* */
    }
  }
  const room = Math.max(0, MAX_PAGES - 1);
  return urls.slice(0, room);
}

async function scrollPageForLazyLinks(page) {
  for (let i = 0; i < 8; i++) {
    await page.evaluate(() =>
      window.scrollBy(0, Math.min(window.innerHeight * 1.2, 1400)),
    );
    await new Promise((r) => setTimeout(r, 350));
  }
  await page.evaluate(() => window.scrollTo(0, 0));
  await new Promise((r) => setTimeout(r, 200));
}

/** Reveal hidden navigation menus by hovering over menu items. */
async function revealNavigationMenus(page, lg) {
  try {
    await page.evaluate(() => window.scrollTo(0, 0));
    await new Promise((r) => setTimeout(r, 300));

    const navSelectors = [
      "nav a",
      "header a",
      "[role='navigation'] a",
      ".menu a",
      ".nav a",
      ".navbar a",
    ];

    for (const selector of navSelectors) {
      const links = await page.$$(selector);
      for (let i = 0; i < Math.min(links.length, 20); i++) {
        try {
          await links[i].hover({ timeout: 1000 });
          await new Promise((r) => setTimeout(r, 200));
        } catch {
          /* element might not be hoverable */
        }
      }
    }
  } catch (e) {
    lg.warning(`[crawler] revealNavigationMenus failed: ${e?.message || e}`);
  }
}

/** Extract ALL hrefs from the page, including hidden/collapsed links. */
async function extractAllHrefs(page, currentUrl) {
  return page.evaluate((url) => {
    const allLinks = Array.from(document.querySelectorAll("a[href]"));
    const hrefs = allLinks
      .map((a) => {
        try {
          const href = a.getAttribute("href");
          if (!href) return null;
          return new URL(href, url).href;
        } catch {
          return null;
        }
      })
      .filter(Boolean);
    return [...new Set(hrefs)];
  }, currentUrl);
}

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

/** Extra ms after load so Next.js / SPAs can hydrate (was 800; too short for many pages). */
const SETTLE_MS = Math.max(
  800,
  parseInt(process.env.CRAWL_SETTLE_MS || "3500", 10),
);

/** Read DOM text; retry once if the client router replaces the document mid-run. */
async function extractVisibleText(page, lg, url) {
  const runEvaluate = () =>
    page.evaluate(() => {
      const strip = document.querySelectorAll(
        "nav, footer, script, style, noscript, iframe, svg, header[role='banner'], .cookie, #cookie",
      );
      strip.forEach((el) => el.remove());

      const pick = [];
      const seen = new Set();
      const add = (el) => {
        const t = (el.innerText || "").trim();
        if (t && t.length > 2 && !seen.has(t)) {
          seen.add(t);
          pick.push(t);
        }
      };

      document
        .querySelectorAll("main, article, section, [role='main']")
        .forEach(add);
      document
        .querySelectorAll("h1, h2, h3, h4, h5, h6, p")
        .forEach(add);

      let joined = pick.join("\n\n");
      const loadingOnly =
        joined.length < 400 ||
        /^loading\b/i.test(joined.trim()) ||
        /\bloading stupa\b/i.test(joined);
      if (loadingOnly) {
        const body = document.body;
        if (body) {
          const b = (body.innerText || "").trim();
          if (b.length > joined.length) {
            joined = b;
          }
        }
      }

      return joined;
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
  maxRequestsPerCrawl: EFFECTIVE_MAX_PAGES,
  maxConcurrency: 2,
  requestHandlerTimeoutSecs: 60,

  async requestHandler({ page, request, enqueueLinks, log: lg }) {
    const url = request.loadedUrl || request.url;
    if (skipBinaryRequest({ url })) {
      lg.info(`[crawler] skip binary URL: ${url}`);
      return;
    }

    dbg("fetch", url);
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
    try {
      await page.waitForLoadState("networkidle", { timeout: 12000 });
    } catch {
      /* ads / analytics keep network busy — ignore */
    }
    await new Promise((r) => setTimeout(r, SETTLE_MS));

    if (SINGLE_PAGE) {
      await scrollPageForLazyLinks(page);
      await new Promise((r) => setTimeout(r, 1500));
    }

    let raw;
    try {
      raw = await extractVisibleText(page, lg, url);
      const short = !raw || raw.trim().length < 200;
      if (short) {
        await new Promise((r) => setTimeout(r, 2000));
        raw = await extractVisibleText(page, lg, url);
      }
    } catch (e) {
      lg.warning(`[crawler] extract failed ${url}: ${e?.message || e}`);
      raw = "";
    }

    const content = cleanText(raw);
    if (!content) {
      lg.warning(`[crawler] no text extracted: ${url}`);
    } else {
      try {
        const res = await fetch(INGEST_URL, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url, content }),
        });
        if (!res.ok) {
          const errText = await res.text().catch(() => "");
          lg.error(
            `[crawler] ingest HTTP ${res.status} ${url}: ${errText.slice(0, 200)}`,
          );
        } else {
          pagesDone += 1;
          dbg("ingested", pagesDone, url);
          lg.info(`[crawler] ingested pages=${pagesDone} url=${url}`);
        }
      } catch (e) {
        const code = e?.cause?.code || e?.code || "";
        const msg = e?.message || String(e);
        lg.error(
          `[crawler] ingest fetch failed (${INGEST_URL}): ${msg}` +
            (code ? ` [${code}]` : ""),
        );
        lg.error(
          "[crawler] hint: start FastAPI on the ingest URL, e.g. " +
            "uvicorn app.main:app --host 0.0.0.0 --port 8000",
        );
      }
    }

    await new Promise((r) => setTimeout(r, 300));
    if (SINGLE_PAGE) {
      lg.info("[crawler] single-page mode: skipping link enqueue");
      return;
    }
    await scrollPageForLazyLinks(page);
    
    // Reveal hidden navigation menus (dropdowns, submenus)
    await revealNavigationMenus(page, lg);
    
    // Extract all hrefs including hidden ones
    let allHrefs = [];
    try {
      allHrefs = await extractAllHrefs(page, url);
      dbg("discovered hrefs", allHrefs.length, "from", url);
      if (allHrefs.length > 0) {
        lg.info(`[crawler] discovered ${allHrefs.length} links on ${url}`);
      }
    } catch (e) {
      lg.warning(`[crawler] extractAllHrefs failed: ${e?.message || e}`);
    }
    
    // Standard enqueueLinks (for visible links)
    await enqueueLinks({
      strategy: EnqueueStrategy.SameDomain,
      exclude: LINK_EXCLUDE,
      transformRequestFunction: (reqOpts) =>
        skipBinaryRequest(reqOpts) ? false : reqOpts,
    });
    
    // Manually enqueue all discovered hrefs (including hidden ones)
    if (allHrefs.length > 0) {
      const filtered = allHrefs.filter((href) => {
        try {
          const hrefUrl = new URL(href);
          const currentOrigin = new URL(url).origin;
          const sameOrigin = hrefUrl.origin === currentOrigin;
          const notBinary = !BINARY_PATH.test(href) && !BINARY_PATH.test(hrefUrl.pathname);
          return sameOrigin && notBinary;
        } catch {
          return false;
        }
      });
      
      if (filtered.length > 0) {
        await crawler.addRequests(filtered.map((href) => ({ url: href })));
        dbg("manually enqueued", filtered.length, "hidden/submenu links");
        lg.info(`[crawler] manually enqueued ${filtered.length} additional links`);
      }
    }
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
  `[crawler] start ${startUrl} max_pages=${EFFECTIVE_MAX_PAGES} ` +
    `single_page=${SINGLE_PAGE} ingest=${INGEST_URL}`,
);

const sitemapSeeds = SINGLE_PAGE ? [] : await collectSitemapSeeds(startUrl);
const initialRequests = SINGLE_PAGE
  ? [startUrl]
  : [startUrl, ...sitemapSeeds];
log.info(
  `[crawler] queue_seed_urls=${initialRequests.length} ` +
    `(sitemap_extra=${sitemapSeeds.length})`,
);

await crawler.run(initialRequests);
log.info(`[crawler] done pages_ingested=${pagesDone}`);
