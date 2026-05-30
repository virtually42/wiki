# deploymentbox log

Append-only project log.

**Ownership: llm.**

---

## [2026-05-30] adr | v3 pivot — GitHub Actions + sigstore attestation supersedes v2 microVM substrate for public OSS

Day after v2 landed, the operator returned with a re-framed
question: would the *much simpler* path of "let GitHub build,
download to laptop, sign there, upload to Sonatype, re-verify on
clean machine" be just as secure as v2's Hetzner + Firecracker +
MinIO substrate?

In conversation: yes, for **public OSS specifically**, with one
material caveat — a plain SHA from GitHub is integrity-in-transit
only; it does not prove *what was built from what source*. The
primitive that makes v3 actually competitive with v2 on the
threat model is the **sigstore-signed build provenance
attestation** (`actions/attest-build-provenance`, GA 2024). The
attestation cryptographically binds artifact bytes → source commit
SHA → workflow run, witnessed in a public transparency log via the
runner's short-lived GitHub OIDC identity. That's SLSA Build L3 —
*stronger* than v2's bare SHA-256 manifest, which only proved "the
host signed what the microVM emitted."

With attestations in scope, v3's trade-off vs v2 net-favors
v3 for public OSS:

- **Loses:** operator-controlled build substrate, custom hardening
  surface, "single chokepoint we own end-to-end."
- **Gains:** €0 cost (saves €7-8/mo), cryptographic source-to-artifact
  provenance, ephemeral fresh-every-run runners, zero host
  maintenance, public reproducibility (anyone can fork and re-run
  the tag), no SSH-forwarding ceremony, signing key responses never
  leave the laptop USB bus.

The single new trust extension — GitHub Actions infrastructure for
the build — is a small delta relative to "GitHub already hosts the
source." The clean-machine re-verify step (pull from Maven Central
on a host independent of the laptop, run `gpg --verify` +
`sha256sum` re-check + `gh attestation verify`) is the
trust-but-verify capstone.

**Scope is explicitly public-OSS-only.** Recorded in ADR-0007 as a
load-bearing scope decision: if any future `no.virtual-architect`
artifact needs to ship privately, it must reach for a v2-shaped
self-managed pipeline, *not* extend v3. The v2 design + ADRs
0001/0005/0006 are preserved with `status: superseded` precisely so
they remain available as a starting point.

Created:

- `projects/deploymentbox/designs/release-pipeline-v3-github-attested.md`
  — v3 design (architecture, per-release flow, secrets map, trust
  model, threat model, trade-off table vs v2, open questions
  including "should we do local reproducible-build cross-check
  before sign?", "where to publish the project GPG public key?",
  "disposition of staged v2 repo work?").
- `projects/deploymentbox/adr/0007-build-on-github-with-attestations.md`
  — load-bearing v3 decision; supersedes 0001/0002/0003/0005/0006;
  records per-library workflow invariants (pinned action SHAs,
  `id-token`+`attestations` permissions, separate test workflow,
  attestation over every published artifact); rejects "sign on
  runner with key in Secrets", "cloud HSM", "skip attestation and
  just trust SHA", "self-hosted runner".

Marked superseded (frontmatter `status: superseded`,
`superseded_by:` pointing to 0007 or v3 design):

- `projects/deploymentbox/designs/release-pipeline-v2-microvm.md`
- `projects/deploymentbox/adr/0001-host-hetzner-nixos.md`
- `projects/deploymentbox/adr/0002-public-ssh-hardened.md`
- `projects/deploymentbox/adr/0003-signing-yubikey-forwarded.md`
  (key-custody contract carries over and is *strengthened*; only the
  SSH-forwarding transport is gone)
- `projects/deploymentbox/adr/0005-build-in-firecracker-microvm.md`
- `projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening.md`

ADR-0004 (tag-driven Central releases, one GPG key, no snapshots,
groupId `no.virtual-architect`, Sonatype Central Portal endpoint)
**remains accepted unchanged** — v3 inherits all of it.

Updated:

- `projects/deploymentbox/index.md` — rewritten for v3 (stack,
  role-in-wiki diagram, ADR list partitioned into accepted-v3 and
  superseded, pages list, out-of-scope, open questions).
- `projects/deploymentbox/wip.md` — overwritten with v3 status
  (blockers shift: namespace TXT still pending, but now also need
  first library `release.yml`, operator-side release script, and
  disposition of `/p/hg/deploymentbox/` staged v2 work).
