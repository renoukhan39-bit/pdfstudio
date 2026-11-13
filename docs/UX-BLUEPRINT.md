# Product UX and Editor Blueprint

## Core experience
1. Land on a fast, searchable catalog with categories and clear upload CTA.
2. Upload from device (and later optional connected cloud providers).
3. Show local-versus-server processing status and applicable file limits.
4. Open the **continuous PDF workspace**: thumbnail navigator, central canvas, active tools, inspector/properties, file and revision info.
5. Process with progress, cancellation and actionable errors.
6. Preview original vs result (visual diff where useful); keep an undoable working revision.
7. Download, export, continue editing, or start a reusable workflow.

## Proposed information architecture
- **Home / All Tools**: discover PDF functions by category and search.
- **Edit PDF**: Sejda-inspired clarity, not a copy of competitor design.
- **Organize**: merge/split/extract/rearrange/crop/rotate/alternate/bookmarks.
- **Convert**: PDF ↔ Office/images/HTML/text/Markdown.
- **Optimize**: compress/OCR/repair/archival/deskew.
- **Protect & Sign**: encrypt/unlock authorized files/redact/forms/signatures.
- **AI**: summary, grounded chat, translation, structured extraction.
- **Workflows**: chain and batch tools, history/progress.
- **Account** (later): saved files, billing, privacy settings, teams.

## Editor controls
Top toolbar: Text · Image · Draw · Highlight · Shapes · Link · Forms · Sign · Pages · Find/Replace · Undo/Redo · Export.
Left rail: thumbnails, bookmarks, document outline.
Center: zoomed PDF page(s) with selection handles.
Right properties panel: font, size, colors, alignment, layers, field/link attributes.
Bottom: page count, zoom, processing state and save warnings.
On mobile: collapsible panels and limited direct-manipulation affordances.

## UX safeguards
- Explicit labels: **edit existing text** vs **add overlay text**.
- Separate whiteout from secure redaction and clearly warn about differences.
- Explain when a signature is merely visual versus digitally verifiable.
- Preserve original file or let users work on a copy by default.
- No silent upload to AI or third-party APIs.
- Keyboard accessibility, screen-reader semantics, responsive design and usable error messages.

## Differentiating experiences
- One upload + multiple operations without reuploading.
- Drag/drop workflow builder later.
- Before/after visual comparison, output validation messages.
- Clear “processed locally” indication for browser-only tools.
- Optional multilingual UI: English, Hindi, Punjabi, others after testing.

## Design deliverables before UI coding
Journey map; page wireframes; editor interaction prototype; tool cards taxonomy; component design tokens; accessibility spec; loading/error/empty states; responsive acceptance screenshots.
