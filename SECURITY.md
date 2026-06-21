# Security Policy

## Supported Versions
This repository is a private research prototype. Only the latest commit on the `main` branch receives best-effort maintenance.

| Version | Supported |
|---------|-----------|
| 0.x (main) | ✅ |

## Reporting a Vulnerability
Please report security issues privately:
1. Open a GitHub Issue with the `security` label, **or**
2. Contact the maintainer directly via GitHub: @ShorxNetwork

We do not operate a bug bounty program. As this is a zero-cost research environment, there is no SLA, but critical issues will be reviewed promptly.

Please do not run automated vulnerability scanners against this repository – GitHub Advanced Security is intentionally disabled to avoid charges.

---

### Repository Status Review: New_Agent_Variant_Against_Chaos

| Category | Status | Current Value / Configuration |
| :--- | :--- | :--- |
| **Primary Language** | ✅ Optimized | Python 99.2% / Dockerfile 0.8% |
| **Repository Structure** | ✅ Correct | `.dockerignore` located in `task-c/prototype/` |
| **CI/CD – Docker Build** | ✅ On-Demand | Triggers only on `git tag v*` (no cost on push) |
| **CI/CD – Formatter** | ✅ Passive | Black runs on push, commits only if needed |
| **Code Quality** | ✅ Production-Ready | Black-formatted, typed, 321 lines, modular |
| **Security Features** | ✅ Disabled | Advanced Security off – zero charges |
| **Contributors / Bot Noise** | ✅ Clean | 1 contributor (owner only) |
| **Next Action** | Ready | Tag `v0.1` to validate Docker build |

**Detailed Validation:**

1. **Structure:** The misplaced `.dockerignore` has been removed from `.github/workflows/` and correctly placed alongside the `Dockerfile`. This ensures the Docker build context is clean and excludes `.git`, `.github`, and cache files.

2. **CI/CD Governance:** The `docker-build.yml` workflow is now cost-controlled and will not execute on routine commits. The repository will remain silent until you intentionally create a release tag.

3. **Code – `agent_pipeline.py`:** The implementation meets professional standards with:
   - Structured logging via JSON for observability
   - Deterministic orchestrator with circuit-breaker pattern (halts on `TaskResult.status == "failure"`)
   - Integrated fault injection for chaos testing
   - Full type hints and dataclass-based context management

4. **Cost Control:** All optional GitHub services that incur charges remain disabled, aligning with your requirement for a zero-cost research environment.

**Conclusion:** The repository is now fully optimized, clean, and ready for the next development phase.
