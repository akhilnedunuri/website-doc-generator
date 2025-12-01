// =======================
// AUTO DETECT BACKEND URL
// =======================

// 🔥 CRITICAL: Replace this with your actual, live backend URL on Render.
// If your service is down or the URL is wrong, the frontend will fail to fetch.
const GLOBAL_URL = "https://web-doc-generator.pbshope.in"; 

const BACKEND_URL =
    window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
        ? "http://127.0.0.1:8000" // Use 8000 for local uvicorn run
        : GLOBAL_URL;


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

// Helper to update message text and styling
function updateMessage(text, isError = false) {
    messageDiv.textContent = text;
    // Clear previous classes and set new ones for visual feedback
    messageDiv.className = "status-message " + (isError ? "error" : "success");
}

// Check if backend URL is configured correctly on load
console.log(`Using Backend URL: ${BACKEND_URL}`);


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

    updateMessage("⏳ Generating documentation... This may take a moment.", false); // Use neutral status first
    actionsDiv.style.display = "none";
    mdContentPre.style.display = "none";
    mdContentPre.textContent = "";

    try {
        const endpoint = `${BACKEND_URL}/generate-docs?url=${encodeURIComponent(url)}&max_pages=${maxPages}`;

        const response = await fetch(endpoint, { 
            method: "POST",
            // Set a higher timeout in your backend configuration if the process takes too long!
        });

        if (!response.ok) {
            let errorMsg = `Server responded with status ${response.status}.`;
            try {
                // Try to get detailed error from the JSON body sent by FastAPI
                const err = await response.json();
                if (err.detail) errorMsg = err.detail;
            } catch (e) {
                // If it wasn't JSON, just use the status message
                errorMsg += " (No detailed error message from server)";
            }
            throw new Error(errorMsg);
        }

        const data = await response.json();
        updateMessage("✅ Documentation generated successfully!", false);

        // Links use the base URL provided by the backend, which handles http/https/port correctly
        currentMdUrl = `${BACKEND_URL}${data.view_md_url}`;
        currentMdDownloadUrl = `${BACKEND_URL}${data.download_md_url}`;
        currentPdfDownloadUrl = `${BACKEND_URL}${data.download_pdf_url}`;

        actionsDiv.style.display = "block";

    } catch (error) {
        console.error("Frontend Fetch Error:", error);
        updateMessage(`❌ Error: Could not reach the server or process the request. Details: ${error.message}`, true);
    }
});


// =======================
// VIEW MARKDOWN
// =======================
viewMdBtn.addEventListener("click", async () => {
    if (!currentMdUrl) return;

    try {
        mdContentPre.textContent = "Loading Markdown...";
        mdContentPre.style.display = "block";

        const response = await fetch(currentMdUrl);
        if (!response.ok) throw new Error(`Failed to fetch Markdown (${response.status})`);

        const mdText = await response.text();
        mdContentPre.textContent = mdText;
    } catch (error) {
        console.error(error);
        mdContentPre.textContent = `Error fetching Markdown: ${error.message}`;
    }
});


// =======================
// DOWNLOAD FILES (Triggers direct download via browser)
// =======================
downloadMdBtn.addEventListener("click", () => {
    if (!currentMdDownloadUrl) return;
    window.open(currentMdDownloadUrl, "_blank");
});

downloadPdfBtn.addEventListener("click", () => {
    if (!currentPdfDownloadUrl) return;
    window.open(currentPdfDownloadUrl, "_blank");
});