const form = document.getElementById("upload-form");
const status = document.getElementById("status");
const fileInput = document.getElementById("files");
const dropzone = document.getElementById("dropzone");
const filelist = document.getElementById("filelist");
const progress = document.getElementById("progress");
const bar = document.getElementById("bar");
const submitBtn = document.getElementById("submit-btn");

const I18N = window.I18N || {};

function plural(entry, n) {
    return (n === 1 ? entry.one : entry.other).replace("{n}", n);
}

function updateList() {
    const n = fileInput.files.length;
    filelist.textContent = n ? plural(I18N.selected, n) : "";
}
fileInput.addEventListener("change", updateList);

["dragenter", "dragover"].forEach(ev =>
    dropzone.addEventListener(ev, e => { e.preventDefault(); dropzone.classList.add("drag"); }));
["dragleave", "drop"].forEach(ev =>
    dropzone.addEventListener(ev, e => { e.preventDefault(); dropzone.classList.remove("drag"); }));
dropzone.addEventListener("drop", e => {
    if (e.dataTransfer.files.length) { fileInput.files = e.dataTransfer.files; updateList(); }
});

form.addEventListener("submit", function (event) {
    event.preventDefault();
    const files = fileInput.files;
    if (!files.length) return;

    submitBtn.disabled = true;
    submitBtn.style.opacity = ".6";
    progress.classList.add("show");
    status.textContent = plural(I18N.uploading, files.length);

    const data = new FormData(form);
    const xhr = new XMLHttpRequest();
    xhr.open("POST", "/upload");

    xhr.upload.onprogress = function (e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            bar.style.width = percent + "%";
            status.textContent = I18N.uploading_percent.replace("{p}", percent);
        }
    };

    xhr.onload = function () {
        document.open();
        document.write(xhr.responseText);
        document.close();
    };

    xhr.onerror = function () {
        status.textContent = I18N.error;
        submitBtn.disabled = false;
        submitBtn.style.opacity = "1";
    };

    xhr.send(data);
});
