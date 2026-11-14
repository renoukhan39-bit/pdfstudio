> Updated: the prototype now includes eleven tools. See [Core Toolkit](CORE-TOOLKIT.md) for current functionality, routes and limits. The historical merge setup below still works.

# Running the First PDF Studio Prototype

**What works:** locally served homepage and **Merge PDF** only. Other tools are roadmap items, not functioning links. **Do not deploy to the open internet yet**: in-process PDF parsing is not isolated against hostile inputs.

## Requirements

- Python 3.11 or newer
- Internet access to install Python dependencies on a new machine
- No Node.js, API key, Gotenberg, or external PDF service required for this first proof of concept

## Local run

~~~bash
git clone https://github.com/renoukhan39-bit/pdfstudio.git
cd pdfstudio
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
python -m pip install -e '.[dev]'
uvicorn app.main:app --reload
~~~

Open **http://127.0.0.1:8000**. Upload two or more PDFs, reorder, merge, and download the combined PDF.

## Tests

~~~bash
python -m pytest -q
python -m compileall -q app
~~~

CI in `.github/workflows/ci.yml` installs pinned dependencies and runs synthetic tests.
See [CI](CI.md) for lint, coverage, package/container checks and failure recovery.

## Docker prototype (local-only)

~~~bash
docker build -t pdfstudio-prototype .
docker run --rm -p 127.0.0.1:8000:8000 pdfstudio-prototype
~~~

## Routes

| Route | Method | Function |
| --- | --- | --- |
| `/` | GET | Homepage |
| `/api/health` | GET | Health indicator |
| `/api/tools` | GET | Minimal tool registry (prototype vs planned) |
| `/api/tools/merge` | POST | Multipart `files`, 2-10 PDFs, output `application/pdf` |

## API sample

~~~bash
curl -f -X POST http://127.0.0.1:8000/api/tools/merge \
  -F 'files=@first.pdf' -F 'files=@second.pdf' \
  --output pdfstudio-merged.pdf
~~~

## Safety and limitations

- This version has only one live tool. It is not a Sejda/iLovePDF clone yet.
- The Python merge is a small adapter proof of concept. Gotenberg integration is a planned next step, not secretly installed.
- Multipart upload parsing may temporarily spool to local disk. Uploaded PDFs aren't intentionally stored long-term by this app.
- Raw HTTP bodies are now bounded to 41 MiB before multipart parsing, including chunked requests. Uploads time out after 30 seconds. The extra 1 MiB is for multipart overhead; PDF payloads still have a 40 MiB aggregate cap. Temporary ingress buffers close on success, rejection and disconnect.
- No persistent user accounts, database, background job queue, audit logs, PDF parsing sandbox, rate limits or strict reverse-proxy request-body enforcement.
- Do **not** expose this to general public untrusted PDFs until worker isolation, input sanitation, security testing and abuse controls are implemented.
- A new Python environment must run CI to verify the exact pinned versions; the initial local tests used preinstalled versions.

