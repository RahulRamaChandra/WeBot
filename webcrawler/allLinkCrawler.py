import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

visited = set()
link_data = {}

async def crawl_url(crawler, url, config):
    if url in visited:
        return
    visited.add(url)

    result = await crawler.arun(url, config=config)

    if result.success:
        # ✅ Extract and print markdown info here
        try:
            full_markdown_length = len(result.markdown.raw_markdown)
            fit_markdown_length = len(result.markdown.fit_markdown)
            print(f"[✓] Crawled: {url}")
            print(f"    Full Markdown Length: {full_markdown_length}")
            print(f"    Fit Markdown Length: {fit_markdown_length}")
        except Exception as e:
            print(f"[!] Warning: Markdown extraction failed for {url} — {e}")

        # Process internal links
        internal_links = result.links.get("internal", [])
        for link in internal_links:
            href = link.get('href')
            text = link.get('text', '').strip() or href

            if href and href not in visited:
                link_data[text] = href  # Save text -> href pair
                await crawl_url(crawler, href, config)  # Recursively crawl
    else:
        print(f"[ERROR] Failed to crawl: {url}, Reason: {result.error_message}")

async def main():
    start_url = "https://decisionanalytics.ai/"
    config = CrawlerRunConfig(

        excluded_tags=["nav", "footer", "aside"],
        remove_overlay_elements=True,
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter()),
        exclude_external_links=True,
        exclude_social_media_links=True
    )

    async with AsyncWebCrawler() as crawler:
        await crawl_url(crawler, start_url, config)
    

    print(f"\n✅ Total unique links found: {len(link_data)}\n")
    for text, href in link_data.items():
        print(f"{text}: {href}")

    # Optional: Save to file
    # with open('all_links.txt', 'w', encoding='utf-8') as f:
    #     for text, href in link_data.items():
    #         f.write(f"{text}: {href}\n")

if __name__ == "__main__":
    asyncio.run(main())
