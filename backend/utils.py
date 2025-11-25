from urllib.parse import urlparse

def clean_domain_name(url: str):
    return urlparse(url).netloc.replace("www.", "")
