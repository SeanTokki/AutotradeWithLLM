from playwright.sync_api import sync_playwright
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio
import time

def fetchWithPlaywright(urls):
    contents = []
    for url in urls:
        with sync_playwright() as pw:
            try:
                print(f"Start fetching | url: {url}")
                browser = pw.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                
                page.goto(url)
                # Waiting until page loading is done. But don't know why this is the solution.
                print(f"Waiting for page loading... | url: {url}")
                time.sleep(6) 

                contents.append(page.content())
                print(f"Fetch clear | url: {url}")
            except Exception as e:
                print(f"Fetching error: {e} | url: {url}")
                contents.append("")
            finally:
                browser.close()
    
    return contents

async def _asyncFetch(urls):
    # Inner function to fetch only one url
    async def asyncFetchOne(url):
        async with async_playwright() as pw:
            try:
                print(f"Start fetching | url: {url}")
                browser = await pw.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                )
                page = await context.new_page()
                
                await page.goto(url)
                # Waiting until page loading is done. But don't know why this is the solution.
                print(f"Waiting for page loading... | url: {url}")
                await asyncio.sleep(6)

                content = await page.content()
                print(f"Fetch clear | url: {url}")
            except Exception as e:
                print(f"Fetching error: {e} | url: {url}")
                content = ""
            finally:
                await browser.close()
        
        return content
    
    # Start fetching all urls simultaneously
    contents = await asyncio.gather(*[asyncFetchOne(url) for url in urls])
    
    return contents

def asyncFetchWithPlaywright(urls):
    # Due to the server specifications, at most 2 crawler will be active at a time.
    # contents = asyncio.run(asyncFetch(urls))
    bundled_urls = [[x, y] for x, y in zip(urls[0::2], urls[1::2])]
    #print(bundled_urls)
    contents = []
    for bundle in bundled_urls:
        contents.extend(asyncio.run(_asyncFetch(bundle)))

    return contents