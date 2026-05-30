---
id: deploymentbox-design-release-pipeline-v3-github-attested
title: Release pipeline v3 — GitHub Actions build + sigstore attestation + local YubiKey sign + clean-machine re-verify
kind: descriptive
status: accepted
project: deploymentbox
created: 2026-05-30
updated: 2026-05-30
related_adrs:
  - projects/deploymentbox/adr/0004-tag-driven-central-releases.md
  - projects/deploymentbox/adr/0007-build-on-github-with-attestations.md
related_plans: []
supersedes:
  - projects/deploymentbox/designs/release-pipeline.md
  - projects/deploymentbox/designs/release-pipeline-v2-microvm.md
sources:
  - sources/summaries/github_actions_nix_cachix_dhall_gvolpe.md
  - projects/deploymentbox/designs/release-pipeline-v2-microvm.md
---

## What's different from v2

[v2](release-pipeline-v2-microvm.md) ran the build inside a
Firecracker microVM on a self-managed Hetzner host, with MinIO
artifact handoff and SHA-256 manifest verification before signing.
The threat model it closed — *malicious dep cannot reach the
host's signing path* — is real, but the trust root was
operator-managed infrastructure (Hetzner provider, NixOS config,
microvm.nix toolchain, MinIO, gpg-agent forwarding).

v3 makes a different trade for **public open-source artifacts**:
let GitHub Actions build, get a cryptographically-verifiable
proof of *what was built from what source* via the sigstore-backed
**build provenance attestation** (`actions/attest-build-provenance`),
download to the operator's laptop, verify the attestation, sign
locally with YubiKey, upload to Sonatype, and re-verify on a
clean machine after publish.

The trade:

- **Loses:** operator-controlled build environment, custom
  hardening surface, "single chokepoint we own end-to-end".
