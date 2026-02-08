import asyncio 
from playwright.async_api import async_playwright

BASE_URL = "https://www.bbc.com/technology"

async def main():
   async  with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(BASE_URL, timeout=120000)
        await asyncio.sleep(2)
        await extract_technology_news(page)
        await browser.close()

async def extract_technology_news(page):
    articles = await page.locator('//div[@data-testid="anchor-inner-wrapper"]').all()
    print(f"No of articles {len(articles)}")  

    
    

if __name__ == "__main__":
    asyncio.run(main())