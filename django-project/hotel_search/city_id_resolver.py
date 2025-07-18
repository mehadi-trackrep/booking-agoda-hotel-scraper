import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urlparse, parse_qs
from loguru import logger

async def get_agoda_city_id(city_name: str) -> str | None:
    """
    Uses Playwright to navigate Agoda, search for a city, and extract the city ID from the URL.
    """
    logger.info(f"Attempting to get Agoda city ID for: {city_name}")
    async with async_playwright() as p:
        browser = None
        try:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to Agoda homepage
            await page.goto("https://www.agoda.com/en-gb/", wait_until="domcontentloaded")
            logger.info(f"Navigated to Agoda homepage: {page.url}")

            try:
                # Fill destination
                await page.fill("#textInput", city_name)

                # Wait for the search button
                await page.wait_for_selector("button[data-selenium='searchButton']", timeout=10000)
                
                # Click the search button
                await page.click("button[data-selenium='searchButton']")
                logger.info("Clicked search input.")
        
                # Wait for navigation (search results page)
                await page.wait_for_load_state("networkidle")
            except PlaywrightTimeoutError:
                logger.warning("Could not find direct search input, trying alternative selectors.")
                # Fallback 
                await page.click("button[data-selenium='searchButton']", timeout=5000)
                logger.info("Clicked alternative search input.")

            
            # Extract city ID from the URL
            parsed_url = urlparse(page.url)
            query_params = parse_qs(parsed_url.query)
            
            city_id = query_params.get('city', [None])[0]
            
            if city_id:
                logger.info(f"Successfully extracted Agoda city ID: {city_id}")
                return city_id
            else:
                logger.warning(f"Could not find 'city' parameter in URL: {page.url}")
                return None

        except PlaywrightTimeoutError as e:
            logger.error(f"Playwright operation timed out: {e}")
            if browser:
                await browser.close()
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during Agoda city ID resolution: {e}")
            if browser:
                await browser.close()
            return None
        finally:
            if browser:
                await browser.close()

if __name__ == '__main__':
    # Example usage for testing
    async def main():
        city_id = await get_agoda_city_id("Bangkok")
        print(f"Resolved Bangkok City ID: {city_id}")
        
        city_id = await get_agoda_city_id("New York")
        print(f"Resolved New York City ID: {city_id}")

    asyncio.run(main())
