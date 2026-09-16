# Contributing Guidelines

We welcome contributions to the **Real-Time Corrective RAG Intelligence Platform**.

## How to Contribute
- **Fork the repository** and create a feature branch.
- **Follow the coding style** defined in `requirements-dev.txt` (e.g., `black`, `flake8`).
- **Write tests** for any new functionality and ensure existing tests pass.
- **Update documentation** when you add or modify features.
- **Submit a Pull Request** with a clear description of your changes.

## Branch Strategy
- `main` – stable baseline.
- `dev` – integration branch for upcoming releases.
- Feature branches: `feature/<short-description>`.

## Commit Message Convention
```
<type>(<scope>): <subject>

<body>

<footer>
```
- `type`: `feat`, `fix`, `docs`, `test`, `chore`.
- `scope`: optional component name.
- Follow the **Conventional Commits** specification.

## Code Review
- At least one reviewer must approve before merging.
- All CI checks must pass.

## Release Process
- When `dev` is deemed stable, a maintainer creates a release branch, bumps the version in `CHANGELOG.md`, and merges to `main`.

## License
This project is licensed under the Apache 2.0 License – see `LICENSE`.
