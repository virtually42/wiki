---
id: wip-deploymentbox
title: WIP — v3 accepted; first library workflow + laptop script pending
kind: session
status: active
project: deploymentbox
created: 2026-05-30
updated: 2026-05-30
branch: main
related:
  - projects/deploymentbox/designs/release-pipeline-v3-github-attested.md
  - projects/deploymentbox/adr/0007-build-on-github-with-attestations.md
---

## Goal

Stand up the **deploymentbox v3** publishing pipeline: GitHub Actions
builds public `no.virtual-architect` artifacts, sigstore attestation
proves source-to-artifact provenance, operator pulls to laptop,
verifies attestation, signs locally with YubiKey, uploads to Sonatype
Central Portal, re-verifies on a clean machine after publish. v3
replaces the v2 Hetzner-host + Firecracker-microVM + MinIO design for
the public-OSS scope.

## Status

- **Wiki:** v3 design + ADR-0007 landed and accepted. v1 + v2 designs
  and ADRs 0001/0002/0003/0005/0006 marked `superseded` with
  `superseded_by` pointing to 0007 (or to the v3 design as
  appropriate). ADR-0004 (tag-driven, one key, no snapshots, groupId
  `no.virtual-architect`, Central Portal endpoint) carries over
  unchanged. Project `index.md` rewritten for v3. All wiki updates
  complete.
- **Repo (`/p/hg/deploymentbox/`):** v2 changes still staged
  uncommitted from the 2026-05-29 session (8 modified files + 4 new
  paths — full list in 2026-05-29 wip below `Files Touched`). v3
  open question #6 records the recommended disposition: commit as
  historical record + add README note that v3 moved the pipeline into
  GitHub Actions; let the repo go dormant. **Not yet done.**
- **First library `release.yml`:** not yet written. v3 spec is in
  ADR-0007 §"What v3 requires of each library repo" — the YAML
  itself lives in each library repo and the deploymentbox project
  only commits to the *invariants* (pinned action SHAs, `id-token`
  + `attestations` permissions, separate test workflow,
  `attest-build-provenance` over every published artifact).
- **Operator-side release script:** not yet written. Will live in
  operator dotfiles or as a small tool. v3 design §"Per-release
  flow" sketches the seven-step shape; needs translation into an
  actual script.
- **Sonatype namespace `no.virtual-architect` verification:**
  unchanged from v2 — DNS TXT on `virtual-architect.no` via
  uniweb.no still pending. Until verified, the final Central upload
  step (any version) returns 403. v3-orthogonal: do it in parallel.
- **YubiKey ceremony:** unchanged from v2 — not yet done. Recorded
  as v3 design open question #5 (orthogonal to architecture).
- **Hetzner server:** never provisioned. v3 does not need one.
  Don't provision.
- **First publish:** never attempted.

## Files Touched

### Wiki (2026-05-30)

- `projects/deploymentbox/designs/release-pipeline-v3-github-attested.md`
  — NEW. v3 source-of-truth design (architecture diagram, per-release
  flow, secrets map, trust model, threat model, trade-off table vs v2,
  open questions).
- `projects/deploymentbox/adr/0007-build-on-github-with-attestations.md`
  — NEW. Load-bearing v3 decision. Supersedes 0001/0002/0003/0005/0006.
  Records per-library workflow invariants.
- `projects/deploymentbox/designs/release-pipeline-v2-microvm.md` —
  marked `status: superseded`, `superseded_by:` v3 design.
- `projects/deploymentbox/adr/0001-host-hetzner-nixos.md` — marked
  `status: superseded`, `superseded_by:` 0007.
- `projects/deploymentbox/adr/0002-public-ssh-hardened.md` — marked
  `status: superseded`, `superseded_by:` 0007.
