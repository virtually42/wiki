# nix.dev — Continuous Integration with GitHub Actions

**Source URL:** https://nix.dev/guides/recipes/continuous-integration-github-actions
**Fetched:** 2026-05-29
**Upstream site:** nix.dev (NixOS community documentation)
**Kind:** prescriptive recipe / how-to

This file is a factual extraction of the published recipe — section
structure, version pins, the documented workflow example, secrets,
and outbound links — at the time of fetching. It is not a verbatim
reproduction of the upstream prose.

---

## Section structure (H2 / H3 in order)

1. Continuous integration with GitHub Actions
2. Caching builds using Cachix
   1. Creating your first binary cache
   2. Setting up secrets
   3. Setting up GitHub Actions
3. Next steps

## Core thesis

Run Nix on GitHub Actions and pair it with Cachix as a binary cache,
so developer environments (and any derivations) are built once and
shared across CI runs and developer machines instead of being rebuilt
per branch / per developer.

## Action version pins (observed on upstream 2026-05-29)

| Action | Version pin |
|--------|-------------|
| `actions/checkout` | `v4` |
| `cachix/install-nix-action` | `v25` |
| `cachix/cachix-action` | `v14` |

These pins drift; treat them as observed-on-date references rather
than authoritative current values.

## Documented workflow example

The recipe publishes a `.github/workflows/test.yml` with this shape:

```yaml
name: "Test"
on:
  pull_request:
  push:
jobs:
  tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: cachix/install-nix-action@v25
      with:
        nix_path: nixpkgs=channel:nixos-unstable
    - uses: cachix/cachix-action@v14
      with:
        name: mycache
        signingKey: '${{ secrets.CACHIX_SIGNING_KEY }}'
        authToken: '${{ secrets.CACHIX_AUTH_TOKEN }}'
    - run: nix-build
    - run: nix-shell --run "echo OK"
```

Shape decisions encoded in the example:

- Triggers on both `pull_request` and `push`.
- Runs on `ubuntu-latest`.
- Pins nixpkgs to the rolling `nixos-unstable` channel via
  `nix_path`, not via a flake input — this is a non-flake recipe.
- Uses the legacy CLI (`nix-build`, `nix-shell --run`), not
  `nix build` / `nix develop`.
- Cache identity (`name: mycache`) is a placeholder for the
  per-team cache name created at cachix.org.
- Both `signingKey` and `authToken` are wired; either or both can
  be present depending on cache configuration.

## Required secrets

| Secret | Purpose |
|--------|---------|
| `CACHIX_SIGNING_KEY` | Write access to push builds to the cache |
| `CACHIX_AUTH_TOKEN` | Auth for cachix-action; complements or replaces signing-key depending on cache config |

## Setup phases described in upstream

- **Create a binary cache** — at cachix.org; the recipe advises a
  separate cache per team based on access-control needs.
- **Configure repository secrets** — add the signing key and / or
  auth token to GitHub repo settings under Secrets.
- **Add the workflow file** — `.github/workflows/test.yml` with the
  example above.

## Outbound links

- https://github.com/features/actions — GitHub Actions landing
- https://cachix.org/ — Cachix service
- https://app.cachix.org/cache — Cachix cache creation UI
- https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions — GitHub Actions workflow syntax reference
- https://github.com/nix-dot-dev/getting-started-nix-template — quickstart template repository
