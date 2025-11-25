import asyncio
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
import time

# ------------------------------
# FAST MODE (Static sites)
# ------------------------------
def fast_crawl_single(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=15, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        # remove scripts/styles
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # extract meaningful text
        text = " ".join([p.get_text() for p in soup.find_all(["p", "div"])])
        text = " ".join(text.split())
        return text, html
    except:
        return "", ""


def fast_crawl(url, max_pages=10):
    visited = set()
    to_visit = [url]
    domain = urlparse(url).netloc
    crawled = []

    while to_visit and len(visited) < max_pages:
        u = to_visit.pop(0)
        if u in visited:
            continue

        text, html = fast_crawl_single(u)
        if not text:
            visited.add(u)
            continue

        crawled.append({"url": u, "text": text})
        visited.add(u)

        # extract internal links
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            link = a["href"]
            if link.startswith("/"):
                link = urljoin(u, link)
            elif not link.startswith("http"):
                continue
            if urlparse(link).netloc == domain and link not in visited and link not in to_visit:
                to_visit.append(link)

    return crawled

# ------------------------------
# Detect heavy JS / bot-protected
# ------------------------------
def detect_heavy_js(text, html):
    if len(text) < 100:  # likely JS-rendered site
        return True
    bot_keywords = ["cf-browser-verification", "captcha", "robot", "challenge"]
    return any(k in html.lower() for k in bot_keywords)


# ------------------------------
# STEALTH MODE (Playwright)
# ------------------------------
async def stealth_crawl_async(start_url, max_pages=10):
    visited = set()
    to_visit = [start_url]
    domain = urlparse(start_url).netloc
    crawled = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,  # Non-headless for stealth
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage"
            ]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                       "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131 Safari/537.36",
            viewport={"width": 1366, "height": 768}
        )

        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            if url in visited:
                continue

            page = await context.new_page()
            try:
                # robust navigation with retries
                try:
                    await page.goto(url, timeout=120000, wait_until="networkidle")
                except PlaywrightTimeoutError:
                    try:
                        await page.goto(url, timeout=120000, wait_until="domcontentloaded")
                    except PlaywrightTimeoutError:
                        await page.goto(url, timeout=120000)

                # Close popups / cookie banners
                try:
                    buttons = await page.query_selector_all("button, a")
                    for b in buttons:
                        text_btn = await b.inner_text()
                        if any(k in text_btn.lower() for k in ["accept", "agree", "close", "ok"]):
                            await b.click()
                            await asyncio.sleep(0.5)
                except:
                    pass

                # scroll slowly to bottom (dynamic JS content)
                previous_height = await page.evaluate("document.body.scrollHeight")
                for _ in range(15):
                    await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                    await asyncio.sleep(0.5)
                    new_height = await page.evaluate("document.body.scrollHeight")
                    if new_height == previous_height:
                        break
                    previous_height = new_height

                # Extract text
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")
                for tag in soup(["script", "style", "noscript"]):
                    tag.decompose()
                text = " ".join([p.get_text() for p in soup.find_all(["p", "div"])])
                text = " ".join(text.split())
                crawled.append({"url": url, "text": text or "(Minimal text)"})
                visited.add(url)

                # Extract internal links
                try:
                    links = await page.eval_on_selector_all(
                        "a[href]", "els => els.map(e => e.href)"
                    )
                    for link in links:
                        if urlparse(link).netloc == domain and link not in visited and link not in to_visit:
                            to_visit.append(link)
                except:
                    pass

            except Exception as e:
                print(f"STEALTH error on {url}:", e)
            finally:
                await page.close()

        await browser.close()
    return crawled


def stealth_crawl(url, max_pages):
    return asyncio.run(stealth_crawl_async(url, max_pages))


# ------------------------------
# AUTO-DECISION CRAWLER
# ------------------------------
def crawl_website(url, max_pages=10):
    print(f"🚀 Crawling started for: {url}")
    print("🟢 Trying FAST mode first…")
    fast_text, html = fast_crawl_single(url)

    if detect_heavy_js(fast_text, html):
        print("⚠ Detected heavy JS / bot-protected → Using STEALTH mode (may take time)")
        return stealth_crawl(url, max_pages)
    else:
        print("✅ FAST mode OK → Crawling normally")
        return fast_crawl(url, max_pages)


# ------------------------------
# Example usage
# ------------------------------
if __name__ == "__main__":
    url = "https://www.goindigo.in/"
    data = crawl_website(url, max_pages=5)
    for i, page in enumerate(data, 1):
        print(f"\nPage {i} — {page['url']}\nText length: {len(page['text'])}")
