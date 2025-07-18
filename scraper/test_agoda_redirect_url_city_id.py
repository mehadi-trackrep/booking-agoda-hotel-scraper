import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto("https://www.agoda.com/en-gb/search")

        # Wait for input field
        await page.wait_for_selector("#textInput", timeout=15000)

        # Fill destination
        await page.fill("#textInput", "Sylhet")

        # Wait for the search button
        await page.wait_for_selector("button[data-selenium='searchButton']", timeout=10000)

        # Click the search button
        await page.click("button[data-selenium='searchButton']")

        # Wait for navigation (search results page)
        await page.wait_for_load_state("networkidle")

        # Get the final redirected URL
        final_url = page.url
        print("Final redirected URL:", final_url)

        await browser.close()

asyncio.run(run())
