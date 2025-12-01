import asyncio
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError


# ---------------------------------------------------------
# FAST MODE (Static HTML websites)
# ---------------------------------------------------------
def fast_crawl_single(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, timeout=15, headers=headers)
        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()

        # extract text
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


# ---------------------------------------------------------
# Detect Heavy-JS or Bot Protection
# ---------------------------------------------------------
def detect_heavy_js(text, html):
    if len(text) < 100:
        return True
    bot_words = ["captcha", "robot", "cf-browser-verification", "challenge"]
    return any(b in html.lower() for b in bot_words)


# ---------------------------------------------------------
# STEALTH MODE (Playwright Headless Chromium)
# ---------------------------------------------------------
async def stealth_crawl_async(start_url, max_pages=10):
    visited = set()
    to_visit = [start_url]
    domain = urlparse(start_url).netloc
    crawled = []

    async with async_playwright() as p:

        # ***************************************************
        # MOST IMPORTANT PART → Chromium works WITHOUT sandbox
        # ***************************************************
        browser = await p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-blink-features=AutomationControlled",
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
                # multiple fallback loads
                try:
                    await page.goto(url, timeout=120000, wait_until="networkidle")
                except PlaywrightTimeoutError:
                    try:
                        await page.goto(url, timeout=120000, wait_until="domcontentloaded")
                    except PlaywrightTimeoutError:
                        await page.goto(url, timeout=120000)

                # scroll to load dynamic content
                previous_height = await page.evaluate("document.body.scrollHeight")
                for _ in range(10):
                    await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                    await asyncio.sleep(0.4)
                    new_height = await page.evaluate("document.body.scrollHeight")
                    if new_height == previous_height:
                        break
                    previous_height = new_height

                # extract HTML
                html = await page.content()
                soup = BeautifulSoup(html, "html.parser")

                for tag in soup(["script", "style", "noscript"]):
                    tag.decompose()

                text = " ".join([p.get_text() for p in soup.find_all(["p", "div"])])
                text = " ".join(text.split())

                crawled.append({"url": url, "text": text or "(Minimal text)"})
                visited.add(url)

                # extract internal links
                try:
                    links = await page.eval_on_selector_all(
                        "a[href]", "els => els.map(e => e.href)"
                    )
                    for link in links:
                        if urlparse(link).netloc == domain and link not in visited:
                            to_visit.append(link)
                except:
                    pass

            except Exception as e:
                print("STEALTH ERROR:", e)

            finally:
                await page.close()

        await browser.close()

    return crawled


def stealth_crawl(url, max_pages):
    return asyncio.run(stealth_crawl_async(url, max_pages))


# ---------------------------------------------------------
# AUTO MODE → Detect → Fast or Stealth
# ---------------------------------------------------------
def crawl_website(url, max_pages=10):
    print(f"🚀 Crawling started for: {url}")
    print("🟢 Trying FAST mode first…")

    fast_text, html = fast_crawl_single(url)

    if detect_heavy_js(fast_text, html):
        print("⚠ Heavy JS detected → Using STEALTH mode")
        return stealth_crawl(url, max_pages)

    print("✅ FAST mode OK → Using FAST crawler")
    return fast_crawl(url, max_pages)


# ---------------------------------------------------------
# Debug Example
# ---------------------------------------------------------
if __name__ == "__main__":
    url = "https://www.goindigo.in/"
    data = crawl_website(url, max_pages=5)
    for i, page in enumerate(data, 1):
        print(f"\nPage {i}: {page['url']}\nLength: {len(page['text'])}")
