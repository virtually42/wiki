# deploymentbox

Publishing pipeline for signed `no.virtual-architect` Maven Central
artifacts. Public OSS artifacts are built on GitHub Actions, get a
sigstore-backed build provenance attestation, are downloaded to the
operator's laptop, verified, signed locally with a YubiKey, uploaded to
the Sonatype Central Portal, and re-verified on a clean machine after
publish. The signing key lives only on the YubiKey — never on a server,
never in CI secrets.

**Status:** active (v3 accepted 2026-05-30 — pre-first-release; the v1
Hetzner-host and v2 Firecracker-microVM designs are preserved as
historical record)

## Stack

- Build: GitHub Actions hosted runner with per-library `nix develop`
  toolchain (Volpe pattern — see [[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]])
- Provenance: sigstore SLSA-3 build attestation via `actions/attest-build-provenance`
- Verification (laptop side): `gh attestation verify` + `sha256sum -c`
- Signing: YubiKey 5 + gpg-agent on operator's laptop (no SSH forwarding, no remote host)
- Distribution: Sonatype Central Portal REST API
- Verification (clean machine, post-publish): `gpg --verify` against project public key + `sha256sum` re-check + `gh attestation verify` against Central-served bytes
- Cost: €0 (GitHub Actions is free for public repos)

## Code Location

**v3 has no operator-managed host.** The "code" of the v3 pipeline is:

- `.github/workflows/release.yml` in each library repo (tag-triggered, signs nothing — only builds + attests + uploads)
- `.github/workflows/test.yml` in each library repo (PR-time, no elevated permissions)
- A small operator-side release script on the laptop (pulls artifacts, verifies attestation, signs loop, uploads to Central)

