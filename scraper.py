import asyncio 
from playwright.async_api import async_playwright
import csv
import json

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
    # articles = await page.locator('//div[@data-testid="anchor-inner-wrapper"]').all()
    more_articles_section = page.get_by_test_id("alaska")
    current_page = 1
    all_present_links = []

    while current_page <= 7:
        # click current page button
        buttons_section = page.get_by_test_id("pagination")
        button = buttons_section.get_by_role(f"//button[title='Go to page {current_page}']")
        articles = await more_articles_section.locator('//div[@data-testid="anchor-inner-wrapper"]').all()

        
        for article in articles:
            a_element = article.get_by_test_id("internal-link").first
            if a_element:
                href_a = await a_element.get_attribute("href")
                # https://www.bbc.com/news/articles/cn9z0d9pd2xo
                complete_link = f"https://www.bbc.com{href_a}"
                all_present_links.append(complete_link)


        current_page += 1 

    for_test = all_present_links[0:10]    
    
    for link in for_test:
        await page.goto(link, timeout=30000)
        headline_block_locator =  page.locator('//div[@data-component="headline-block"]').first
        title_locator =  headline_block_locator.locator("h1").first
        if title_locator:
            title = await title_locator.inner_text()
        contributer_locator = page.get_by_test_id("byline-contributors-contributor-0").first
        author_locator = contributer_locator.locator("span").first
        if author_locator:
            author = await author_locator.inner_text()

        # logic to extract date time
        byline_block_locator = page.get_by_test_id("byline").first
        time_locator = byline_block_locator.locator("time").first
        if time_locator:
            full_date_time = await time_locator.get_attribute('datetime')
        
        date_formatted = full_date_time.split('T')[0]

        
        print(f"TITLE: {title}, AUTHOR: {author}, DATE: {date_formatted}")



if __name__ == "__main__":
    asyncio.run(main())