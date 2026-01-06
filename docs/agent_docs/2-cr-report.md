# Code Review Report

**Date:** 2026-01-06
**Scope:** Review of `docker-factory` repository against `plan.md`.

## 1. Executive Summary

The repository structure and core logic generally align well with the `plan.md`. The Monorepo structure, image isolation, and custom dependency-based build matrix generation (`generate_matrix.py`) are implemented correctly.

However, there are specific **functional gaps** regarding CI/CD triggers and tagging strategies, as well as some **best practice improvements** needed for production readiness.

## 2. Plan Compliance Analysis

| Feature | Plan Requirement | Implementation Status | Notes |
| :--- | :--- | :--- | :--- |
| **Monorepo Structure** | `images/<name>`, `image.yml` | ✅ Implemented | Correctly structured. |
| **Dependency Graph** | `depends_on` in `image.yml` triggers rebuilds | ✅ Implemented | `scripts/generate_matrix.py` correctly calculates affected images. |
| **Multi-Arch** | `linux/amd64`, `linux/arm64` | ✅ Implemented | `docker/build-push-action` configured with platforms. |
| **Registry** | GHCR (`ghcr.io`) | ✅ Implemented | Workflow logs in to GHCR. |
| **CI - Main Push** | Build changed images | ✅ Implemented | Path filtering and matrix generation work. |
| **CI - Tag Push** | Build ALL images | ✅ Implemented | `generate_matrix.py --all` is called on tags. |
| **Tagging Strategy** | `sha-<sha>`, `main`, `latest` | ✅ Implemented | - |
| **Semantic Versioning** | `v1.2.3` -> `v1.2`, `v1` | ❌ **Missing** | Current config only pushes the exact Git tag ref. |
| **PR Workflow** | Build only (no push), no secrets | ❌ **Missing** | `on: pull_request` is completely missing from the workflow. |
| **Hard Rules** | `pre-build.sh` + `requires` checks | ✅ Implemented | `scripts/lint_rules.py` enforces this. |

## 3. Detailed Findings

### 3.1. Critical Functional Gaps

#### [MISSING] PR Integration
The `plan.md` (Section 6.5) specifies that PRs should trigger a build check (without pushing). The current `.github/workflows/build-and-publish.yml` **does not have a `pull_request` trigger**.
*   **Impact**: Code changes are not verified until they are merged to `main`, leading to potential broken builds on the main branch.

#### [MISSING] Semantic Versioning Tags
The plan (Section 5.2) requires pushing `:v1.2.3`, `:v1.2`, and `:v1` tags.
The current configuration uses `type=ref,event=tag`, which only produces the exact tag (e.g., `v1.2.3`).
*   **Fix**: Update `docker/metadata-action` config to use `type=semver` patterns.

### 3.2. Code Quality & Best Practices

#### [Dockerfile] Use of `latest` Tags
Both `images/biomini/Dockerfile` and `images/spreadsheet/Dockerfile` use `FROM alpine:latest`.
*   **Risk**: Builds are not reproducible over time. If Alpine updates, the base image changes unpredictably.
*   **Recommendation**: Pin to specific versions (e.g., `alpine:3.19`).

#### [CI] Unpinned Python Dependencies
The workflow step `Install dependencies` runs:
```bash
pip install pyyaml
```
*   **Risk**: Breaking changes in `pyyaml` (though unlikely) could break the CI pipeline.
*   **Recommendation**: Pin version, e.g., `pip install pyyaml==6.0.1`.

#### [Security] Root User
Dockerfiles do not switch to a non-root user.
*   **Recommendation**: Add a `USER` instruction for better runtime security, unless root is explicitly required.

### 3.3. Logic & Architecture

#### `spreadsheet` Dependency Coupling
`spreadsheet` declares a dependency on `biomini` in `image.yml`, which correctly triggers a rebuild of `spreadsheet` if `biomini` changes.
*   **Observation**: `images/spreadsheet/Dockerfile` uses `FROM alpine:latest` and does not seemingly consume `biomini`.
*   **Assessment**: This is acceptable if the dependency implies a logical "service-level" dependency or if `spreadsheet` is expected to *eventually* use `biomini` as a base. If it stays independent, the dependency strictly serves to coordinate release versions, which is a valid use case in this "Factory" model.

## 4. Recommendations

1.  **Immediate Fixes**:
    *   Add `pull_request` trigger to `.github/workflows/build-and-publish.yml` with `push: false`.
    *   Update `docker/metadata-action` to generate SemVer tags.
2.  **Refactoring**:
    *   Pin versions in Dockerfiles and CI scripts.

## 5. Conclusion
The repository implements the core "Factory" logic successfully, particularly the dynamic matrix generation. Addressing the missing PR triggers and tagging logic will bring it to full parity with the design plan.
