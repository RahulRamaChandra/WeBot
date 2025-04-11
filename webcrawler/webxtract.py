import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy

async def main():
    # Configure a 2-level deep crawl
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=10, 
            include_external=False
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True
    )

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun("https://www.revenue.ie/en/home.aspx", config=config)

        print(f"Crawled {len(results)} pages in total")

        # Access individual results
        with open('example.txt', 'w') as file:

            for result in results[:3]:  # Show first 3 results
                print(f"URL: {result.url}")
                print(f"Depth: {result.metadata.get('depth', 0)}")
                file.write(result)



if __name__ == "__main__":
    asyncio.run(main())