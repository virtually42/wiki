---
id: summary-github-actions-nix-cachix-dhall-gvolpe
title: GitHub Actions powered by Nix Shell & Cachix (Volpe 2020)
kind: descriptive
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: medium
sources:
  - sources/tmp/github_actions_nix_cachix_dhall_gvolpe.md
  - https://gvolpe.com/blog/github-actions-nix-cachix-dhall/
provenance:
  upstream_author: Gabriel Volpe (gvolpe)
  upstream_url: https://gvolpe.com/blog/github-actions-nix-cachix-dhall/
  upstream_kind: personal-blog
  upstream_published: 2020-06-02
  introduced_to_wiki_by: user
  confirmed_at: 2026-05-29
tags: [nix, nix-shell, cachix, github-actions, dhall, ci, supply-chain, reproducible-builds, scala, sbt, haskell, ruby]
---

## Source

`sources/tmp/github_actions_nix_cachix_dhall_gvolpe.md` is a 2020 blog
post by Gabriel Volpe presenting a three-part recipe for CI on GitHub
Actions:

1. **`shell.nix`** with a pinned `nixpkgs` tarball as the single
   declaration of the build environment, used identically locally
   and in CI.
2. **Dhall** as a typed alternative to hand-written workflow YAML,
   compiled with `dhall-to-yaml` before commit. Built on
   `regadas/github-actions-dhall` (Volpe maintains a fork with cachix
   steps added).
3. **Cachix** as a binary cache for Nix derivations, populated by a
   `nix-shell` → `nix-store -qR --include-outputs` push pattern that
   the article notes is "currently an under-documented feature."

The article carries three worked examples: a Jekyll blog (Ruby), a
Haskell shopping-cart, and the Redis4Cats Scala microsite publish
pipeline. Only the microsite uses sbt — and Nix is the *driver*, not
the build tool (sbt is reached via `nix-shell --run "sbt publishSite"`).

## Core thesis (verbatim where relevant)

> "We use the same `shell.nix` we use for local development to build
> our software in the CI pipeline. […] No more duplicate ways of
> building packages! This way, we guarantee that whatever works
> locally, also works on our CI."

This is the load-bearing claim. Everything else (Cachix, Dhall) is
performance and ergonomics. The reproducibility argument lives in
*one* `shell.nix` per repo, pinned to a specific nixpkgs tarball SHA.

## What the article actually advocates

| Claim | Mechanism | Strength of evidence in article |
|-------|-----------|---------------------------------|
| Same dependencies locally and in CI | `shell.nix` consumed by `nix-shell --run …` in both contexts | Strong — direct demonstration on three repos |
| Pinned nixpkgs prevents drift | `fetchTarball` with explicit `sha256` | Strong — standard Nix practice |
| Typed workflows beat raw YAML | Dhall → `dhall-to-yaml` | Author preference; "I really dislike YAML files" + link to noyaml.com. Personal taste, not evidence. |
| Cachix speeds CI builds | binary cache as a service | Author explicitly hedges: "for a CI build job I could probably get away without using Cachix and it'll still be the same. However, as soon as the Nix dependencies of your project start to grow, you may notice a difference." |
| Semantic integrity for workflow imports | Dhall's content-addressed imports with hash pinning | Real feature — Dhall imports include `sha256:…` and refuse to load on mismatch. Comparable to Nix's own integrity check; both are content-addressed. |

## Mapping to *our* current question (Maven Central + supply chain)

The user's ongoing conversation is about Mill libraries published to
Maven Central under `no.virtual-architect`, signed with a YubiKey,
with the build environment hardened against supply-chain attacks. The
article addresses only the **build-environment** half of that, not
the **signing** half. Specifically:

### Useful overlaps

- `shell.nix` with pinned nixpkgs is exactly the wrapper we'd put
  around Mill (`nix develop` → `mill __.compile`) to harden the CI
  build environment against a compromised toolchain. This is the
  "Phase 1" recommendation in the conversation.
- The single-`shell.nix` discipline (one declaration for local + CI)
  matches what would be needed if a future verifier rebuilds locally
  and compares hashes against CI output.
- `nix-shell` (or `nix develop`) inside a hosted GitHub runner is
  the cheapest answer to "I don't trust the runner's preinstalled
  toolchain" — the article validates this pattern.

### Useful **non-overlaps** (where the article is silent)

- **No GPG / artifact signing.** The Scala example uses `GITHUB_TOKEN`
  to publish a *microsite* to GitHub Pages, not signed artifacts to
  Maven Central. The signing question (key in CI vs YubiKey local vs
  hybrid) is untouched.
- **No reproducibility verification.** Volpe uses Nix to *produce*
  reproducible environments but never proposes "rebuild locally and
  compare CI's output" as a supply-chain control. The article is
  fine with trusting CI as long as CI's environment is pinned.
- **No flakes.** The article predates flakes being mainstream. It
  uses `fetchTarball` with a pinned URL and SHA, not
  `flake.nix` + `flake.lock`. For our 2026 stack the equivalent
  pattern is `nix develop` against a flake, with `flake.lock`
  doing the pinning that `sha256` does here.
