(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const input = $("fileInput"), select = $("tool-select"), run = $("merge-button");
  const status = $("merge-status"), zone = $("dropzone"), list = $("file-list");
  const limits = {file: 8 * 1024 * 1024, total: 40 * 1024 * 1024};
  let files = [], tools = [], busy = false, lastResult = null;
  const tool = () => tools.find(item => item.slug === select.value);
  function message(text, error = false) { status.textContent = text; status.classList.toggle("error", error); }
  function action(text, label, handler, disabled) {
    const button = document.createElement("button");
    button.type = "button"; button.textContent = text; button.setAttribute("aria-label", label);
    button.disabled = disabled; button.addEventListener("click", handler); return button;
  }
  function render() {
    const merge = select.value === "merge";
    const docx = select.value === "docx-to-pdf";
    input.multiple = merge; input.disabled = busy; select.disabled = busy;
    $("clear-files").disabled = busy;
    $("queue-container").hidden = files.length === 0; $("file-count").textContent = `(${files.length})`;
    run.disabled = busy || !tool() || files.length < (merge ? 2 : 1);
    run.textContent = busy ? "Processing…" : `${tool()?.name || "Choose a tool"} →`;
    $("file-limits").textContent = `${merge ? "2–10 PDFs" : docx ? "One DOCX file" : "One PDF"} · 8 MB each · 200 pages max output`;
    list.replaceChildren();
    files.forEach((file, index) => {
      const row = document.createElement("li"); row.className = "file-row";
      const info = document.createElement("span"); info.className = "file-info";
      const name = document.createElement("strong"); name.textContent = file.name;
      const size = document.createElement("small"); size.textContent = `${(file.size / 1048576).toFixed(2)} MB`;
      info.append(name, size);
      const controls = document.createElement("span"); controls.className = "file-actions";
      [-1, 1].forEach(delta => controls.append(action(delta < 0 ? "↑" : "↓", `Move ${file.name} ${delta < 0 ? "up" : "down"}`, () => {
        [files[index], files[index + delta]] = [files[index + delta], files[index]]; render();
      }, busy || index + delta < 0 || index + delta >= files.length)));
      controls.append(action("×", `Remove ${file.name}`, () => { files.splice(index, 1); render(); }, busy));
      row.append(info, controls); list.append(row);
    });
    document.querySelectorAll("#options-panel input, #options-panel select").forEach(el => { el.disabled = busy; });
    $("use-result").disabled = busy;
  }
  function changeTool() {
    const slug = select.value;
    const docx = slug === "docx-to-pdf";
    input.accept = docx ? ".docx,application/vnd.openxmlformats-officedocument.wordprocessingml.document" : ".pdf,application/pdf";
    if (files.some(file => !file.name.toLowerCase().endsWith(docx ? ".docx" : ".pdf"))) {
      files = []; message("Choose the correct file type for this tool.");
    } else if (slug !== "merge" && files.length > 1) {
      files = files.slice(0, 1); message("Kept the first document for this tool.");
    } else message("Add files, review your options, then process.");
    $("tool-heading").textContent = tool().name; $("tool-description").textContent = tool().description;
    $("pages-group").hidden = !["split", "extract", "delete", "reorder", "rotate", "text", "page-numbers", "watermark", "crop"].includes(slug);
    $("angle-group").hidden = slug !== "rotate";
    $("password-group").hidden = !["protect", "unlock"].includes(slug);
    $("metadata-group").hidden = slug !== "metadata";
    $("watermark-group").hidden = slug !== "watermark";
    $("crop-group").hidden = slug !== "crop";
    $("page-selection").value = ""; $("pdf-password").value = "";
    $("page-help").textContent = slug === "split" ? "Leave blank for one PDF per page, or enter groups: 1-3;4-6." : slug === "reorder" ? "Include every page once, for example 3,1,2." : ["rotate", "text", "page-numbers", "watermark", "crop"].includes(slug) ? "Leave blank for all pages, or use 1,3-5." : "Required: use 1,3-5. Each page can appear once.";
    render();
  }
  function add(incoming) {
    if (busy) return;
    const added = [...incoming], next = files.concat(added), max = select.value === "merge" ? 10 : 1;
    const docx = select.value === "docx-to-pdf";
    if (next.length > max) return message(`This tool accepts ${max === 1 ? "one file. Clear the current file first" : "up to 10 PDFs"}.`, true);
    if (added.some(f => !f.name.toLowerCase().endsWith(docx ? ".docx" : ".pdf") || !f.size || f.size > limits.file)) return message(`Choose nonempty ${docx ? "DOCX" : "PDF"} files no larger than 8 MB each.`, true);
    if (next.reduce((sum, f) => sum + f.size, 0) > limits.total) return message("Combined files cannot exceed 40 MB.", true);
    files = next; message("Files ready. Review the selected tool and options."); render();
  }
  input.addEventListener("change", () => { add(input.files); input.value = ""; });
  select.addEventListener("change", changeTool);
  $("clear-files").addEventListener("click", () => { files = []; lastResult = null; $("use-result").hidden = true; $("pdf-password").value = ""; render(); message("Files cleared."); });
  zone.addEventListener("dragover", event => { event.preventDefault(); zone.classList.add("dragging"); });
  zone.addEventListener("dragleave", () => zone.classList.remove("dragging"));
  zone.addEventListener("drop", event => { event.preventDefault(); zone.classList.remove("dragging"); add(event.dataTransfer.files); });
  $("use-result").addEventListener("click", () => {
    if (!lastResult || busy) return;
    if (select.value === "docx-to-pdf") { select.value = "extract"; changeTool(); }
    files = [new File([lastResult.blob], lastResult.name, {type: "application/pdf"})];
    render(); message("Result selected. Choose the next tool to continue."); select.focus();
  });
  run.addEventListener("click", async () => {
    if (run.disabled) return;
    const slug = select.value, options = {}, form = new FormData();
    if (!$("pages-group").hidden) options.pages = $("page-selection").value;
    if (slug === "watermark") options.text = $("watermark-text").value;
    if (slug === "crop") options.margin = $("crop-margin").value;
    if (slug === "rotate") options.angle = $("rotation").value;
    if (["protect", "unlock"].includes(slug)) options.password = $("pdf-password").value;
    if (slug === "metadata") ["title", "author", "subject", "keywords"].forEach(key => { options[key] = $(`pdf-${key}`).value; });
    files.forEach(file => form.append(slug === "merge" ? "files" : "file", file, file.name));
    if (slug !== "merge" && slug !== "docx-to-pdf") form.append("options", JSON.stringify(options));
    busy = true; lastResult = null; $("use-result").hidden = true; render(); message("Processing your document…");
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 60000);
    try {
      const response = await fetch(`/api/tools/${slug}`, {method: "POST", body: form, cache: "no-store", signal: controller.signal});
      if (!response.ok) {
        let detail = `Processing failed (HTTP ${response.status}).`;
        try { const error = await response.json(); if (typeof error.detail === "string") detail = error.detail; } catch { /* Keep HTTP error. */ }
        throw new Error(detail);
      }
      const blob = await response.blob();
      const mime = blob.type.split(";")[0];
      if (!blob.size || !["application/pdf", "application/zip", "text/plain"].includes(mime)) throw new Error("Unexpected output type.");
      const name = /filename="([a-zA-Z0-9.-]+)"/.exec(response.headers.get("content-disposition") || "")?.[1] || "pdfstudio-result.pdf";
      const url = URL.createObjectURL(blob), link = document.createElement("a");
      link.href = url; link.download = name; document.body.append(link); link.click(); link.remove();
      setTimeout(() => URL.revokeObjectURL(url), 10000);
      if (mime === "application/pdf" && blob.size <= limits.file) { lastResult = {blob, name}; $("use-result").hidden = false; }
      message(`Download ready. ${response.headers.get("X-PDF-Notice") || "Your original file is unchanged."}`);
    } catch (error) { message(error.name === "AbortError" ? "The request timed out. Try a smaller document." : error.message, true); }
    finally { clearTimeout(timer); $("pdf-password").value = ""; busy = false; render(); }
  });
  fetch("/api/tools", {cache: "no-store"}).then(response => { if (!response.ok) throw new Error("Unable to load tools."); return response.json(); }).then(data => {
    tools = data.tools;
    const colors = ["coral", "lavender", "sky", "mint", "gold", "pink"];
    tools.forEach((item, index) => {
      const option = document.createElement("option"); option.value = item.slug; option.textContent = item.name; select.append(option);
      const card = document.createElement("a"); card.className = "tool-card live"; card.href = "#workspace";
      const icon = document.createElement("span"); icon.className = `tool-icon ${colors[index % colors.length]}`; icon.textContent = String(index + 1).padStart(2, "0");
      const title = document.createElement("strong"); title.textContent = item.name;
      const description = document.createElement("p"); description.textContent = item.description;
      const state = document.createElement("small"); state.textContent = "Open tool →";
      card.append(icon, title, description, state); card.addEventListener("click", event => { if (busy) { event.preventDefault(); return; } select.value = item.slug; changeTool(); });
      $("tool-grid").append(card);
    });
    changeTool();
  }).catch(error => message(error.message, true));
  render();
})();