- `index.md` (top-level) — deploymentbox project row updated
  for v3 stack + status.

Notable observations:

- **Two design pivots inside 24 hours.** v1 was created and
  superseded in the 2026-05-29 session; v2 was created and
  superseded on 2026-05-30. The wiki's
  "preserve-superseded-rather-than-delete" pattern is doing real
  work here — the v2 design + ADRs are the documented starting
  point for any future private-artifact pipeline, and the
  rejected-branches sections in each ADR's "Alternatives
  Considered" preserve the reasoning trail. The cost is six
  superseded ADRs against two accepted ones, but the reasoning is
  fully reconstructible.
- **The "GitHub-hosted runner" rejection in ADR-0001 aged out, not
  was wrong.** ADR-0001's two objections to GitHub runners were
  (a) unpinned toolchain and (b) Secrets-only key custody. The
  flake-pinned toolchain pattern (Volpe) makes (a) moot; sigstore
  attestation lets us *separate* the build from the sign so (b)
  becomes irrelevant. ADR-0007 §Context narrates this explicitly
  so the rejection's history isn't mysterious to future readers.
- **First wiki use of sigstore / SLSA / attestation primitives.**
  Nothing in `tech/decisions/` or `tech/patterns/` mentions
  sigstore or SLSA. If a second project ever adopts a similar
  "CI-built + attested + local-sign" pattern, the promotion
  candidate is something like
  `tech/patterns/ci-attested-local-signed-release.md`. Premature
  with one consumer (the deploymentbox project itself, applied to
  N libraries). Revisit if a non-Maven distribution path (e.g. npm
  for a generated TS package, or container images) ever adopts the
  same shape.
- **Two `release.yml` invariants worth promoting eventually.**
  ADR-0007 commits each library to (a) pinning every `uses:` to a
  commit SHA and (b) splitting `test.yml` (PR-time, no elevated
  permissions) from `release.yml` (tag-triggered, with
  `id-token`+`attestations`). Both are general GitHub Actions
  hygiene; if more projects adopt v3-style pipelines, these become
  candidates for `tech/patterns/github-actions-release-hygiene.md`.

Refs:
[[projects/deploymentbox/designs/release-pipeline-v3-github-attested]],
[[projects/deploymentbox/adr/0007-build-on-github-with-attestations]],
[[projects/deploymentbox/designs/release-pipeline-v2-microvm]]
(superseded),
[[projects/deploymentbox/adr/0001-host-hetzner-nixos]] (superseded),
[[projects/deploymentbox/adr/0005-build-in-firecracker-microvm]]
(superseded),
[[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]]
(load-bearing for the runner-hermeticity argument).

## [2026-05-29] session | end-of-session snapshot — resume tomorrow from here

State of the world at session close. Read this *first* to resume cold;
the entries below it carry the longer decision trace.

### Where we are

- **Wiki:** all v2 design + ADRs + log entries landed.
- **Repo (`/p/hg/deploymentbox/`):** v1 already committed by operator
  (SHA `a978a76` "init"). v2 changes **staged but not committed** —
  8 modified files + 4 new files / directories. See bridge
  [[sources/tmp/code/deploymentbox]] for the exact list.
- **Not yet deployed.** No Hetzner server provisioned. No microVM
  ever booted. No release rehearsed.
- **Not yet flake-evaluated.** No `nix flake check` has run against
  the staged v2 tree. Some errors will surface there before any
  deploy is possible.

### Concrete "tomorrow" picks (in dependency order)

1. **(Trivial blocker) Replace SSH-key placeholder** in
   `modules/release-user.nix:20` with the laptop's ed25519 public
   key. Otherwise no one can log in after deploy.
2. **`nix flake check`** the v2 tree from a Linux machine (or the
   laptop with remote builder). Expect: option-name typos, possibly
   `qemu-bridge-helper`-related warnings from `microvm.host`, and
   firewall + networkd interactions that need a tweak. Iterate
   until clean.