Historical: `/p/hg/deploymentbox/` contains the v2 NixOS host scaffold
(staged uncommitted). Disposition is open (v3 design open question #6);
recommended path is "commit as historical record, then dormant." If a
private artifact ever ships, that repo is the starting point for a
v2-shaped revival.

Personal-repo commit policy applies to `/p/hg/deploymentbox/` (unsigned,
no Co-Authored-By, author `tigidar`).

## Role in the Wiki

The deploymentbox project is the **policy + workflow definition** for
publishing every `no.virtual-architect` artifact to Maven Central. v3
relocates the actual work into GitHub Actions + the operator's laptop:

```
github.com/tigidar/<lib>             github.com/tigidar/<lib>
  on: push: tags: ['v*']        ──►   release.yml workflow runs:
                                       │  nix develop -c mill publishM2Local
                                       │  actions/attest-build-provenance
                                       │  actions/upload-artifact
                                       ▼
                                  (sigstore-signed attestation +
                                   artifact bundle stored on GitHub)
                                       │
                                       │ gh run download
                                       ▼
                              operator's laptop (YubiKey plugged in)
                                       │  gh attestation verify  ◄── abort if fails
                                       │  sha256sum -c
                                       │  gpg --detach-sign  (YubiKey touch)
                                       │  POST /api/v1/publisher/upload
                                       ▼
                              Sonatype Central Portal
                                       │
                                       │ (propagation)
                                       ▼
                                Maven Central
                                       │
                                       │ pulled out-of-band
                                       ▼
                              clean verification machine
                                       │  gpg --verify
                                       │  sha256sum re-check
                                       │  gh attestation verify
                                       ▼
                                 release confirmed
```

The detailed flow with timing, secrets map, and trust model lives in
[[projects/deploymentbox/designs/release-pipeline-v3-github-attested]].

Libraries currently in scope: [[projects/safetensors-scala]],
[[projects/sourceline-manager]], [[projects/toolbox]],
[[projects/tagless]], [[projects/shapesdsl]], [[projects/animdsl]],
and any future `/p/hg/` library open-sourced under
`no.virtual-architect`. [[projects/dependency-manager]] is **out of
scope** — intentionally unlicensed, not for distribution.

## Pages

### Designs

- [designs/release-pipeline-v3-github-attested.md](designs/release-pipeline-v3-github-attested.md)
  — **current** end-to-end architecture: GitHub Actions build +
  sigstore attestation + local YubiKey sign + clean-machine
  re-verify. Trust model, threat model, trade-off table vs v2,
  secrets map, open questions.
- [designs/release-pipeline-v2-microvm.md](designs/release-pipeline-v2-microvm.md)
  — **superseded.** Firecracker microVM + MinIO + SHA-256 manifest.
  Preserved as historical record and as the starting point if a
  private-artifact pipeline is ever needed.
- [designs/release-pipeline.md](designs/release-pipeline.md)
  — **superseded.** v1 host-builds-directly threat model. Preserved
  as historical record.

### ADRs

#### Accepted (v3)

- [adr/0007-build-on-github-with-attestations.md](adr/0007-build-on-github-with-attestations.md)
  — **load-bearing v3 decision.** Build on GitHub Actions; verify via
  sigstore attestation; sign on laptop; re-verify on clean machine.
  Supersedes ADRs 0001 / 0002 / 0003 / 0005 / 0006. Records what the
  workflow YAML must contain, what the laptop script must do, and
  what trust dependencies v3 accepts vs the dependencies it removes.
- [adr/0004-tag-driven-central-releases.md](adr/0004-tag-driven-central-releases.md)
  — **still accepted, unchanged.** groupId `no.virtual-architect`;
  release flow keyed on git tags; releases only (no snapshots); one
  GPG key for all libraries; Sonatype Central Portal endpoint. v3
  inherits all of this.

#### Superseded (kept as historical record)

- [adr/0001-host-hetzner-nixos.md](adr/0001-host-hetzner-nixos.md)
  — Hetzner CX32 NixOS as build host. Superseded by 0007 (no host).
- [adr/0002-public-ssh-hardened.md](adr/0002-public-ssh-hardened.md)
  — Public SSH on port 22 with `StreamLocalBindUnlink yes`.
  Superseded by 0007 (no host).
- [adr/0003-signing-yubikey-forwarded.md](adr/0003-signing-yubikey-forwarded.md)
  — GPG signing via SSH-forwarded gpg-agent. Superseded by 0007 for
  the *transport* part (signing now happens directly on the laptop);
  the *key-custody contract* (YubiKey-only, never on filesystem,
  never in CI secrets) carries over and is strengthened.
- [adr/0005-build-in-firecracker-microvm.md](adr/0005-build-in-firecracker-microvm.md)
  — Build inside Firecracker microVM. Superseded by 0007 (ephemeral
  GitHub runner gives equivalent isolation for public OSS;
  sigstore attestation is stronger than the v2 SHA manifest).
- [adr/0006-adopt-paranoid-nixos-hardening.md](adr/0006-adopt-paranoid-nixos-hardening.md)
  — Selected paranoid-NixOS layers. Superseded by 0007 (no host to harden).

### Tickets, plans, syntheses

*None yet.* Plans land when the first library's `release.yml` is
authored and the operator-side script is wired.

### Other

- [log.md](log.md)
- [wip.md](wip.md)

## Out of scope (and where the boundary is)

- **Library-side Mill `PublishModule` wiring.** Each `/p/hg/<lib>`
  decides for itself how it declares `pomSettings`, `groupId`,
  `developers`, `scmInfo`, etc. The deploymentbox project only
  specifies *that* libraries publish under `no.virtual-architect`
  (per ADR-0004) and *how* the release workflow runs (per ADR-0007)
  — the per-library publish config lives in each library's
  `build.mill`.
- **GitHub Actions PR-time test workflow.** Each library has a
  separate `.github/workflows/test.yml` (no `id-token` /
  `attestations` permissions, no signing path). That's intentional
  per ADR-0007 — keeps the high-privilege surface attached only to
  tag-triggered runs. Not in scope for the deploymentbox project's
  ADRs beyond that invariant.
- **`dependency-manager` releases.** dm is unlicensed and internal.
  v3 does not apply (v3 is public-OSS-only by ADR-0007 scope). If dm
  ever needs signed releases, it must reach for a v2-shaped
  self-managed pipeline.
- **Snapshot publishing.** Explicitly excluded per ADR-0004. Local
  cross-library iteration uses `mill __.publishLocal` on the
  developer machine; no SNAPSHOT artifacts ever reach Central.
- **Private artifact pipeline.** Out of scope. If a future
  `no.virtual-architect` library needs to ship privately, the v2
  design + ADRs 0001 / 0005 / 0006 are the starting point — that's
  why they're preserved with `status: superseded` rather than
  deleted.

## Open Questions

1. **Sonatype namespace verification timing.** The
   `no.virtual-architect` namespace claim is a DNS TXT exercise on
   `virtual-architect.no` via uniweb.no. Until the namespace verifies,
   the final Central upload step (any version) returns 403. The
   workflow + attestation + laptop verify path is exercisable
   end-to-end *without* publishing — only the final Central upload
   step needs the namespace.
2. **YubiKey key-generation ceremony.** Carried over from v2 open
   question. Offline-generate vs. on-device. Affects backup story
   but not the architecture. Resolve before first real release.
3. **Disposition of `/p/hg/deploymentbox/`.** v3 design open
   question #6. Recommended: commit the staged v2 changes as
   historical record + dormant marker, update the repo README to
   note v3 moved the pipeline into GitHub Actions.
4. **Where to publish the project GPG public key for consumer
   verification.** v3 design open question #2. Minimum:
   `keys.openpgp.org` + per-library README link. Belt-and-braces:
   `.well-known/openpgp.asc` on `virtual-architect.no`.
5. **First-library workflow author.** No library yet has the v3
   `release.yml`. First write happens against the smallest library
   (recommend `sourceline-manager`) so the operator can iterate on
   the YAML pattern against a small build before propagating.
