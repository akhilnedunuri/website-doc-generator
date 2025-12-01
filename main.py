from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from io import BytesIO
import uuid
import os
import sys


# ------------------------------------------------------
# BASE PATH FIX (WORKS LOCALLY + RENDER)
# ------------------------------------------------------
CURRENT_FILE = Path(__file__).resolve()
BASE_DIR = CURRENT_FILE.parent        # this = project root (contains frontend/, backend/)
BACKEND_DIR = BASE_DIR / "backend"
FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"

# Allow importing from backend/
sys.path.append(str(BACKEND_DIR))


# Import backend modules
from crawler import crawl_website
from summarizer import summarize_domain, summarize_page
from md_generator import generate_markdown_content
from pdf_generator import md_to_pdf_better


# ------------------------------------------------------
# FASTAPI INITIALIZATION
# ------------------------------------------------------
app = FastAPI(title="Website Markdown & PDF Generator", version="1.0")


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        proto = request.headers.get("x-forwarded-proto")
        if proto == "https":
            request.scope["scheme"] = "https"
        response = await call_next(request)
        return response

app.add_middleware(HTTPSRedirectMiddleware)

# ------------------------------------------------------
# STATIC FILES (CSS + JS)
# ------------------------------------------------------
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
else:
    print("⚠ WARNING: static/ folder NOT found at", STATIC_DIR)


# ------------------------------------------------------
# SERVE FRONTEND INDEX.HTML
# ------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    index_path = FRONTEND_DIR / "index.html"

    if not index_path.exists():
        return f"""
        <h2>Frontend not found!</h2>
        <p>Looking for file:</p>
        <pre>{index_path}</pre>
        """

    # Read HTML content
    return index_path.read_text(encoding="utf-8")


# Store generated docs
app.state.docs = {}


# ------------------------------------------------------
# GENERATE DOCUMENTATION
# ------------------------------------------------------
@app.post("/generate-docs")
def generate_docs(request: Request, url: str = Query(...), max_pages: int = Query(10)):

    try:
        crawled_pages = crawl_website(url, max_pages)
        if not crawled_pages:
            raise HTTPException(status_code=400, detail="No pages crawled.")

        combined_text = "\n".join([p["text"] for p in crawled_pages])

        domain_summary = summarize_domain(combined_text, url, len(crawled_pages))

        pages_list_md = "\n".join([f"- {p['url']}" for p in crawled_pages])

        page_details_md = ""
        for idx, page in enumerate(crawled_pages, start=1):
            summary = summarize_page(page["text"], page["url"])
            page_details_md += f"""
### Page {idx} — {page['url']}
{summary}

---
"""

        # Generate Markdown
        _, md_text = generate_markdown_content(
            domain=url,
            pages_list_md=pages_list_md,
            domain_summary=domain_summary,
            page_details_md=page_details_md
        )

        # Generate PDF
        pdf_bytes = BytesIO()
        md_to_pdf_better(md_text, pdf_bytes, input_is_text=True)
        pdf_bytes.seek(0)

        # Store
        doc_id = str(uuid.uuid4())
        app.state.docs[doc_id] = {"md": md_text, "pdf": pdf_bytes}

        backend_url = str(request.base_url).rstrip("/")

        return {
            "message": "Documentation generated successfully!",
            "doc_id": doc_id,
            "view_md_url": f"{backend_url}/view-md/{doc_id}",
            "download_md_url": f"{backend_url}/download-md/{doc_id}",
            "download_pdf_url": f"{backend_url}/download-pdf/{doc_id}",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ------------------------------------------------------
# ROUTES FOR VIEW/DOWNLOAD
# ------------------------------------------------------
@app.get("/view-md/{doc_id}")
def view_md(doc_id: str):
    if doc_id not in app.state.docs:
        raise HTTPException(status_code=404, detail="Markdown not found")
    return PlainTextResponse(app.state.docs[doc_id]["md"])


@app.get("/download-md/{doc_id}")
def download_md(doc_id: str):
    if doc_id not in app.state.docs:
        raise HTTPException(status_code=404, detail="Markdown not found")

    md_bytes = BytesIO(app.state.docs[doc_id]["md"].encode("utf-8"))
    md_bytes.seek(0)

    return StreamingResponse(
        md_bytes,
        media_type="text/markdown",
        headers={"Content-Disposition": "attachment; filename=documentation.md"},
    )


@app.get("/download-pdf/{doc_id}")
def download_pdf(doc_id: str):
    if doc_id not in app.state.docs:
        raise HTTPException(status_code=404, detail="PDF not found")

    pdf_bytes = app.state.docs[doc_id]["pdf"]
    pdf_bytes.seek(0)

    return StreamingResponse(
        pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=documentation.pdf"},
    )


# ------------------------------------------------------
# ENTRY FOR RENDER + LOCAL
# ------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
