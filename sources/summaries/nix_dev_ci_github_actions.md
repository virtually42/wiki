---
id: summary-nix-dev-ci-github-actions
title: nix.dev — Continuous Integration with GitHub Actions (Cachix recipe)
kind: descriptive
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: high
tags_extended: [supply-chain, signing, reproducibility]
sources:
  - sources/raw/docs/nix_dev_ci_github_actions.md
  - https://nix.dev/guides/recipes/continuous-integration-github-actions
provenance:
  upstream_author: nix.dev maintainers (NixOS community documentation)
  upstream_url: https://nix.dev/guides/recipes/continuous-integration-github-actions
  upstream_kind: community-documentation
  introduced_to_wiki_by: user
  confirmed_at: 2026-05-29
tags: [nix, ci, github-actions, cachix, binary-cache, infra, recipe]
---

## Source

A short recipe page on nix.dev describing how to run Nix on GitHub
Actions with Cachix as a binary cache. The recipe is non-flake — it
pins `nixpkgs` to the rolling `nixos-unstable` channel via the
`install-nix-action`'s `nix_path` input and uses the legacy CLI
(`nix-build`, `nix-shell --run`). See raw extraction at
[[sources/raw/docs/nix_dev_ci_github_actions.md]].

The recipe is structured as three setup phases (create cache → wire
secrets → add workflow file) plus a single example
`.github/workflows/test.yml` exhibiting the canonical step sequence:
`checkout → install-nix → cachix-action → nix-build → nix-shell`.

## What this source teaches

### The shape of "Nix + GHA + Cachix"

- Three actions compose the pipeline:
  - `actions/checkout@v4` (observed 2026-05-29)
  - `cachix/install-nix-action@v25` — installs Nix and configures
    `nix_path`
  - `cachix/cachix-action@v14` — wires the binary cache; uses
    `signingKey` (cache write) and / or `authToken` (cachix auth)
- Builds run with `nix-build`; dev shell is smoke-tested via
  `nix-shell --run "echo OK"`.
- Triggers on both `pull_request` and `push` (no branch filter).
- Cache identity is a per-team cachix.org cache; the recipe advises
  a separate cache per team based on access-control needs.

### Why Cachix

The recipe's value proposition is "build derivations once, share them
everywhere." Without a cache, every CI run rebuilds derivations from
source; with Cachix, the GHA runner pulls cached outputs and only
builds new derivations, which it then pushes back to the cache.
Developers configured to read the same cache pick up CI's builds
automatically.

## What this source does *not* teach

- **Flakes.** The recipe is pre-flake. No `nix build .#x`,
  `nix develop`, `nix flake check`, or `flake.lock` discipline.
  Flake users need a different shape (still `install-nix-action`,
  still `cachix-action`, but `nix-path` becomes irrelevant and the
  build commands change).
- **Alternative caching strategies.** The recipe assumes Cachix.
  It does not mention `nix-community/cache-nix-action`,
  Magic Nix Cache, self-hosted `nix-serve` / Attic, or
  S3-backed binary caches.
- **Substituter / signing-key configuration outside CI.** The recipe
  shows the CI side but not how developers configure
  `nix.conf` / `~/.config/nix/nix.conf` to read from the cache.
- **Matrix builds, cross-platform runners, or self-hosted runners.**
  Single-job, single-runner shape only.
- **Action-version drift policy.** The pinned `@v25` / `@v14` / `@v4`
  numbers will go stale; the recipe gives no guidance on upgrades.
- **What to do when the cache misses or the auth fails.** No
  troubleshooting section.

## Security framing (the angle the recipe undersells)

The upstream recipe sells Cachix as a speed-up: "never build a
derivation twice." That framing undersells what is actually a
supply-chain control point. A more honest framing:

### Cache + CI as a chain-of-custody

| Layer | What it gives you | What enforces it |
|-------|-------------------|------------------|
| Content addressing | "What I deploy is bit-for-bit what CI built" | Nix store path hashes |
| Signed cache entries | "Only CI can publish artifacts" | `CACHIX_SIGNING_KEY` held only in GHA secrets |
| Trusted-keys on consumers | "Hosts refuse unsigned / wrong-signer artifacts" | `trusted-public-keys` in `nix.conf` on the consumer |
| Pinned closure | "Runtime libs identical to test-time libs" | Nix closure = derivation + all transitive runtime deps, every input hashed |
| No build toolchain in prod | "Smaller attack surface; nothing to compromise" | Deploy hosts pull outputs, never source |
| Per-input hashes | "Provable bill of materials" | `nix-store --query --requisites` / `--graph` |

The signing-key model is the load-bearing piece. Without it the cache
is a CDN — fast but not authenticated. With it, the cache is the
boundary between "trusted artifact" and "anything else."

### What the recipe gets right (security-wise)

- Putting `CACHIX_SIGNING_KEY` in GitHub Secrets, not in the repo —
  the key never leaves CI.
- Both `signingKey` and `authToken` wired — separation of "write to
  cache" capability from "read with auth" capability.

