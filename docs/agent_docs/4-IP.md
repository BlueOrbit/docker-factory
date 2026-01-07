# GitHub Actions Workflow Improvements

## Goal Description
Configure `build-and-publish.yml` to run validation builds on PRs (without pushing) and enable incremental builds for tagged releases by only building images changed since the last tag.

## User Review Required
> [!IMPORTANT]
> The incremental tag build logic relies on `git describe --tags --abbrev=0 HEAD^` to find the previous tag. If this is the very first tag in the repo, this command might fail or return nothing. The current plan assumes a history of tags exists or that the user processes the first tag differently (likely by building all).

## Proposed Changes

### Workflow Configuration
#### [MODIFY] [build-and-publish.yml](file:///Users/lanjiachen/Developer/BlueOrbit/docker-factory/.github/workflows/build-and-publish.yml)
- Update `on` triggers to include `pull_request` for `images/**`.
- Update `push` parameter in `docker/build-push-action` to be dynamic: `${{ github.event_name != 'pull_request' }}`.
- refactor `detect-changes` job:
    - In the `tag` block:
        - Identify previous tag: `git describe --tags --abbrev=0 HEAD^`
        - Calculate changed files between `PREV_TAG` and `CURRENT_TAG`.
        - Pass those changes to `generate_matrix.py --changes` instead of `--all`.

## Verification Plan
### Automated Tests
- I cannot run GitHub Actions locally.
- Review the yml syntax.
- Verify the shell commands for git describe locally if possible (though repo state might differ).
