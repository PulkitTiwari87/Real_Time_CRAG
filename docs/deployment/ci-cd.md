# CI/CD

## Status

This describes what is actually implemented and running via GitHub Actions
today. Anything not listed here as implemented is not wired up, whatever
the architecture docs describe as a future target.

## Pipeline

```mermaid
flowchart TD
    Dev[Developer] -->|git push / PR| GH[GitHub]
    GH --> CI

    subgraph CI[CI workflow -- pull_request + push to main]
        L[lint-and-test\nflake8 + pytest]
        D[docker-validate\ncompose config + docker build]
        S[security\npip-audit]
    end

    CI -->|workflow_run, only if CI succeeded on a push to main| CD

    subgraph CD[CD workflow]
        B[build-and-push\nGHCR image, tagged by commit SHA + latest]
        T[smoke-test\nrun image, poll GET /health]
        B --> T
    end

    T -->|operator pulls the image by SHA| Ext[External runtime\n(not managed by this repo)]
```

## What's implemented vs. what isn't

**Implemented and running in GitHub Actions:**
- Lint (`flake8`) and the full `pytest` suite on every pull request and
  every push to `main`.
- `docker compose config` validation for `docker-compose.yml` and
  `infrastructure/docker-compose.kafka.yml`.
- A real `docker build` of the backend image on every CI run (build-only,
  not pushed) so a broken Dockerfile fails CI before merge.
- `pip-audit` against `requirements.txt`.
- On a successful CI run on `main`: build the backend image and push it to
  GitHub Container Registry (GHCR), tagged with the commit SHA and
  `latest`.
- A smoke test that runs the freshly published image in the Actions runner
  and polls `GET /health` until it returns `200`.

**Deliberately not implemented, and why:**
- **No workflow deploys to a persistent, publicly reachable server.**
  GitHub Actions runners are ephemeral; nothing in this repository
  currently names an external host (no Fly.io/Render/etc. account or
  secrets configured). The CD workflow's "deployment" is publishing an
  immutable image to GHCR and proving it boots and answers `/health` --
  running it as a long-lived service is the operator's responsibility (see
  *Running the published image* below).
- **No GitHub Pages workflow for the frontend.** `frontend/index.html`
  calls the API via `window.location.origin` (same-origin fetches) and the
  FastAPI backend has no CORS middleware configured. Deploying the static
  file to Pages (a different origin from wherever the backend runs) would
  break both endpoints without first adding CORS and a configurable API
  base URL to the frontend -- out of scope for a CI/CD change. If the
  frontend gains that configurability later, Pages becomes viable.
- **No Kafka in CD.** `src/streaming/` is unit-tested against connection
  failures but has never been exercised against a live broker in this
  project. `infrastructure/docker-compose.kafka.yml` is validated for
  syntax in CI, nothing more.
- **No CodeQL/SAST workflow.** GitHub's secret scanning and Dependabot are
  free, native, zero-workflow repository settings -- turn them on under
  **Settings -> Code security** rather than adding another Actions job.

## GitHub Secrets and Variables

**Secrets required today: none beyond the built-in `GITHUB_TOKEN`.**
The GHCR push uses `GITHUB_TOKEN` (auto-provided, scoped to this repo, no
PAT needed). The smoke test only hits `/health`, which never calls an LLM
provider, so no `GEMINI_API_KEY` or similar is needed in CI.

If an external deployment target is added later, that host would need
(not this repo's Actions secrets, but the host's own config):

| Name | Kind | Used by |
|---|---|---|
| `GEMINI_API_KEY` | Secret | `src/rag_baseline/llm_providers/gemini_provider.py` |
| `GEMINI_MODEL` | Variable | same (optional, has a default) |
| `LLM_PROVIDER` | Variable | provider selection (`gemini` / `ollama`) |
| `LLM_MODEL` | Variable | provider selection |
| `OLLAMA_HOST` | Variable | `ollama_provider.py`, if using local Ollama |
| `EMBEDDING_MODEL` | Variable | `src/embeddings/embedding_service.py` (optional, has a default) |

`.env.example` also lists `HF_TOKEN`, `VECTOR_DB_URL`, `VECTOR_DB_COLLECTION`,
`DATABASE_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`,
`SUPABASE_PUBLISHABLE_KEY`, and `KAFKA_BOOTSTRAP_SERVERS` -- none of these
are currently read anywhere in `src/`. They're placeholders for
not-yet-implemented phases; don't provision them.

## Image tags and rollback

Every image is pushed as `ghcr.io/<owner>/<repo>:<commit-sha>` and also
tagged `:latest`. `latest` is a convenience pointer only -- deploy and
roll back by SHA:

```bash
# Roll back to a known-good commit's image:
docker pull ghcr.io/pulkittiwari87/real_time_crag:<previous-good-sha>
docker stop <running-container> && docker rm <running-container>
docker run -d -p 8000:8000 --env-file .env \
  -v vector_store_data:/app/local_vector_store \
  ghcr.io/pulkittiwari87/real_time_crag:<previous-good-sha>
```

Find `<previous-good-sha>` from the commit history on `main` or from the
CD workflow run history in the Actions tab.

## Running the published image

The image expects a persistent volume mounted at `/app/local_vector_store`
(embedded Qdrant storage -- losing this volume loses the index). Point it
at whatever real values the deployment needs from the table above via
`--env-file` or `-e`. It listens on port 8000 and exposes `GET /health`
and `GET /metrics` (Prometheus format).

## Local verification

Everything CI checks can be run locally first:

```bash
pip install -r requirements.txt -r requirements-dev.txt
flake8 src tests scripts
pytest -q
cp .env.example .env && docker compose config
docker build -t rag-api .
```