- `projects/deploymentbox/adr/0003-signing-yubikey-forwarded.md` —
  marked `status: superseded`, `superseded_by:` 0007 (key-custody
  contract carries over; SSH-forwarding transport is what's gone).
- `projects/deploymentbox/adr/0005-build-in-firecracker-microvm.md`
  — marked `status: superseded`, `superseded_by:` 0007.
- `projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening.md`
  — marked `status: superseded`, `superseded_by:` 0007.
- `projects/deploymentbox/index.md` — rewritten for v3 (stack, role
  diagram, ADR list, pages list, out-of-scope, open questions).
- `projects/deploymentbox/wip.md` — this file (overwritten).
- `projects/deploymentbox/log.md` — new top entry.
- `meta/log.md` — new top entry.
- `index.md` (top-level) — deploymentbox project row updated for v3
  stack + status.

### Repo (`/p/hg/deploymentbox/`)

Unchanged this session. The v2 staged-but-uncommitted changes from
2026-05-29 are still in the working tree. Disposition decided in v3
design open question #6 — recommended commit + dormant marker is
**not yet executed** (operator's call; personal-repo commit policy
applies).

## Decisions

(Full reasoning in ADR-0007; listed here for cold-resume context.)

- **GitHub Actions + sigstore attestation is the v3 build path** for
  all public `no.virtual-architect` artifacts.
- **Operator's laptop is where signing happens** — no remote host, no
  SSH forwarding. YubiKey reached via local gpg-agent. Touch-required
  mode on the YubiKey carried over from ADR-0003's recommendation.
- **Sonatype Central Portal REST upload from the laptop**, with the
  Portal token in a password manager / OS keychain (not on disk in
  plaintext).
- **Post-publish re-verification on a clean machine** (spare laptop,
  live USB, throwaway VM) is mandatory: `gpg --verify` + SHA-256
  re-check + `gh attestation verify` against Central-served bytes.
- **Per-library workflow invariants** enforced by ADR-0007: every
  `uses:` pinned to a commit SHA (not a tag), `id-token: write` +
  `attestations: write` permissions, separate `test.yml` for PR-time
  with no elevated permissions, `concurrency` group on the release
  workflow.
- **v3 is public-OSS-only.** Any future private artifact must use a
  v2-shaped pipeline (which is why v2 is preserved with
  `status: superseded` rather than deleted).
- **`no.virtual-architect` namespace + DNS TXT verification + single
  GPG key + tag-driven + release-only + Central Portal endpoint** —
  all carry over from ADR-0004 unchanged.

## Blockers

| # | Blocker | Unblock action |
|---|---|---|
| 1 | Sonatype namespace `no.virtual-architect` not verified | Add TXT record on `virtual-architect.no` via uniweb.no; wait for propagation; click *Verify Namespace* on central.sonatype.com. Carries over from v2 — DNS propagation eats hours, kick off first. |
| 2 | No library has a v3 `release.yml` yet | Author against the smallest library (recommend `sourceline-manager`). Use ADR-0007 §"What v3 requires of each library repo" as the spec. |
| 3 | No operator-side release script | Translate v3 design §"Per-release flow" into an actual script. Decide where it lives (`~/.local/bin/`, dotfiles, a small standalone tool). |
| 4 | YubiKey ceremony not done | Offline-generate + dual-YubiKey backup + offline master + revocation cert. Orthogonal; can happen any time before first real release. |
| 5 | `/p/hg/deploymentbox/` staged v2 changes uncommitted | v3 design open question #6: recommended action is "commit as historical record + add README note about v3 pipeline relocation + let repo go dormant." Operator's call. |
| 6 | Project GPG public key not yet published for consumer verification | Publish on `keys.openpgp.org`; link from each library README. Optionally mirror on `.well-known/openpgp.asc` on `virtual-architect.no`. |

## Next Step

**Today's #1: kick off the Sonatype DNS TXT record on `virtual-architect.no`** via uniweb.no.
Propagation takes hours — start it first, do the rest in parallel.
(Same Blocker #1 as the v2 wip — v3 inherits this from ADR-0004
unchanged.)

After the TXT is in place (or in parallel):

1. Verify on central.sonatype.com when DNS propagates.
2. Author `release.yml` against `sourceline-manager` first
   (smallest library — fastest iteration on the YAML).
3. Author the laptop-side release script.
4. Resolve `/p/hg/deploymentbox/` disposition (recommend: commit
   staged changes + add README v3 note + let dormant).
5. Publish project GPG public key on `keys.openpgp.org`.
6. YubiKey ceremony.
7. Dry-run release of `sourceline-manager` against an invalid tag
   to exercise the full workflow without publishing.
8. First real release.

## Resume Instructions

To resume cold in a fresh session:

1. Open this file (`projects/deploymentbox/wip.md`) — current state.
2. Read `projects/deploymentbox/log.md` top entry (session snapshot
   from 2026-05-30) for the longer decision trace of the v2→v3
   pivot.
3. v3 architecture: `projects/deploymentbox/designs/release-pipeline-v3-github-attested.md`.
4. v3 load-bearing decision: `projects/deploymentbox/adr/0007-build-on-github-with-attestations.md`.
5. Carry-over decision: `projects/deploymentbox/adr/0004-tag-driven-central-releases.md`.
6. Historical record for the v2 path (in case a private artifact
   ever needs to ship): `projects/deploymentbox/designs/release-pipeline-v2-microvm.md` + ADRs 0001/0002/0003/0005/0006.
7. Repo: `/p/hg/deploymentbox/` (v1 committed at `a978a76`; v2
   changes staged uncommitted; v3 has no repo state — pipeline
   lives in each library's `.github/workflows/`).

External-lib / source references that were load-bearing for v3:

- [[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]] —
  the per-repo flake-pinned toolchain pattern that makes GitHub
  runners hermetic. Load-bearing for ADR-0007's hermeticity
  argument.
