// =======================
// AUTO DETECT BACKEND URL
// =======================
const BACKEND_URL =
    window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000"
        : "https://your-render-backend-url.onrender.com";  // ← Replace after deploying


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
    const url = document.getElementById("url").value;
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
        const response = await fetch(
            `${BACKEND_URL}/generate-docs?url=${encodeURIComponent(url)}&max_pages=${maxPages}`,
            { method: "POST" }
        );

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Failed to generate documentation");
        }

        const data = await response.json();

        messageDiv.textContent = "✅ Generation completed!";

        // IMPORTANT FIX → URLs are already absolute!
        currentMdUrl = data.view_md_url;
        currentMdDownloadUrl = data.download_md_url;
        currentPdfDownloadUrl = data.download_pdf_url;

        actionsDiv.style.display = "block";

    } catch (error) {
        console.error(error);
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
