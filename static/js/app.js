const fileInput = document.getElementById("fileInput");
const browseBtn = document.getElementById("browseBtn");
const uploadBtn = document.getElementById("uploadBtn");
const loading = document.getElementById("loading");
const result = document.getElementById("result");
const downloadSection = document.getElementById("downloadSection");
const dropZone = document.getElementById("dropZone");
const fileMeta = document.getElementById("fileMeta");
const dashboard = document.getElementById("dashboard");
const emailCount = document.getElementById("emailCount");
const resultsWrap = document.getElementById("resultsWrap");
const resultsInfo = document.getElementById("resultsInfo");
const themeToggle = document.getElementById("themeToggle");

let downloadJobId = null;

function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    themeToggle.textContent = theme === "dark" ? "Light mode" : "Dark mode";
}

const savedTheme = localStorage.getItem("leadflow_theme");
const initialTheme = savedTheme || "light";
applyTheme(initialTheme);

themeToggle.addEventListener("click", () => {
    const nextTheme = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    applyTheme(nextTheme);
    localStorage.setItem("leadflow_theme", nextTheme);
});

browseBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", () => {
    const file = fileInput.files[0];
    fileMeta.textContent = file ? `Selected: ${file.name}` : "No file selected";
});

dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("dragover");
});

dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("dragover");
});

dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    fileInput.files = e.dataTransfer.files;
    const file = fileInput.files[0];
    fileMeta.textContent = file ? `Selected: ${file.name}` : "No file selected";
});

uploadBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];

    if (!file) {
        alert("Please select a CSV or XLSX file first.");
        return;
    }

    loading.style.display = "flex";
    dashboard.style.display = "none";
    resultsWrap.style.display = "none";
    result.innerHTML = "";
    downloadSection.innerHTML = "";
    downloadJobId = null;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/api/upload/", {
            method: "POST",
            body: formData
        });

        const data = await response.json();
        loading.style.display = "none";

        if (!data.success) {
            alert(data.message || "Upload failed.");
            return;
        }

        downloadJobId = data.job_id;

        dashboard.style.display = "grid";
        resultsWrap.style.display = "block";

        emailCount.textContent = data.total_emails;
        resultsInfo.textContent = `Showing a preview of ${Math.min(data.preview_emails.length, 20)} emails only. The full list is available in the CSV download.`;

        const previewEmails = data.preview_emails || [];
        result.innerHTML = previewEmails.map(email => `
            <div class="email-item">${email}</div>
        `).join("");

        downloadSection.innerHTML = `
            <a class="download-link" href="/api/download/${downloadJobId}/">
                <button type="button" class="primary-btn">Download Emails CSV</button>
            </a>
        `;
    } catch (error) {
        loading.style.display = "none";
        alert("Something went wrong while processing the file.");
    }
});