- **No self-hosted runner discussion.** The article assumes hosted
  GitHub runners throughout. For our supply-chain thread, this is
  consistent with the Phase 1 recommendation (GitHub-hosted runner +
  Nix-wrapped build).

### Where the article is weakest for *our* purposes

- **Dhall adds management overhead** that the user has explicitly
  told the assistant to minimise. Generating YAML from Dhall means a
  second toolchain (`dhall-json`), a generation step (`dhall-to-yaml
  --file ci.dhall > ci.yml`), and a custom action library
  (`regadas/github-actions-dhall`) whose pinning becomes one more
  thing to track. The semantic-integrity benefit is real but small;
  the cost is friction on every workflow edit. **For a low-management
  setup, write YAML directly and skip Dhall.**
- **Cachix is a third-party service** and signing a Maven Central
  artifact whose build cache passed through a third-party CDN
  weakens the supply-chain story we're optimising for. For
  release builds (as opposed to test-on-PR runs), the case for
  pulling from Cachix is weakest precisely when reproducibility
  matters most. The author's own assessment — "I could probably get
  away without using Cachix" — agrees. **Skip Cachix on release
  workflows; consider it only for test/PR workflows if cold-build
  cost becomes painful.**
- **The Scala worked example is a microsite publish, not a Maven
  Central release.** Don't read it as a template for our Mill
  signing pipeline.

## Distilled takeaways for the in-flight CI / publish design

1. **Adopt the `shell.nix` (or `flake.nix`) discipline** so the
   build toolchain (JDK, Mill, optionally `sbt` for legacy)
   is hermetically pinned and identical between dev laptop and
   CI runner. This directly satisfies the "I don't trust the
   GitHub runner's preinstalled toolchain" concern raised
   2026-05-29 in this thread.
2. **Skip Dhall.** Hand-written workflow YAML costs less to
   maintain than the Dhall generation pipeline at this scale.
3. **Skip Cachix on release jobs.** Acceptable on a test/PR job
   if cold-build time becomes an issue. Even there, Volpe's own
   data ("I could probably get away without") argues for
   YAGNI.
4. **The article is silent on the signing half** — the YubiKey
   vs CI-secret question must be answered from elsewhere.
5. **Use flakes, not `fetchTarball`**, given the article's age.
   The conceptual model is identical (content-addressed pin of
   nixpkgs); the implementation moved to `flake.lock`.

## Promotion candidates

None at this ingest. Reasons:

- The `shell.nix` discipline is a strong candidate for a future
  tech-layer guide on "Nix-wrapped Mill builds in CI", but a
  single 2020 blog post about Ruby+Haskell+Scala is insufficient
  evidence to promote a Mill-specific pattern. Wait for a project
  ADR that adopts the pattern (likely on the open-source libraries
  this conversation is designing the release pipeline for).
- Dhall is a *negative* recommendation in our context — there's no
  page shape for "third-party preference we considered and rejected"
  outside an anti-pattern, and Dhall doesn't rise to anti-pattern
  status here. It's just a path we don't take.
- Cachix similarly — not adopted, not rejected as an anti-pattern,
  just out of scope until cold-build pain motivates it.

## Effect on prior wiki state

- No existing tech-layer page addresses GitHub Actions, CI workflow
  authoring, Cachix, or Dhall.
- `tech/guides/mill-cross-platform.md`, `tech/guides/mill-monorepo.md`,
  and `tech/guides/mill-dependency-management.md` all assume a Mill
  build but say nothing about the *environment* the build runs in.
  This article fills that gap descriptively; whether it should become
  a normative `tech/guides/nix-wrapped-mill-ci.md` is a future
  decision after the open-source libraries' release pipeline lands.
- The in-flight conversation references "Phase 1: GitHub Actions for
  tests + builds (running inside `nix develop`), Phase 2: NixOS
  build host if company release work justifies it." This article is
  the closest existing reference for *Phase 1*; no existing wiki
  page documents it.

## Open questions

1. **Does the user want this captured as a `tech/guides/` page now,
   or stage it until a project adopts the pattern in code?** Default
   answer per CLAUDE.md / breakout discipline: wait for the code.
2. **Promote `sources/tmp/github_actions_nix_cachix_dhall_gvolpe.md`
   to `sources/raw/docs/`?** Only if the article should be preserved
   as durable raw source; the summary alone may be enough since the
   article is publicly reachable.
3. **Worth adding a glossary entry for "Cachix" / "Dhall"?** Only if
   either ends up cited elsewhere in the wiki.

## Links

- [[sources/tmp/github_actions_nix_cachix_dhall_gvolpe]] — raw extraction (staged)
- [[tech/guides/mill-cross-platform]] — Mill build conventions (silent on CI environment)
- [[tech/guides/mill-monorepo]] — Mill repo layout (silent on CI environment)
- [[tech/stack/mill]] — Mill version policy
- External: https://gvolpe.com/blog/github-actions-nix-cachix-dhall/