3. **Decide the microVM build-credentials path.** v2 has a known
   gap (called out in `bootstrap.md` §6 and `microvms/build-sandbox/configuration.nix:90`):
   the file `/etc/build-credentials` is sourced inside the microVM
   but not yet declaratively wired. Two acceptable answers:
     - (a) v1-style: small ext4 volume containing only the env
       file, declared in `microvm.volumes`, populated by host at
       install time. Quick.
     - (b) Phase-2-style: sops-nix on the host decrypts at boot and
       a `microvm.shares`-equivalent ships the file in. Cleaner but
       more wiring; Firecracker has *no shares*, so this would
       require a small staging volume anyway.
   Recommended: (a) for now, with a TODO toward (b).
4. **Commit v2** when satisfied with eval. Per personal-repo policy.
5. **Sonatype namespace verification — independent parallel
   track.** Until the DNS TXT on `virtual-architect.no` (via
   uniweb.no) verifies, the final Central upload step in
   `release.sh` will 403. Everything else end-to-end testable
   without it.
6. **First deploy: `nix run .#bootstrap -- root@<hetzner-ip>`.**
   Follow `scripts/bootstrap.md` v2 checklist.
7. **YubiKey ceremony** — orthogonal, can happen before or after
   the box is provisioned. Pre-decision: offline-generate +
   dual-YubiKey backup + offline master + revocation cert.
   *Not yet decided in any ADR* — recorded as open question #1 in
   v2 design doc.
8. **Dry-run release** with an invalid tag against any small
   library. Confirms: job write to MinIO works, microVM boots,
   git can reach github.com via NAT, host detects failure cleanly.

### Known v2 gaps (don't surprise yourself tomorrow)

- microVM build-credentials provisioning not wired (item 3 above).
- Central Portal bundle layout in `release.sh` §7 may need
  smarter zip than `zip -qr` of `m2/`. First real release surfaces
  it — rehearsal step (`bootstrap.md` §10) catches before publish.
- microVM scratch-volume reset is manual (no scheduled cron).
- MinIO credentials are paste-once in v2 (sops-nix is Phase 2).
- Sizing assumes CX32 (4 GiB microVM); CX22 would need
  `microvm.mem` lowered in `microvms/build-sandbox/configuration.nix:34`.

### Open decisions to make tomorrow / soon

| Decision | Where it lives | Why it's open |
|---|---|---|
| YubiKey key ceremony shape | v2 design doc §"Open Questions" #1 | Orthogonal to the box; affects backup story |
| Sops migration timing | v2 design doc §"Secrets map" | Affects bootstrap.md §5, §6, §8 |
| Per-library vs single build microVM | v2 design doc §"Open Questions" #5 | One microVM is fine for v1; revisit on contamination concerns |
| Off-host log shipping | ADR-0006 §"Open Follow-ups" #1 | Needs a log sink; not blocking v2 |

### Wiki / repo cross-reference

- v2 design source of truth:
  [[projects/deploymentbox/designs/release-pipeline-v2-microvm]]
- All six ADRs:
  [[projects/deploymentbox/adr/0001-host-hetzner-nixos]],
  [[projects/deploymentbox/adr/0002-public-ssh-hardened]],
  [[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]],
  [[projects/deploymentbox/adr/0004-tag-driven-central-releases]],
  [[projects/deploymentbox/adr/0005-build-in-firecracker-microvm]],
  [[projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening]]
- Repo bridge (with dirty-state inventory):
  [[sources/tmp/code/deploymentbox]]
- microvm.nix reference: [[microvm.nix/llm-wiki/index]]
- Hardening source: [[sources/summaries/paranoid_nixos_xe_iaso]]

### Parallel tracks (not deploymentbox, but related)

- **Sonatype namespace claim** on `no.virtual-architect`. DNS TXT
  on `virtual-architect.no` via uniweb.no. Discussed in the
  conversation that produced this project; not yet started. Should
  be kicked off before or during tomorrow's session — DNS
  propagation eats hours, do it first.

## [2026-05-29] implement | v2 architecture — Firecracker microVM + MinIO + SHA verify + selected paranoid-NixOS hardening

User explicitly raised the gap left by v1: even with a separate
build host, a malicious dep in any library's flake could execute
on the deploymentbox during `nix develop`/`mill compile` and reach
the host's Nix store, Sonatype token, and gpg-agent. The host *was*
the build environment.