### Where the recipe leaves a gap

- **Consumer-side verification is not shown.** A deploy host that
  doesn't configure `substituters` + `trusted-public-keys` will
  either (a) not use the cache at all, or (b) trust unsigned
  artifacts. Either way, the signing model collapses. This step
  belongs in a sibling deployment recipe that does not exist on
  nix.dev at the same prominence.
- **Channel pinning (`nixos-unstable`) is a weak reproducibility
  claim.** Two builds an hour apart can resolve different
  `nixpkgs`. For a security narrative ("we deployed exactly what
  we tested") you want a `flake.lock` or a pinned commit, not a
  rolling channel.
- **No `nix-build --check` or content-addressed derivations.** The
  recipe doesn't verify that builds are bit-reproducible, only that
  they're cached.
- **No artifact attestation** (SLSA, in-toto, Sigstore). The Cachix
  signature is the only attestation, and it's a "this came from a
  key I trust", not "this came from this specific commit built
  under these specific inputs."

### What this means for our wiki

Any future `tech/guides/nix-ci-github-actions.md` (or, more
likely, a `tech/guides/nix-secure-deployment.md`) should treat the
recipe as **the build-and-push half of a two-half story** and pair
it with downstream consumer configuration. The single-recipe
"Cachix gets you fast CI" framing is incomplete for any project
that takes deployment integrity seriously — which the planned
`infra` project, by virtue of being infrastructure, will.

## Relationship to current wiki state

The wiki has **no existing Nix topic area**:

- No `tech/guides/nix-*.md`
- No `tech/stack/nix.md`
- No `tech/patterns/` entries for derivation caching, binary caches,
  or substituters
- No project currently uses Nix-based CI on disk; the `infra` project
  in [[index]] is `planned` (NixOS-shaped) but has no on-disk presence

Closest neighbours in spirit:

- [[tech/guides/mill-cross-platform]] — also a CI-adjacent build-tool
  guide, but Mill/Scala, not Nix.
- The planned `infra` project — the natural consumer of any future
  Nix CI guide.

Because the wiki has no Nix presence at all, this source establishes
a single anchor point for future Nix-related work rather than slotting
into an existing topology.

## Promotion candidacy

| Candidate page | Status | Reasoning |
|----------------|--------|-----------|
| `tech/guides/nix-ci-github-actions.md` (descriptive how-to) | **deferred** | A descriptive guide is admissible from one source, but the wiki has no broader Nix context yet. A guide written now would be a thin wrapper around the upstream recipe with little wiki-specific value. Wait until a project (currently most likely the `infra` project, once it activates) needs Nix CI and provides a concrete usage anchor. |
| `tech/stack/nix.md` (technology page) | **deferred** | Premature without a project using Nix. |
| `tech/patterns/binary-cache-for-ci.md` (pattern) | **deferred** | Single-source; would require either a second corroborating source (e.g. a flake-native CI recipe) or in-project evidence before promotion. |
| `tech/decisions/*.md` (decision) | **not a candidate** | Decisions encode obligations on projects; nothing here rises to organisational decision until we adopt Nix CI for real. |

The page is therefore **accepted as a reference summary** without an
immediate promotion. When the first wiki project wires up Nix CI,
revisit and consider authoring `tech/guides/nix-ci-github-actions.md`
that points at this summary plus the in-project usage.

## Open questions left for the next ingest / project anchor

1. **Flake vs non-flake** — if `infra` (or any project) adopts Nix
   CI, will it use flakes? If so, this source covers only half the
   shape; a flake-native recipe (or a `tech/guides/` page) would
   need to be authored fresh.
2. **Cache identity** — per-project, per-team, or wiki-wide cache?
   The upstream recipe defers to "team access-control needs."
3. **Substitute consumer wiring (load-bearing for security).** How
   do deploy hosts and developers configure `substituters` +
   `trusted-public-keys` to actually verify cache signatures? Not
   covered here. Without this, the signing model is decorative —
   see §Security framing. A second source (or a
   `tech/guides/nix-secure-deployment.md` authored against a real
   project) is needed to close this loop.
4. **Reproducibility verification.** Does any future project want
   to enforce bit-reproducible builds (`nix-build --check`,
   content-addressed derivations, `flake.lock` instead of channel
   pins)? The recipe is silent; if our security framing is to
   hold, this needs an answer.
5. **Artifact attestation.** SLSA / in-toto / Sigstore over the
   Cachix signature — overkill, complementary, or redundant? Open
   until a project demands it.
6. **Version-pin maintenance** — when `cachix-action@v15`,
   `install-nix-action@v26` etc. ship, what triggers the wiki to
   refresh derived pages? Tie to ingest-external refresh cadence if
   a guide is authored.

## Links

- [[sources/raw/docs/nix_dev_ci_github_actions.md]] — raw extraction
- [[index]] §Projects — `infra` (planned) is the likely consumer
- [[tech/guides/mill-cross-platform]] — neighbouring CI-shaped guide
  (different toolchain)
