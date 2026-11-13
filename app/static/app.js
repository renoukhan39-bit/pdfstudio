(() => {
  "use strict";
  const input = document.querySelector("#fileInput");
  const zone = document.querySelector("#dropzone");
  const container = document.querySelector("#queue-container");
  const list = document.querySelector("#file-list");
  const count = document.querySelector("#file-count");
  const mergeButton = document.querySelector("#merge-button");
  const status = document.querySelector("#merge-status");
  const clearButton = document.querySelector("#clear-files");
  const MAX_FILE_BYTES = 8 * 1024 * 1024;
  const MAX_FILES = 10;
  let selectedFiles = [];
  let processing = false;

  function updateStatus(message, isError = false) {
    status.textContent = message;
    status.classList.toggle("error", isError);
  }
  function humanBytes(bytes) {
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  }
  function move(index, delta) {
    const target = index + delta;
    if (target < 0 || target >= selectedFiles.length || processing) return;
    [selectedFiles[index], selectedFiles[target]] = [selectedFiles[target], selectedFiles[index]];
    render();
  }
  function button(label, title, handler, disabled) {
    const element = document.createElement("button");
    element.type = "button";
    element.textContent = label;
    element.title = title;
    element.setAttribute("aria-label", title);
    element.disabled = disabled;
    element.addEventListener("click", handler);
    return element;
  }
  function render() {
    list.replaceChildren();
    count.textContent = `(${selectedFiles.length})`;
    container.hidden = selectedFiles.length === 0;
    mergeButton.disabled = processing || selectedFiles.length < 2;
    mergeButton.textContent = processing ? "Merging…" : "Merge PDFs →";
    selectedFiles.forEach((file, index) => {
      const li = document.createElement("li");
      li.className = "file-row";
      const badge = document.createElement("span");
      badge.className = "file-badge";
      badge.textContent = "PDF";
      const info = document.createElement("span");
      info.className = "file-info";
      const name = document.createElement("strong");
      name.textContent = file.name;
      const size = document.createElement("small");
      size.textContent = humanBytes(file.size);
      info.append(name, size);
      const actions = document.createElement("span");
      actions.className = "file-actions";
      actions.append(
        button("↑", `Move ${file.name} up`, () => move(index, -1), processing || index === 0),
        button("↓", `Move ${file.name} down`, () => move(index, 1), processing || index === selectedFiles.length - 1),
        button("×", `Remove ${file.name}`, () => { selectedFiles.splice(index, 1); render(); }, processing)
      );
      li.append(badge, info, actions);
      list.append(li);
    });
  }
  function addFiles(files) {
    if (processing) return;
    const candidates = [...files];
    if (selectedFiles.length + candidates.length > MAX_FILES) {
      updateStatus(`Select no more than ${MAX_FILES} PDF files.`, true);
      return;
    }
    for (const file of candidates) {
      if (!file.name.toLowerCase().endsWith(".pdf") || file.size > MAX_FILE_BYTES || file.size === 0) {
        updateStatus("Use nonempty PDF files no larger than 8 MB each.", true);
        return;
      }
    }
    selectedFiles = selectedFiles.concat(candidates);
    updateStatus(selectedFiles.length < 2 ? "Add one more PDF to begin." : "Ready to merge your PDFs.");
    render();
  }
  input.addEventListener("change", () => { addFiles(input.files); input.value = ""; });
  clearButton.addEventListener("click", () => {
    if (!processing) { selectedFiles = []; render(); updateStatus("Add at least two PDFs to begin."); }
  });
  zone.addEventListener("dragover", event => { event.preventDefault(); zone.classList.add("dragging"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("dragging"));
  zone.addEventListener("drop", event => {
    event.preventDefault();
    zone.classList.remove("dragging");
    addFiles(event.dataTransfer.files);
  });
  mergeButton.addEventListener("click", async () => {
    if (selectedFiles.length < 2 || processing) return;
    processing = true;
    render();
    updateStatus("Combining PDFs…");
    try {
      const formData = new FormData();
      selectedFiles.forEach(file => formData.append("files", file, file.name));
      const response = await fetch("/api/tools/merge", { method: "POST", body: formData, cache: "no-store" });
      if (!response.ok) {
        let message = `Merge failed (HTTP ${response.status}).`;
        try { const payload = await response.json(); message = payload.detail || message; } catch (_) { /* Keep generic message. */ }
        throw new Error(message);
      }
      const pdf = await response.blob();
      if (pdf.type !== "application/pdf" || pdf.size === 0) throw new Error("The server returned an unexpected file.");
      const url = URL.createObjectURL(pdf);
      const link = document.createElement("a");
      link.href = url;
      link.download = "pdfstudio-merged.pdf";
      document.body.append(link);
      link.click();
      link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 10000);
      updateStatus("Success! Your merged PDF is downloading.");
    } catch (error) {
      updateStatus(error instanceof Error ? error.message : "Something went wrong.", true);
    } finally {
      processing = false;
      render();
    }
  });
  render();
})();