v2 closes that gap by relocating the entire build into a
**Firecracker microVM** (the user's choice of hypervisor for
minimal attack surface — confirmed against
[[microvm.nix/llm-wiki/hypervisors/firecracker]]). The microVM
has no shares, no PCI/USB, TAP-only networking on an internal
bridge. Artifact handoff to the host is over **MinIO** on the
internal bridge; the host downloads, verifies SHA-256 against a
microVM-emitted manifest, then signs (gpg → forwarded YubiKey
socket → laptop) and publishes to Central.

Same session: user pointed at the existing
[[sources/summaries/paranoid_nixos_xe_iaso]] summary. Selected layers
adopted at the host level; tmpfs-root + impermanence deferred with
recorded expiry condition.

Created:

- `projects/deploymentbox/designs/release-pipeline-v2-microvm.md` —
  v2 design (architecture, timing table, secrets map, trade-off
  table revised from v1, file inventory, open questions).
- `projects/deploymentbox/adr/0005-build-in-firecracker-microvm.md` —
  microVM + MinIO + SHA verify decision; rejects nix-sandbox-only,
  systemd-nspawn, cloud-hypervisor (shares are *attack surface*
  here, not a feature), QEMU, vsock-only transport, kernel-cmdline
  job passing.
- `projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening.md` —
  selected layers adopted with modern option names; tmpfs-root +
  impermanence deferred with explicit expiry condition;
  Tailscale-only excepted (already rejected by ADR-0002); off-host
  log shipping deferred.

Updated:

- `projects/deploymentbox/designs/release-pipeline.md` — marked
  `status: superseded`, `superseded_by:` pointing to v2; preserved
  as historical record.
- `projects/deploymentbox/index.md` — stack section, role diagram,
  and ADR list updated for v2.

Repo scaffold extensions at `/p/hg/deploymentbox/`:

- `flake.nix` — `microvm.nix` added as flake input.
- `hosts/deploymentbox/default.nix` — imports new modules.
- `modules/microvm-host.nix` (NEW) — `microvm.host` module, the
  internal `microvm0` bridge, NAT to the external interface, and
  the declarative `microvm.vms.build-sandbox` entry referencing the
  Firecracker config.
- `modules/minio.nix` (NEW) — `services.minio`, bound to the
  internal bridge IP only, hardened systemd unit (`Protect*`,
  `MemoryDenyWriteExecute`).
- `modules/hardening.nix` (NEW) — selected paranoid-NixOS levers
  (auditd execve, `noexec` writable mounts, `defaultPackages = []`,
  `nix.settings.allowed-users = [ "@wheel" ]`, kernel sysctls).
- `modules/release-user.nix` — extended with `minio-client`,
  systemd interaction perms for starting `microvm@build-sandbox`.
- `microvms/build-sandbox/configuration.nix` (NEW) — Firecracker
  microVM NixOS config (rootfs, scratch volume for `/nix/store`,
  TAP interface, on-boot `build-job.service`).
- `microvms/build-sandbox/build-job.sh` (NEW) — the script the
  microVM runs on boot.
- `scripts/release.sh` — rewritten as orchestrator: writes job to
  MinIO, starts microVM, polls for `.done`, downloads, verifies
  SHA, signs, uploads to Central, cleans up.
- `scripts/bootstrap.md` — extended with microVM + MinIO bootstrap
  steps.
- `README.md` — architecture section refreshed.

Notable observations:

- **The microVM closure is itself a derivation.** v2's threat-model
  guarantee depends on the microVM image being reproducibly built
  from the host's `flake.lock`. The Firecracker runner package +
  the guest's NixOS toplevel are both in-tree dependencies; rebuild
  from clean clones gives bit-identical images. This is the
  *load-bearing* property — if the microVM were imperatively
  configured (e.g. installed once and updated by hand), the
  isolation guarantee would erode.
- **MinIO chosen over alternatives.** vsock would give a narrower
  transport but requires custom protocol; virtio-fs would give
  shared `/nix/store` (faster builds) but break the "microVM has
  no host filesystem access" invariant. MinIO over the internal
  bridge is the right balance — standard S3 protocol, bucket-
  scoped credentials, audit logs, and the microVM *only* gets
  put-only on its build-id prefix.
- **First Nix-adjacent normative ADR on supply chain.** No
  `tech/decisions/supply-chain.md` exists yet. If a second project
  ever adopts a similar build-isolation pattern, the candidate
  promotion is something like
  `tech/patterns/microvm-build-isolation.md` — but it's premature
  with one consumer.
