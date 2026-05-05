# Website crawl → RAG (Crawlee + FastAPI)

This stack indexes **public HTML pages** into a **dedicated Chroma database**
(`website_vector_store` in `config.yaml`, default `data/chroma_website`).
File uploads use `data/chroma` only. RAG merges retrieval from both stores on
`/query` and `/query/stream`.

## 1. Install Crawlee (Node)

From the repo root:

```bash
cd crawler
npm install
```

**Required once after `npm install`:** download browsers (pick one):

```bash
npx playwright install chromium
```

or:

```bash
npx crawlee install
```

If you see **`Executable doesn't exist`** under `ms-playwright\...`, the step
above was skipped or Playwright was upgraded—run `npx playwright install
chromium` again from **`crawler/`**.

Requires **Node.js 18+** and a working `node` on your `PATH` (needed for
`POST /crawl`).

## 2. Run the FastAPI app

```bash
# from project root, with your venv activated
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 3. Run the crawler manually

The script lives in **`crawler/crawler.js`**, not the repo root. Either **change
into `crawler/`** first, or pass the path from the project root.

With the API already listening on port 8000:

```bash
cd crawler
node crawler.js example.com
```

From the **project root** (same folder as `app/`):

```bash
node crawler/crawler.js https://stupasports.ai/
```

Using **`cd crawler`** is recommended so Crawlee’s `storage` folder stays under
`crawler/`.

Or with a full URL:

```bash
cd crawler
node crawler.js https://example.com/docs/
```

### Environment variables

| Variable     | Default                                      | Meaning                          |
|-------------|----------------------------------------------|----------------------------------|
| `MAX_PAGES` | `100`                                        | Max URLs per crawl (cap 50 000)  |
| `INGEST_URL`| `http://localhost:8000/ingest-website`       | FastAPI ingest endpoint          |

Example:

```bash
set MAX_PAGES=50
set INGEST_URL=http://127.0.0.1:8000/ingest-website
node crawler.js https://docs.example.com/
```

(On PowerShell, use `$env:MAX_PAGES="50"`.)

## 4. Trigger via FastAPI

`POST /crawl` (also under `/api/crawl`) starts the Node process in the
background.

```bash
curl -X POST http://localhost:8000/crawl ^
  -H "Content-Type: application/json" ^
  -d "{\"domain\": \"example.com\", \"max_pages\": 100}"
```

Response includes `pid` of the child process.

Per-page ingestion (what the crawler calls):

```bash
curl -X POST http://localhost:8000/ingest-website ^
  -H "Content-Type: application/json" ^
  -d "{\"url\": \"https://example.com/page\", \"content\": \"plain text...\"}"
```

Chunks are stored with metadata `source` = page URL and a synthetic
`filename` like `web:example.com/path_hint` for citations.

## 5. Behaviour notes

- Crawl stays on the **same registrable domain** (`EnqueueStrategy.SameDomain`).
- Duplicates are avoided by Crawlee’s request queue.
- Nav / footer / scripts / styles are removed before text extraction.
- **PDF, Office, archives, etc.** are excluded from link discovery so the crawl
  does not hit Playwright’s “Download is starting” navigation errors. To index
  that content, use **`/upload`** (or extend the crawler with a PDF parser).
- **Uploaded files** live in `vector_store.persist_directory`; **crawled pages**
  live in `website_vector_store.persist_directory` only. Re-crawl after
  switching this layout if old pages were indexed into the uploads DB.

## 6. Troubleshooting

| Symptom                         | What to try                                      |
|---------------------------------|--------------------------------------------------|
| `503` on `/crawl`               | Install Node.js; ensure `node` is on `PATH`.     |
| Crawler: browser errors         | Run `npx crawlee install` in `crawler/`.         |
| Ingest connection refused       | Start FastAPI first; fix `INGEST_URL` if needed. |
| Empty chunks for many pages    | Site may be mostly JS; crawler waits for load + short settle; see `crawler.js`. |
| `Download is starting` / PDF  | Normal for direct file links; those URLs are skipped. Use `/upload` for PDFs.   |
