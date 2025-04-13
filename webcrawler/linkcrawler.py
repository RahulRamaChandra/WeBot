import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

async def main():
    crawler_cfg = CrawlerRunConfig(
        exclude_external_links=True,          # No links outside primary domain
        exclude_social_media_links=True,
         markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter()
        ),       
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun(
            "https://www.allianz-assistance.ie/",
            config=crawler_cfg
        )
        if result.success:
            print("[OK] Crawled:", result.url)
            print("Internal links count:", len(result.links.get("internal", [])))
            print("External links count:", len(result.links.get("external", [])))
            print(len(result.markdown.raw_markdown))
            print(len(result.markdown.fit_markdown))
            print(result.markdown.fit_markdown)
            # Likely zero external links in this scenario
            internal_links = {}
            for i in range (len(result.links['internal'])):
                internal_links[result.links['internal'][i]['href']] = [result.links['internal'][i]['text']]
                print(result.links['internal'][i]['href'])
            # with open ('example.txt', 'w') as file:
            #         file.write(str(internal_links))   
        else:
            print("[ERROR]", result.error_message)

if __name__ == "__main__":
    asyncio.run(main())