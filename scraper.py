import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import csv
import json
import sys

BASE_URL = "https://www.bbc.com/technology"

filename = sys.argv[1]

async def main():
   async  with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        await page.goto(BASE_URL, timeout=120000)
        await asyncio.sleep(2)
        await extract_technology_news(page)
        await browser.close()

async def extract_technology_news(page):
    more_articles_section = page.get_by_test_id("alaska")
    current_page = 1
    all_present_links = []

    COLUMNS = ['title', 'author', 'date', 'image_url', 'article_id', 'link']

    # writing headers
    if check_file_format(filename):

        with open(filename, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()


    while True:
        print(f"Scraping page: {current_page}")

        articles = await more_articles_section.locator('//div[@data-testid="anchor-inner-wrapper"]').all()

        for article in articles:
            a_element = article.get_by_test_id("internal-link").first
            if a_element:
                href_a = await a_element.get_attribute("href")
                complete_link = f"https://www.bbc.com{href_a}"
                all_present_links.append(complete_link)

        # check if a next page button exists
        buttons_section = page.get_by_test_id("pagination")
        next_button = buttons_section.get_by_text(f"{current_page + 1}")
        if await next_button.count() == 0:
            break

        await next_button.click()
        await asyncio.sleep(2)
        current_page += 1

    print(f"Total links collected: {len(all_present_links)}")
  
    
    for link in all_present_links:
        try:
            await page.goto(link, timeout=30000)
            headline_block_locator =  page.locator('//div[@data-component="headline-block"]').first
            title = "no title found"
            if await headline_block_locator.locator('h1').count() > 0:
                title = await headline_block_locator.locator("h1").first.inner_text()

            author = None
            byline_contributor_block_locator = page.get_by_test_id("byline-contributors-contributor-0")
            author = await byline_contributor_block_locator.locator("span").first.inner_text()

            # logic to extract date time
            byline_block_locator = page.get_by_test_id("byline").first
            time_locator = byline_block_locator.locator("time").first
            if time_locator:
                full_date_time = await time_locator.get_attribute('datetime')

            date_formatted = full_date_time.split('T')[0]

            # extracting article id
            split_link = link.split('/')
            article_id = split_link[-1]

            # extracting image
            image_url = "no image found"
            hero_image_locator = page.get_by_test_id("hero-image").first
            if await hero_image_locator.count() > 0:
                image_element = hero_image_locator.locator("img").first
                if await image_element.count() > 0:
                    srcset = await image_element.get_attribute("srcset")
                    if srcset:
                        image_url = srcset.split(' ')[0]

            # dictionary to append
            article = {
                "title": title,
                "author": author,
                "date": date_formatted,
                "image_url": image_url,
                "article_id": article_id,
                "link": link
            }

            # append dictionary to file
            append_data(article, filename, COLUMNS)

            print(f"TITLE: {title}, AUTHOR: {author}, DATE: {date_formatted}, Article ID: {article_id}")

        except PlaywrightTimeoutError:
            print(f"SKIPPED (timeout): {link}")
            continue


def check_file_format(filename):
    if filename.endswith('.csv'):
        return True
    return False


def append_data(article_dict, filename, columns):
    if check_file_format(filename):
        with open(filename, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writerow(article_dict)



if __name__ == "__main__":
    asyncio.run(main())