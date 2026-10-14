# Releasing Gridfees AUT

The GitHub repository must be public for HACS. Distribution uses GitHub releases
and the standard `custom_components/gridfees_aut` directory. No separate ZIP
asset is required. HACS installs only the integration directory, including
`tariffs.json`, translations, and the brand image.

## Prepare a version

1. Update the version in `custom_components/gridfees_aut/manifest.json`.
2. Update the README status and add release notes under `docs/releases/`.
3. Push the changes and wait for Calculation tests, hassfest, and HACS validation
   to succeed for the release commit.
4. Confirm the integration loads in Home Assistant and verify any changed setup,
   calculations, forecasts, or migration behavior.

## Publish

Create a GitHub release with a tag matching the manifest version, prefixed with
`v` (for example `v0.5.2`). Target the verified commit and use the prepared notes.
Publish a stable release for normal HACS updates; drafts are preparation only.
Never move an existing release tag to a different commit. Use a new version for
any later fix.

HACS uses the latest published release as its version. Tags alone and draft
releases do not provide a stable update. The default branch is hidden in HACS
to keep installations on released versions.

## First HACS installation check

Add the public repository under HACS custom repositories as type Integration.
Download the release, restart Home Assistant, and verify the version and the
existing tariff profiles. Confirm that Total grid fees and SNAP active retain
their entity IDs. For a fresh installation, use Add integration after restart.

References: [HACS requirements](https://hacs.xyz/docs/publish/start/),
[Integration packaging](https://hacs.xyz/docs/publish/integration/), and
[Custom repositories](https://hacs.xyz/docs/faq/custom_repositories/).