- **Gains:** $0 cost (free for public repos), cryptographic
  source-to-artifact provenance (stronger than v2's bare SHA),
  ephemeral fresh-every-run runners, no host to maintain or
  harden, public reproducibility (any community member can
  re-build from the tag and compare), no SSH forwarding ceremony.

v3 is **scoped to public OSS artifacts only.** If a future
private artifact ever ships, it stays on the v2-shaped path
(preserved in the wiki as historical record). The
`no.virtual-architect` libraries listed in
[[projects/deploymentbox/index]] are all in scope for v3 today.

v2 sections that **remain** valid in spirit: tag-driven releases,
release-only (no snapshots), one GPG key for all libraries,
YubiKey-only key custody, Sonatype Central Portal as the
distribution target. Those are captured in
[[projects/deploymentbox/adr/0004-tag-driven-central-releases]]
which carries over unchanged.

v2 sections that v3 **replaces**: the entire host architecture
(Hetzner CX32, NixOS hardening, MinIO, Firecracker microVM,
SSH-forwarded gpg-agent socket).

## v3 architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│ Library repo on github.com/tigidar/<repo>                            │
│                                                                      │
│   .github/workflows/release.yml                                      │
│     on: push: tags: ['v*']                                           │
│                                                                      │
│     permissions:                                                     │
│       id-token: write     # required for sigstore OIDC               │
│       attestations: write # required for attest-build-provenance     │
│       contents: read                                                 │
│                                                                      │
│     steps:                                                           │
│       ├─ actions/checkout@<sha>       # pinned to commit SHA         │
│       ├─ DeterminateSystems/nix-installer-action@<sha>               │
│       ├─ nix develop -c mill -i __.compile                           │
│       ├─ nix develop -c mill -i __.test                              │
│       ├─ nix develop -c mill -i __.publishM2Local                    │
│       ├─ stage artifacts under ./bundle/  (jars, poms, modules)      │
│       ├─ build sha256 manifest of ./bundle/                          │
│       ├─ actions/attest-build-provenance@<sha>                       │
│       │     subject-path: ./bundle/**/*                              │
│       │                  → sigstore-signed SLSA provenance           │
│       │                    bundled per-artifact .sigstore.json       │
│       └─ actions/upload-artifact@<sha>                               │
│             name: release-<tag>                                      │
│             path: ./bundle/                                          │
│                                                                      │
└────────────────────────┬─────────────────────────────────────────────┘
                         │  (operator pulls manually,
                         │   YubiKey plugged into laptop)
                         ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Operator's laptop                                                    │
│                                                                      │
│   1.  gh run download <run-id> --dir ./work/<tag>/                   │
│                                                                      │
│   2.  gh attestation verify ./work/<tag>/**/*.jar \                  │
│         --repo tigidar/<repo>                                        │
│       → asserts: this artifact was built by this workflow            │
│         from this source SHA, signed by sigstore.                    │
│       → on failure: abort, never sign, surface the failure.          │
│                                                                      │
│   3.  sha256sum -c manifest.sha256                                   │
│       (capture the verified SHAs into ./work/<tag>/sha256.txt        │
│        for the clean-machine re-verify step later)                   │
│                                                                      │
│   4.  For each artifact in ./work/<tag>/:                            │
│         gpg --detach-sign --armor <artifact>                         │
│       YubiKey blinks; operator touches; signature written.           │
│       (No SSH forwarding — laptop *is* the operator.)                │
│                                                                      │
│   5.  Assemble Sonatype Central Portal bundle:                       │
│         release-bundle.zip = <signed jars+poms+modules+.asc files>   │
│                                                                      │
│   6.  Upload to Central Portal (REST API):                           │
│         POST /api/v1/publisher/upload                                │
│         Authorization: Bearer <portal-token>                         │
│       → returns deploymentId; Portal validates;                      │
│       → operator either auto-publishes or reviews-then-publishes.    │
│                                                                      │
└────────────────────────┬─────────────────────────────────────────────┘
                         │  (Central propagation: minutes to hours)
                         ▼
┌──────────────────────────────────────────────────────────────────────┐
│ Clean verification machine                                           │
│ (spare laptop, fresh live-USB session, throwaway VM —                │
│  any host whose state is independent of the laptop above)            │
│                                                                      │
│   1.  Pull the published artifact from Maven Central:                │
│         curl -O https://repo1.maven.org/maven2/no/virtual-architect/ │
│              <lib>/<tag>/<lib>-<tag>.jar                             │
│         curl -O <…>.jar.asc                                          │
│                                                                      │
│   2.  Verify GPG signature against the project public key:           │
│         gpg --verify <lib>-<tag>.jar.asc <lib>-<tag>.jar             │
│                                                                      │
│   3.  Recompute SHA-256 and compare against the sha256.txt           │
│         captured at step 3 above.                                    │
│         Out-of-band channel for the comparison value — e.g.          │
│         operator types both hashes into a shared doc.                │
│                                                                      │
│   4.  Independently, on the clean machine:                           │
│         gh attestation verify <lib>-<tag>.jar \                      │
│           --repo tigidar/<repo>                                      │
│       Proves: "the artifact Central now serves was built by          │
│       the same workflow from the same source SHA."                   │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

## Per-release flow (operator-side)

From the operator's laptop, YubiKey plugged in, GitHub CLI
(`gh`) authenticated:

```bash
# 1. Tag and push to trigger the workflow.
cd /p/hg/<lib>
git tag -s v0.1.0 -m "release v0.1.0"
git push origin v0.1.0

# 2. Wait for workflow success (the operator watches gh run watch).
gh run watch --repo tigidar/<lib>

# 3. Download artifacts + attestations to a per-release working dir.
mkdir -p ./work/v0.1.0 && cd ./work/v0.1.0
gh run download --repo tigidar/<lib> --name release-v0.1.0 --dir .

# 4. Verify the sigstore attestation chain.
gh attestation verify ./**/*.jar --repo tigidar/<lib>

# 5. Verify the manifest (defense in depth — catches local
#    download corruption before signing).
sha256sum -c manifest.sha256

# 6. Sign every artifact. Touch YubiKey per artifact.
for f in ./**/*.{jar,pom,module}; do
  gpg --detach-sign --armor "$f"
done

# 7. Bundle and upload to Sonatype Central Portal.
release-cli upload \
  --bundle ./bundle.zip \
  --deployment-name "<lib>-v0.1.0"
```

Typical timing for a small library:

| Step | Time | Notes |
|---|---|---|
| Push tag | <1s | |
| GitHub workflow boot + checkout | 30-60s | runner provisioning |
| Cold Nix install + dev shell | 2-5 min | first time runner pulls flake closure |
| Warm dev shell | 30s | with Magic Nix Cache or DeterminateSystems setup |
| Mill compile + test | varies | per library |
| Attestation generation + upload | 10-30s | sigstore signs from GitHub OIDC |
| Operator download to laptop | 5-30s | depends on bandwidth |
| `gh attestation verify` | 2-5s | local sigstore verification |
| `sha256sum -c` | <1s | |
| Sign | 10-30s | one YubiKey touch per artifact |
| Central Portal upload | 10-60s | |
| Central propagation to `repo1.maven.org` | minutes-hours | out of operator's control |
| Clean-machine re-verify | 1-2 min | once Central serves the artifact |

Total operator wall-time (excluding propagation wait):
**~10 minutes** for a small library, ~half spent on the workflow
boot/cold-cache. The clean-machine re-verify happens
asynchronously the same day or the next morning.

## Secrets map (v3)

| Credential | Lives on | Used for | Lifetime |
|---|---|---|---|
| GPG signing private key | YubiKey hardware | every Central artifact | identity-lifetime |
| GPG public key | keyservers + project README + operator laptop GNUPGHOME | verification | identity-lifetime |
| GPG revocation cert | operator's offline backup | emergency revocation | identity-lifetime |
| Sonatype Central Portal token | operator's laptop, **password-manager / keychain** | upload to Central | rotatable |
| GitHub CLI auth token | operator's laptop, `gh auth login` | `gh run download`, `gh attestation verify` | rotatable |
| GitHub Actions runtime token | ephemeral, GitHub-managed | sigstore OIDC for `attest-build-provenance` | per-workflow-run |

What the *operator's laptop* now holds (steady state):

- The YubiKey (when plugged in).
- The Sonatype Portal token (in a password manager or OS keychain,
  not on disk in plaintext).
- The GitHub CLI auth.
- The GPG public key for verification.

What no longer exists in the secrets map:

- ~~Host SSH private key~~ — no host.
- ~~Host SSH public key in flake~~ — no host.
- ~~MinIO root credentials~~ — no MinIO.
- ~~MinIO microvm-build credentials~~ — no microvm.
- ~~`StreamLocalBindUnlink` SSH config~~ — no SSH forwarding.

## Trust model

What v3 trusts:

1. **GitHub Actions infrastructure.** Runner provisioning,
   workflow execution, OIDC token issuance for sigstore.
   This is the largest new trust dependency relative to v2.
   Mitigation: source is already hosted on GitHub, so this is
   not a *new* trust relationship — the operator was already
   trusting GitHub with source integrity.
2. **Sigstore root.** The transparency log + trust roots that
   make `gh attestation verify` cryptographically meaningful.
   Sigstore is operated by the OpenSSF (Linux Foundation);
   widely adopted (npm, PyPI, Maven Central itself, container
   registries).
3. **Operator's laptop.** Where signing happens; where the
   YubiKey plugs in; where the Portal token lives. Same trust
   it always had.
4. **YubiKey hardware.** Key custody. Unchanged from v2.
5. **Sonatype Central Portal.** Distribution endpoint.
   Unchanged from v2.

What v3 *no longer trusts* (because it's gone):

- The Hetzner provider.
- A long-running NixOS host config.
- A microvm.nix runtime + Firecracker hypervisor.
- A MinIO instance.
- An SSH+gpg-agent forwarding chain.

The clean-machine re-verify step is the operator's
"trust-but-verify" capstone: it proves that what Central
serves matches what the operator signed *and* matches what
GitHub Actions built. A compromise anywhere in the chain
that produced a *different* artifact would surface here.

## Threat model — what v3 defends against, what it doesn't

**Defended:**

- **Operator laptop compromise as a build vector.** The build
  doesn't happen on the laptop. Source goes through GitHub,
  build happens on an ephemeral GitHub runner. A laptop that
  *also* has malware can still sign with the YubiKey if the
  operator touches — but only artifacts the operator chose to
  sign; touch is gated by physical presence.
- **Malicious transitive dependency.** Executes only on the
  ephemeral GitHub runner — the runner is destroyed after the
  workflow. No persistent state to attack. Cannot reach
  the signing key (never on the runner). Cannot publish to
  Central (no Portal token on the runner). Cannot poison
  subsequent builds (fresh runner every time).
- **Tampering in transit from runner to laptop.** Sigstore
  attestation includes the artifact digest signed at build
  time; `gh attestation verify` recomputes and matches.
  Tampering surfaces here.
- **Tampering in transit from laptop to Central.** Central
  validates the GPG signature; downstream consumers re-verify.
  A mid-flight tampering would invalidate the signature.
- **Tampering between Central and consumers.** Sigstore
  attestation re-verified on the clean machine catches this
  too, *if* the operator publishes the run ID alongside the
  release so consumers can run `gh attestation verify` against
  the artifacts they pulled from Maven Central.

**Not defended (and accepted):**

- **GitHub Actions runner is fundamentally compromised at the
  infrastructure level.** If the entire GitHub Actions control
  plane is suborned, the attacker can produce a malicious
  artifact, get a *valid sigstore attestation for it*, and the
  chain looks clean. Mitigation: this is the same trust the
  operator already extends to GitHub for source hosting.
  Reproducibility-from-source (any community member can
  re-build the tag) is the practical backstop.
- **Sigstore root compromise.** Same class as a CA compromise.
  Out of scope for an individual project; trust delegated to
  the OpenSSF.
- **Sonatype Central infrastructure compromise.** If Central
  serves a different artifact than was uploaded, the
  clean-machine re-verify step catches it provided the operator
  captured the laptop-side SHA-256 out-of-band before upload.
- **Operator's password manager compromise leaks the Portal
  token.** Attacker can upload artifacts impersonating the
  operator — but without the GPG signing key (YubiKey,
  hardware-bound), the artifacts won't validate Central's
  signature check. Worst-case: a denied upload. Token is
  rotatable.

## Trade-off table (v3 vs v2)

| Property | v2 (host+microVM) | v3 (GitHub+attestations) |
|---|---|---|
| Build environment isolation | Firecracker microVM on operator host | Ephemeral GitHub-hosted runner |
| Trust root for the build | Operator-managed (Hetzner, NixOS, microvm.nix) | GitHub Actions infra + sigstore |
| Provenance | SHA-256 manifest (integrity only) | SLSA-3 sigstore attestation (source-to-artifact) |
| Cost | ~€7-8/mo + maintenance time | $0 for public repos |
| Operator wall-time per release | ~10-20 min (cold microVM) / 5 min (warm) | ~10 min (cold runner) / 5-8 min (warm) |
| Cold-start cost | microVM kernel + nix store pull | runner provision + nix install |
| Hardware required | Hetzner CX32 | None (operator's laptop only) |
| Where signing happens | Host (SSH-forwarded YubiKey) | Laptop (direct YubiKey, no forwarding) |
| Operator surface | ssh + remote command | gh CLI pull + local sign |
| Public reproducibility | None — operator-private host | Anyone can re-run the workflow on their own fork |
| Defended against malicious dep | Yes (microVM isolation) | Yes (ephemeral runner) |
| Defended against host compromise | N/A — host is the trusted thing | N/A — no host |
| Defended against GitHub Actions infra compromise | Yes (GitHub never built it) | No (accepted trust) |
| Maintenance burden | NixOS host, microVM, MinIO, audit logs | One YAML file per repo |
| Scope | All artifacts | **Public OSS only** |

## Implementation map (where each piece lives)

| Component | Where |
|---|---|
| Release workflow | `<lib-repo>/.github/workflows/release.yml` |
| Test-only workflow (PR-time) | `<lib-repo>/.github/workflows/test.yml` (already separate per ADR-0001 §Alternatives) |
| Per-library Mill publish config | `<lib-repo>/build.mill` (unchanged from v2 — `pomSettings`, `groupId`, etc.) |
| `flake.nix` for dev shell + toolchain | `<lib-repo>/flake.nix` (unchanged) |
| Operator-side release script | `~/.local/bin/release` (or similar) on the laptop — orchestrates `gh run download`, `gh attestation verify`, `sha256sum -c`, sign loop, Portal upload |
| Operator's GPG public key | published on `keys.openpgp.org` + linked from each library's README |
| Operator's GPG public key (consumer fetch) | `gpg --recv-key <fingerprint>` from a keyserver |

What gets **deleted** from the operator's surface (vs v2):

- `/p/hg/deploymentbox/` Hetzner host scaffold — kept in the
  repo as historical record / starting point for any future
  private-artifact path, but no longer the active publishing
  mechanism.
- Hetzner CX32 — never provisioned.
- MinIO, microvm.nix, hardening modules — never deployed.
- The `release.sh` orchestration on the host — replaced by a
  laptop-side script that calls `gh` and `gpg`.

## Open questions

1. **Reproducible-build cross-check.** Before signing, should
   the operator do a local `nix develop -c mill ... publishM2Local`
   from the same tag and compare hashes against the GitHub-built
   artifact? Cheap insurance against "GitHub Actions silently
   produced something different" — but doubles operator
   wall-time. Defer; revisit if a real cause arises.
2. **Where to publish the operator GPG public key.** Sonatype
   no longer requires a keyserver upload (since Central Portal
   removed the keyserver dependency), but consumers still need
   it for `gpg --verify` re-checks. Publishing on
   `keys.openpgp.org` and linking from each library README is
   the minimum; mirroring on a `.well-known/openpgp.asc` on
   `virtual-architect.no` would be belt-and-suspenders.
3. **Pinning actions to commit SHAs vs version tags.** v3
   workflows must pin every used action to a commit SHA, not
   `@v1`/`@main` tags — tags are mutable. Recorded here as a
   workflow-level invariant so any future workflow templates
   carry it.
4. **Workflow concurrency control.** Two simultaneous tag
   pushes shouldn't both produce conflicting Central
   uploads. `concurrency: { group: release-${{ github.ref }} }`
   on the workflow.
5. **YubiKey ceremony.** Carried over from v2 open question #1
   — orthogonal to v3, same answer needed (offline-generate +
   dual-YubiKey backup + offline master + revocation cert).
   Recorded once here; not duplicated per-version.
6. **Disposition of the staged `/p/hg/deploymentbox/` v2
   work.** Three options:
     - (a) Commit it as historical record (matches the
       wiki's "preserved as historical record" pattern for v1
       and v2 designs), then leave the repo dormant.
     - (b) Revert and let the v1 commit `a978a76` stand as the
       project's last meaningful state.
     - (c) Keep the staged changes uncommitted as a "future
       private-artifact pipeline starting point."
   Recommended: (a). The repo's `README.md` should add a note
   that v3 moved the publishing pipeline into GitHub Actions
   and that this repo is dormant unless a private-artifact
   pipeline is needed.
7. **Sonatype Portal API client.** The v2 `release.sh` used
   `curl` against the Central Portal REST endpoints. v3 needs
   the same logic in the laptop-side script. Options: keep
   `curl` + `jq`, adopt a small Scala CLI, or use Mill's
   built-in publishCentral if that supports the Portal API
   (older Mill only knows the legacy OSSRH endpoints — check
   per-library Mill version before relying on it).
8. **Test-only workflow split.** Each library should have
   `.github/workflows/test.yml` (PR-time, no secrets, no
   attestations) **separate from** `.github/workflows/release.yml`
   (tag-triggered, has `id-token: write` and `attestations:
   write`). Keeps the high-privilege surface as small as
   possible — only the release workflow ever sees the elevated
   token scopes.

## Decision Record

v3 is the **accepted** architecture as of 2026-05-30 for all
public `no.virtual-architect` artifacts. v2 stays in the wiki
as `release-pipeline-v2-microvm.md` with `status: superseded`;
its scaffold under `/p/hg/deploymentbox/` is preserved for the
historical record (and as a starting point if a private-artifact
pipeline is ever needed).

ADR-0007 ([[projects/deploymentbox/adr/0007-build-on-github-with-attestations]])
is the load-bearing decision. It supersedes ADRs 0001, 0002,
0005, 0006, and the SSH-forwarding part of 0003.

ADR-0004 ([[projects/deploymentbox/adr/0004-tag-driven-central-releases]])
remains accepted unchanged — tag-driven releases, release-only,
one GPG key, `no.virtual-architect` groupId all carry over.
