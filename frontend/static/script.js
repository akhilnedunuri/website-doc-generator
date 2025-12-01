// =======================
// AUTO DETECT BACKEND URL
// =======================

// If running on localhost it will call local backend; otherwise use same origin
const BACKEND_URL =
    window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : window.location.origin; // use the current origin for deployed app (works with Coolify)


// =======================
// UI ELEMENTS
// =======================
const generateBtn = document.getElementById("generateBtn");
const viewMdBtn = document.getElementById("viewMdBtn");
const downloadMdBtn = document.getElementById("downloadMdBtn");
const downloadPdfBtn = document.getElementById("downloadPdfBtn");
const messageDiv = document.getElementById("message");
const actionsDiv = document.getElementById("actions");
const mdContentPre = document.getElementById("mdContent");

let currentMdUrl = "";
let currentMdDownloadUrl = "";
let currentPdfDownloadUrl = "";

function updateMessage(text, isError = false) {
    messageDiv.textContent = text;
    messageDiv.className = "status-message " + (isError ? "error" : "success");
}

// Normalize a returned URL (accept absolute or relative)
function normalizeReturnedUrl(returned) {
    if (!returned) return "";
    returned = returned.trim();
    // already absolute
    if (/^https?:\/\//i.test(returned)) return returned;
    // absolute path (starts with /) -> prefix with origin/back-end
    if (returned.startsWith("/")) return BACKEND_URL.replace(/\/$/, "") + returned;
    // otherwise, assume relative and add slash
    return BACKEND_URL.replace(/\/$/, "") + "/" + returned;
}

console.log("Using BACKEND_URL =", BACKEND_URL);

// =======================
// GENERATE DOCUMENTATION
// =======================
generateBtn.addEventListener("click", async () => {
    const url = document.getElementById("url").value.trim();
    const maxPages = document.getElementById("max_pages").value || 10;

    if (!url) {
        alert("Please enter a website URL");
        return;
    }

    updateMessage("⏳ Generating documentation... This may take a while for large sites.");
    actionsDiv.style.display = "none";
    mdContentPre.style.display = "none";
    mdContentPre.textContent = "";

    try {
        const endpoint = `${BACKEND_URL}/generate-docs?url=${encodeURIComponent(url)}&max_pages=${maxPages}`;
        const response = await fetch(endpoint, { method: "POST" });

        if (!response.ok) {
            let errMsg = `Server returned ${response.status}`;
            try {
                const body = await response.json();
                if (body.detail) errMsg = body.detail;
            } catch (_) { /* not JSON */ }
            throw new Error(errMsg);
        }

        const data = await response.json();
        updateMessage("✅ Documentation generated!");

        // Normalize returned urls (works if backend returns absolute OR relative)
        currentMdUrl = normalizeReturnedUrl(data.view_md_url);
        currentMdDownloadUrl = normalizeReturnedUrl(data.download_md_url);
        currentPdfDownloadUrl = normalizeReturnedUrl(data.download_pdf_url);

        console.log("Resolved URLs:", { currentMdUrl, currentMdDownloadUrl, currentPdfDownloadUrl });

        actionsDiv.style.display = "block";
    } catch (err) {
        console.error("Generate error:", err);
        updateMessage("❌ " + err.message, true);
    }
});

// =======================
// VIEW MARKDOWN
// =======================
viewMdBtn.addEventListener("click", async () => {
    if (!currentMdUrl) return;
    mdContentPre.textContent = "Loading Markdown...";
    mdContentPre.style.display = "block";

    try {
        const res = await fetch(currentMdUrl);
        if (!res.ok) throw new Error(`Server returned ${res.status}`);
        const txt = await res.text();
        mdContentPre.textContent = txt;
    } catch (err) {
        console.error("View MD error:", err);
        mdContentPre.textContent = "Error fetching Markdown: " + err.message;
    }
});

// =======================
// DOWNLOAD FILES
// =======================
downloadMdBtn.addEventListener("click", () => {
    if (!currentMdDownloadUrl) return alert("No markdown available");
    window.open(currentMdDownloadUrl, "_blank");
});

downloadPdfBtn.addEventListener("click", () => {
    if (!currentPdfDownloadUrl) return alert("No PDF available");
    window.open(currentPdfDownloadUrl, "_blank");
});
