from datetime import datetime

def generate_markdown_content(domain: str, pages_list_md: str, domain_summary: str, page_details_md: str):
    """
    Generates clean Markdown content and a safe filename.
    Returns:
        tuple: (filename, full_markdown_text)
    """
    # Safe filename
    safe_domain = (
        domain.replace("https://", "")
              .replace("http://", "")
              .replace("/", "_")
              .replace(":", "_")
    )

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_domain}_{timestamp}.md"

    md_content = f"""# 📘 Website Documentation Report

**🌐 Domain:** {domain}  
**📅 Generated On:** {timestamp}

---

## 🔗 1. List of Crawled URLs

{pages_list_md}

---

## 🌍 2. Domain Summary

{domain_summary}

---

## 📄 3. Detailed Page Summaries

{page_details_md}

---

## 📝 4. Final Notes

- This documentation was generated using AI.  
- Summaries are optimized for readability.  
- Useful for SEO audits, analysis & reports.  
- Professional, structured, clean Markdown.
"""

    return filename, md_content
