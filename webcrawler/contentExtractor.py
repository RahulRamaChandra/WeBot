import asyncio
import json
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

# CONFIGURATION
START_URL = "https://www.revenue.ie/en/home.aspx"
MAX_DEPTH = 3
MAX_PAGES = 20
CONCURRENCY = 5
OUTPUT_JSON_FILE = "site_content.json"

# SHARED STATE
visited = set()
pages_crawled = 0
site_data = {}

async def worker(queue, crawler, config, semaphore):
    global pages_crawled

    while not queue.empty() and pages_crawled < MAX_PAGES:
        url, depth = await queue.get()

        if url in visited or depth > MAX_DEPTH:
            queue.task_done()
            continue

        visited.add(url)

        async with semaphore:
            result = await crawler.arun(url, config=config)

        if result.success:
            pages_crawled += 1
            print(f"[✓] ({pages_crawled}) Crawled: {url}")

            # Markdown extraction
            try:
                fit_markdown = result.markdown.fit_markdown
                raw_markdown = result.markdown.raw_markdown
                print(f"    Full Markdown Length: {len(raw_markdown)}")
                print(f"    Fit Markdown Length: {len(fit_markdown)}")
            except Exception as e:
                print(f"[!] Warning: Markdown extraction failed for {url} — {e}")
                fit_markdown = ""
                raw_markdown = ""

            # Extract internal links
            internal_links = result.links.get("internal", [])
            page_links = []
            for link in internal_links:
                href = link.get("href")
                text = link.get("text", "").strip() or href

                if href:
                    page_links.append({"text": text, "href": href})
                    if href not in visited:
                        await queue.put((href, depth + 1))

            # Save page content and links
            site_data[url] = {
                "url_text": page_links,
                "fit_markdown": fit_markdown  # Use raw_markdown if preferred
            }

        else:
            print(f"[ERROR] Failed to crawl: {url} — {result.error_message}")

        queue.task_done()


async def main():
    config = CrawlerRunConfig(
        excluded_tags=["nav", "footer", "aside"],
        remove_overlay_elements=True,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter()
        ),
        exclude_external_links=True,
        exclude_social_media_links=True
    )

    queue = asyncio.Queue()
    await queue.put((START_URL, 0))

    semaphore = asyncio.Semaphore(CONCURRENCY)

    async with AsyncWebCrawler() as crawler:
        workers = [
            asyncio.create_task(worker(queue, crawler, config, semaphore))
            for _ in range(CONCURRENCY)
        ]

        await queue.join()

        for w in workers:
            w.cancel()

        # Wait for worker tasks to exit cleanly
        await asyncio.gather(*workers, return_exceptions=True)

        print(f"\n✅ Crawled {pages_crawled} page(s)")
        print(f"✅ Writing structured data to: {OUTPUT_JSON_FILE}")

        with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(site_data, f, indent=2, ensure_ascii=False)



if __name__ == "__main__":
    asyncio.run(main())
