# Isolated development deployment

```sh
docker compose up --build --detach --wait
# Open http://127.0.0.1:8000
docker compose logs -f
docker compose down
```

The API listens only on host loopback. It forwards document bytes to the `worker` service using `PDFSTUDIO_WORKER_URL=http://worker:8001`. The worker has no published port and joins only an `internal: true` Docker network. It has no host filesystem mounts, no application credentials, no writable root filesystem, all capabilities dropped, no-new-privileges, and bounded temporary memory storage. CPU, RAM and process limits apply at container and child-process levels.

The API cannot silently revert to local PDF processing when its configured worker is offline. The private HTTP transport disables environment proxies and redirects. Each service accepts at most two active HTTP uploads, failing excess requests with 503/Retry-After before reading their bodies. Workers keep the 25-second execution deadline and Linux 20-second CPU/768-MiB child memory ceiling. The worker container has a 2-GiB ceiling across children and service; the API has 1 GiB.

## Verify boundaries and user flow

```sh
docker compose exec -T worker python - < scripts/isolation_smoke.py
python -m pip install -e '.[dev,browser]'
python -m playwright install chromium
python scripts/browser_smoke.py
```

CI also validates Compose's internal network setting, the worker's network membership, absence of published worker ports, and read-only configuration. Browser tests reopen downloaded synthetic PDFs, check order and page-number text, and retain a trace for failures.

## Trust boundaries and remaining release decisions

The worker can reach the API across their private network. Both containers still share the host kernel. A container boundary is not proof against every parser/kernel vulnerability. Do not mount secrets, the Docker socket, or customer directories into the worker. The worker endpoint intentionally has no public authentication and must remain private; never expose it directly or configure it to process arbitrary remote URLs.

This configuration is a reproducible local/staging baseline, not a public-launch approval. Before internet exposure, configure TLS at a trusted reverse proxy, authentication/per-user quotas, request and idle timeouts, container patching/scanning, monitoring, tested retention policy, and incident handling. Confirm original-code license and contribution terms, and complete browser/accessibility/PDF fidelity reviews. There is no persistent document store: uploaded spools and child-process memory are transient, but user downloads remain on their devices.
