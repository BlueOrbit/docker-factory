# Workflow Improvements Walkthrough

I have updated the `build-and-publish.yml` workflow to implement PR validation and incremental tag builds.

## Changes

### PR Validation
- **Trigger**: Added `pull_request` trigger restricted to `images/**` changes.
- **Push Logic**: The `build-and-push` step now conditionally pushes images. It only pushes if the event is NOT a `pull_request`. This ensures PRs run the build to verify correctness without polluting the registry.

### Incremental Tag Builds
- **Logic Update**: When a tag is pushed, the workflow now detects changes relative to the *previous tag* instead of building everything.
- **Command**: Uses `git describe --tags --abbrev=0 HEAD^` to find the previous tag.
- **Diffing**: Calculates changed files between the previous tag and the current SHA.

## Code Changes

```yaml
render_diffs(file:///Users/lanjiachen/Developer/BlueOrbit/docker-factory/.github/workflows/build-and-publish.yml)
```

## Verification Results
- **Automated Tests**: I verified the syntax of the YAML changes.
- **Manual Verification**: Since I cannot run GitHub Actions locally, the user should:
    1.  Open a PR changing a file in `images/` and verify the action runs but does not push.
    2.  Push a new tag and verify it only builds images changed since the last tag.
