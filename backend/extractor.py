from bs4 import BeautifulSoup

def extract_page_data(html_content):
    soup = BeautifulSoup(html_content, "html.parser")

    title = soup.title.text if soup.title else "No Title"
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_desc = meta_desc_tag["content"] if meta_desc_tag else "No Meta Description"

    headings = {
        "h1": [h.text.strip() for h in soup.find_all("h1")],
        "h2": [h.text.strip() for h in soup.find_all("h2")],
        "h3": [h.text.strip() for h in soup.find_all("h3")]
    }

    paragraphs = [p.text.strip() for p in soup.find_all("p")]
    content = "\n".join(paragraphs[:10])  # limit clutter

    return {
        "title": title,
        "meta_description": meta_desc,
        "headings": headings,
        "content": content
    }
