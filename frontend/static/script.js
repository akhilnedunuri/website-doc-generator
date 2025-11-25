// =======================
// AUTO DETECT BACKEND URL
// =======================

// 🔥 Replace this with your actual backend URL on Render
const RENDER_BACKEND = "https://website-doc-generator.onrender.com";  
// (Use your own Render backend URL)

const BACKEND_URL =
    window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : RENDER_BACKEND;


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


// =======================
// GENERATE DOCUMENTATION
// =======================
generateBtn.addEventListener("click", async () => {
    const url = document.getElementById("url").value.trim();
    const maxPages = document.getElementById("max_pages").value;

    if (!url) {
        alert("Please enter a website URL");
        return;
    }

    messageDiv.textContent = "Generating documentation... Please wait.";
    actionsDiv.style.display = "none";
    mdContentPre.style.display = "none";
    mdContentPre.textContent = "";

    try {
        const endpoint = `${BACKEND_URL}/generate-docs?url=${encodeURIComponent(url)}&max_pages=${maxPages}`;

        console.log("Calling backend:", endpoint);

        const response = await fetch(endpoint, { method: "POST" });

        if (!response.ok) {
            let errorMsg = "Failed to generate documentation";
            try {
                const err = await response.json();
                if (err.detail) errorMsg = err.detail;
            } catch (e) {}
            throw new Error(errorMsg);
        }

        const data = await response.json();
        messageDiv.textContent = "✅ Documentation generated successfully!";

        // These links are already absolute URLs from backend
        currentMdUrl = data.view_md_url;
        currentMdDownloadUrl = data.download_md_url;
        currentPdfDownloadUrl = data.download_pdf_url;

        actionsDiv.style.display = "block";

    } catch (error) {
        console.error("Frontend Error:", error);
        messageDiv.textContent = "❌ Error: " + error.message;
    }
});


// =======================
// VIEW MARKDOWN
// =======================
viewMdBtn.addEventListener("click", async () => {
    if (!currentMdUrl) return;

    try {
        const response = await fetch(currentMdUrl);
        if (!response.ok) throw new Error("Failed to fetch Markdown");

        const mdText = await response.text();
        mdContentPre.textContent = mdText;
        mdContentPre.style.display = "block";
    } catch (error) {
        console.error(error);
        alert("Error fetching Markdown: " + error.message);
    }
});


// =======================
// DOWNLOAD FILES
// =======================
downloadMdBtn.addEventListener("click", () => {
    if (!currentMdDownloadUrl) return;
    window.open(currentMdDownloadUrl, "_blank");
});

downloadPdfBtn.addEventListener("click", () => {
    if (!currentPdfDownloadUrl) return;
    window.open(currentPdfDownloadUrl, "_blank");
});