- **microvm.nix wiki proved useful in-conversation.** This is the
  first time the external-lib wiki layer was queried mid-design
  rather than after-the-fact. The hypervisor matrix and
  declarative recipe pages let the design walk converge in
  ~5 minutes of reading. Worth noting as evidence the layer-3
  external wikis pay off — the alternative would have been
  re-reading the upstream handbook from scratch.

Refs:
[[projects/deploymentbox/designs/release-pipeline-v2-microvm]],
[[projects/deploymentbox/adr/0005-build-in-firecracker-microvm]],
[[projects/deploymentbox/adr/0006-adopt-paranoid-nixos-hardening]],
[[sources/summaries/paranoid_nixos_xe_iaso]],
[[microvm.nix/llm-wiki/hypervisors/firecracker]],
[[microvm.nix/llm-wiki/recipes/declarative]],
[[microvm.nix/llm-wiki/recipes/advanced-network]]

## [2026-05-29] ingest | Project registered, scaffold staged

Project introduced in conversation 2026-05-29 alongside the open-source
publishing-pipeline discussion for `no.virtual-architect` libraries.
The user's threat model — laptop compromise as a supply-chain vector
— motivates a separate, clean build environment. Hetzner Cloud was
chosen over self-hosted runners, GitHub-hosted runners, and other
clouds. NixOS was chosen for declarative reproducibility (matches the
user's stack).

Created:

- `projects/deploymentbox/index.md`
- `projects/deploymentbox/designs/release-pipeline.md` — end-to-end
  architecture; source of truth for the host's purpose.
- `projects/deploymentbox/adr/0001-host-hetzner-nixos.md`
- `projects/deploymentbox/adr/0002-public-ssh-hardened.md`
- `projects/deploymentbox/adr/0003-signing-yubikey-forwarded.md`
- `projects/deploymentbox/adr/0004-tag-driven-central-releases.md`
- `sources/tmp/code/deploymentbox.md` — bridge staged for promotion
  to `sources/raw/code/` once the human makes the initial commit.

Repo scaffold staged at `/p/hg/deploymentbox/` (flake + modules +
release script + README + `.gitignore`). Per the personal-repo commit
policy, `git init` and the first commit are the human's call; the
bridge stays at `commit: uninitialized-tree` until then.

Notable observations:

- **First wiki-managed infra project.** Prior `/p/hg/` projects are
  all libraries. `deploymentbox` is the first project whose unit of
  delivery is a running host, not an artifact. The wiki schema
  carries `kind: project` for all of them uniformly — the ADRs name
  decisions, the design doc names architecture, the project page
  names current state.
- **No tech-layer normative counterparts.** Unlike the library
  ingests (which routinely adopt or deviate from
  [[tech/decisions/deps-single-file]] and the pattern pages), all
  four ADRs here record project-internal architectural choices that
  have no existing global counterpart. None of the choices feel
  ready for promotion: a single project with one host is one data
  point. If a second deploy-style project lands (e.g. a per-customer
  release host, or a separate company-software box), a synthesis
  could surface what's common.
- **Conversation-derived decision history.** The four ADRs trace the
  conversational walk through the architecture options
  (laptop-only → GitHub-hosted → self-hosted VPS → NixOS build host
  with YubiKey forwarding). Each ADR's "Alternatives Considered"
  section preserves the rejected branches so future revisits can
  resume from current state, not zero.
- **YubiKey-not-on-the-box is load-bearing.** The whole supply-chain
  argument collapses if the signing key ever sits in the box's
  filesystem or in a GitHub Secret. The architecture is *only*
  defensible because the key lives in hardware on the operator's
  desk and never traverses the network in plain form. ADR-0003
  records this contract explicitly so a future "just put the key on
  the server, it'd be easier" suggestion has a written ground to
  argue against.

Refs: [[projects/deploymentbox/index]],
[[projects/deploymentbox/designs/release-pipeline]],
[[projects/deploymentbox/adr/0001-host-hetzner-nixos]],
[[projects/deploymentbox/adr/0002-public-ssh-hardened]],
[[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]],
[[projects/deploymentbox/adr/0004-tag-driven-central-releases]],
[[sources/tmp/code/deploymentbox]],
[[sources/summaries/github_actions_nix_cachix_dhall_gvolpe]] (closest
prior reference; informed the "GitHub Actions for tests only, build
elsewhere" posture).
