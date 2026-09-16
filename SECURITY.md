# Security Guidelines

## Secrets Management
- Keep all secrets (API keys, tokens, passwords) out of the repository. Store them in a `.env` file that is listed in `.gitignore`.
- Use environment variables for runtime configuration.

## Dependency Security
- Regularly run `pip list --outdated` and `pip-audit` to identify vulnerable packages.
- Pin exact versions in `requirements.txt` and `requirements-dev.txt`.

## Input Validation & Prompt Injection
- Sanitize user‑provided data before feeding it to LLM prompts.
- Use a whitelist of allowed characters for identifiers.

## Data Handling
- Do not store raw proprietary documents in the vector store without encryption.
- Log only metadata (hashes, IDs) to avoid leaking content.

## Deployment
- Run services with least‑privilege system accounts.
- Apply network‑level restrictions (firewalls, VPN) for any external services.

## Auditing
- Enable audit logs for all access to the vector store and LLM endpoints.
- Retain logs for at least 30 days.

## Responsible AI
- Perform regular bias and toxicity checks on generated outputs.
- Provide a mechanism for users to flag problematic responses.
