---
id: summary-paranoid-nixos-xe-iaso
title: Xe Iaso — Paranoid NixOS Setup (2021-07-18)
kind: descriptive
status: accepted
scope: global
created: 2026-05-29
updated: 2026-05-29
confidence: medium
tags_extended: [defense-in-depth, hardening, impermanence, audit]
sources:
  - sources/tmp/paranoid_nixos_xe_iaso.md
  - https://xeiaso.net/blog/paranoid-nixos-2021-07-18/
provenance:
  upstream_author: Xe Iaso
  upstream_url: https://xeiaso.net/blog/paranoid-nixos-2021-07-18/
  upstream_kind: personal-blog-post
  upstream_publication_date: 2021-07-18
  introduced_to_wiki_by: user
  confirmed_at: 2026-05-29
tags: [nixos, security, hardening, impermanence, tmpfs-root, systemd, audit, tailscale, noexec, infra]
---

## Source

A single long-form blog post by Xe Iaso laying out a "paranoid" NixOS
host configuration. The post composes seven discrete hardening
layers — firewall, VPN-only SSH, per-service users, systemd `Protect*`
flags, restricted `nix.allowedUsers`, tmpfs-root / impermanence, and
`noexec` on every mount except `/nix/store` — plus auditd, off-host
log shipping, and several optional teardowns (rip out `sudo`, strip
default packages, restrict sshd, install ClamAV as a PCI
checkbox). The author is a Tailscale employee; the disclaimer notes
Tailscale did not review the post. See raw extraction at
[[sources/tmp/paranoid_nixos_xe_iaso.md]].

Date is 2021-07-18, so the upstream artefacts (`nixos-21.05`
channel, `nix.allowedUsers`, `passwordAuthentication`,
`challengeResponseAuthentication`) reflect that vintage of NixOS.
See §Staleness below.

## What this source teaches

### A defense-in-depth philosophy stated up front

The author's framing is unusually explicit and re-readable:

> "The goal here isn't to make the system attack-proof, nothing is.
> The goal is to annoy the attacker enough that they give up."

This translates into a concrete posture that bounds *what each
layer is asked to do*:

| Layer | Worst-case assumption | What this layer adds |
|-------|------------------------|----------------------|
| Firewall | Network reachable | Reject everything not whitelisted |
| Tailscale | SSH must exist | Make it invisible to the public Internet |
| Per-service users | Service exploited | Blast radius bounded by Unix UID |
| systemd `Protect*` | Process compromised | Kernel-visible surface shrunk per-service |
| `nix.allowedUsers` | User shell achieved | Compiler / scripting toolchain unreachable |
| tmpfs root + impermanence | Disk modified | Modifications evaporate on reboot |
| `noexec` everywhere but `/nix/store` | Binary smuggled in | Cannot execute outside content-addressed store |
| auditd + off-host logs | Attack succeeded | Loud evidence, off the box before tampering |

Each row is intentionally weaker than "prevention" — the post
treats prevention as a layer-stack, not an event.

### Concrete NixOS levers worth naming

The post is dense with specific options. The high-leverage ones:

- `services.tailscale.enable` + `networking.firewall.trustedInterfaces = [ "tailscale0" ]` — the "make SSH invisible" pair.
- `nix.allowedUsers = [ "@wheel" ]` (or `[ "root" ]`) — closes off compilers/scripting to non-admin shells.
- `security.auditd.enable = true; security.audit.enable = true;` + an `execve` rule — minimum-viable execution log.
- `environment.persistence."/nix/persist".directories = [ ... ]` — impermanence as the canonical "what survives reboot" declaration.
- `environment.etc."ssh/ssh_host_*_key".source = "/nix/persist/etc/ssh/..."` — the SSH host-key carve-out impermanence forces (otherwise sshd cannot generate keys).
- `fileSystems."/" .options = [ "noexec" ]` family — the last layer of the onion.
- `environment.defaultPackages = lib.mkForce [];` — even nano/perl/rsync are surface area worth removing on hardened servers.

### Impermanence as a security feature, not a tidiness feature

The post frames tmpfs-root + impermanence as a security
posture: "persistence is opted into, not opted out of." The
practical effect is that an attacker who modifies anything outside
the explicit persistence list loses their changes on the next boot;
combined with `noexec` on the tmpfs, the set of places an attacker
can write *and* execute drops to "running service memory" only.

This is a useful reframing — most impermanence material treats it as
config-hygiene. Here it's an explicit limit on attacker dwell-time.

### Audit-first execution monitoring

The single audit rule `-a exit,always -F arch=b64 -S execve`
captures every program launch, kernel-level. Combined with
off-host log shipping and the `noexec`-on-non-store invariant,
"any execve where the path is not under `/nix/store`" becomes a
high-signal alert. The author doesn't write the detection rule
itself but names the design pattern.

### The PCI ClamAV trick is a clue, not a recommendation

> "PCI Compliance requires you to have an antivirus program
> installed on every server. It doesn't say anything about the
> program _running_, but just it being installed is enough."

Reading this as snark misses the point: the post is hinting that a
serious hardening posture should know which compliance items are
genuinely load-bearing and which are paper. That distinction is
worth carrying into any future `tech/decisions/` work on
infrastructure compliance.

## What this source does *not* teach

- **Flakes.** Pre-flake era. `NIX_PATH` is used to wire in
  impermanence; a modern flake-based setup would import the
  impermanence flake module and pin via `flake.lock`.
- **Secrets management.** No `sops-nix`, `agenix`, or systemd
  credentials. The `services.openssh.passwordAuthentication = false`
  hardening is here, but how to ship private TLS material, DB
  passwords, or API tokens into a tmpfs-rooted box is unaddressed.
  The post's "central management system such as morph or nixops"
  hint is the only gesture in that direction.
- **Backup / restore strategy for `/nix/persist`.** The entire
  persistence layer lives in one directory; the post does not say
  how to snapshot or restore it. For a paranoid posture this is a
  conspicuous omission — the persistence dir is exactly what an
  attacker *wants* to corrupt before forcing a reboot.
- **Container / VM workloads.** No mention of `systemd-nspawn`,
  containers, or microvms. The `noexec` posture interacts oddly
  with containerised payloads (their rootfs would need to live in
  `/nix/store` or on an exec-allowed mount).
- **Threat model boundaries.** The post is implicit about who the
  attacker is. The setup is well-shaped for "remote service
  exploitation by an opportunistic attacker" and "drive-by container
  escape." It is less well-shaped for "insider with shell" (which
  the `nix.allowedUsers = [ "root" ]` knob acknowledges but does not
  fully address) or "supply chain compromise of `nixpkgs`" (which
  channel-pinning to `nixos-21.05` actively worsens — see Staleness).
- **Detection / response.** auditd records execve; nothing says
  who reads the logs, what triggers a page, or what runbook fires.
  The "send all logs off-machine" framing is normative but
  unimplemented.
- **`/boot` integrity.** Secure boot, measured boot, dm-verity, TPM
  attestation — none of these are addressed. An attacker with
  physical or `/boot` write access can subvert the entire
  tmpfs-root model on the next reboot.
- **Build-time supply chain.** With `nix.allowedUsers = [ "root" ]`
  the Nix daemon becomes a sharply-bounded interface, but the
  derivations themselves are still trusted as-is. Reproducible
  builds, content-addressed derivations, or
  `nix-build --check` verification are not discussed.

## Staleness notes (important — the post is from 2021)

Several options the post uses have shifted in modern NixOS:

| Post (2021 / nixos-21.05) | Modern equivalent (2026) |
|---------------------------|---------------------------|
| `nix.allowedUsers` | `nix.settings.allowed-users` |
| `services.openssh.passwordAuthentication = false` | `services.openssh.settings.PasswordAuthentication = false` |
| `services.openssh.challengeResponseAuthentication = false` | `services.openssh.settings.KbdInteractiveAuthentication = false` |
| `NIX_PATH=` + tarball URL for impermanence | impermanence as a flake input |
| `nixos-21.05` channel pin | `nixos-25.05` (or current stable) flake pin |

A future wiki guide derived from this source would need to
re-validate every option name against current NixOS rather than
copy the post's syntax verbatim. The *shape* of the design (tmpfs
root, `noexec`, audit-everything) survives; the *option names*
mostly do not.

## Relationship to current wiki state

The wiki has no NixOS hardening surface in the tech layer yet:

- No `tech/guides/nixos-*.md`
- No `tech/decisions/` on host hardening
- No `tech/patterns/defense-in-depth.md` or similar

It does, as of 2026-05-29, have a concrete consumer: the
**deploymentbox** project ([[projects/deploymentbox/index]]) — a
hardened NixOS host on Hetzner Cloud whose role is to build and
sign Maven Central artifacts. Several of the paranoid-NixOS levers
are directly relevant to that project:

- `services.openssh.settings.PasswordAuthentication = false` etc.
  — adopted in [[projects/deploymentbox/adr/0002-public-ssh-hardened]]
  (modernised option names; see Staleness table).
- Per-service users, `nix.settings.allowed-users` restriction,
  auditd execve logging — **plausibly applicable but not yet
  adopted by deploymentbox ADRs.** Worth surfacing.
- Tailscale-only SSH — **explicitly rejected** by
  [[projects/deploymentbox/adr/0002-public-ssh-hardened]] (one
  operator, one laptop, no fleet). The "VPN for Access" layer of
  the post does not transfer to deploymentbox.
- tmpfs root + impermanence + `noexec` everywhere but `/nix/store`
  — not addressed by current deploymentbox ADRs. Worth surfacing as
  an open consideration. The deploymentbox is the textbook target
  for this posture (single-purpose host, persistent state is
  small and explicit).

This is the second Nix-adjacent source in the wiki, after
[[sources/summaries/nix_dev_ci_github_actions.md]] (which covers
the *build* side — Cachix + GHA). The pair sits naturally as
"build-time integrity" (Cachix recipe) and "runtime
posture" (this post). The deploymentbox project sits between them
as the concrete artefact that would benefit from both.

Adjacent wiki material:

- [[projects/deploymentbox/index]] — concrete consumer; this
  summary should be re-visited when deploymentbox progresses past
  v1 and the "harden further?" question opens.
- [[projects/deploymentbox/adr/0002-public-ssh-hardened]] — already
  adopts the SSH-hardening layer of this post (with modern option
  names).
- [[sources/summaries/nix_dev_ci_github_actions.md]] — covers
  build-side supply chain (Cachix signing, channel pinning critique).
- [[sources/summaries/github_actions_nix_cachix_dhall_gvolpe.md]] —
  the per-library "nix develop --command mill" pattern; the
  build-side analogue.

## Promotion candidacy

| Candidate page | Status | Reasoning |
|----------------|--------|-----------|
| `tech/guides/paranoid-nixos.md` | **deferred** | A descriptive how-to is admissible from one source, but every option name needs re-validation against current NixOS. The deploymentbox project is a candidate consumer but is still at v1 / minimum-viable hardening; a guide written now would either pre-empt its decisions or document only its current scope. Revisit once deploymentbox has a second hardening pass or a second NixOS host lands. |
| `tech/patterns/defense-in-depth.md` | **deferred** | The "layer-stack with bounded responsibilities" framing is genuinely pattern-shaped and could be promoted, but a single source on a single platform is thin evidence. Hold for a second corroborating source (e.g. an OpenBSD or distroless-container piece) before authoring. |
| `tech/patterns/impermanence-as-security.md` | **deferred** | Same single-source caveat. The reframing of impermanence from tidiness to security is worth carrying, but needs project-side evidence to elevate. |
| `tech/stack/nixos.md` | **deferred** | Premature without a project using NixOS on disk. Both Nix-related summaries to date describe upstream patterns, not in-repo usage. |
| `tech/decisions/*.md` | **not a candidate** | Nothing here rises to an organisational obligation until a project actually adopts NixOS. |

The page is therefore **accepted as a reference summary** without
promotion. When the `infra` project activates, revisit and consider
authoring a hardening guide that cites this summary plus the
nix.dev CI recipe as paired build-time / runtime references.

## Open questions left for the next ingest / project anchor

1. **Modern option-name mapping.** A short translation table from
   2021 NixOS options to current ones would be valuable. Deferred
   until needed by a real host config.
2. **Secrets-on-tmpfs.** How should `sops-nix` / `agenix`
   interact with `/nix/persist`? Are secret files persisted in
   `/nix/persist` and decrypted into the tmpfs root, or rendered
   straight into systemd credential dirs? Unaddressed here.
3. **Backup / restore for `/nix/persist`.** What is the canonical
   way to snapshot the persistence dir? ZFS snapshots are an
   obvious answer the post explicitly rejects ("keep the scary
   production servers as boring and vanilla as possible").
4. **`/boot` integrity.** Does the paranoid posture extend to
   secure boot, lanzaboote, or TPM-measured boot? Not covered.
5. **Build-time supply chain.** Reproducible / content-addressed
   derivations, `flake.lock` discipline, signed substituters —
   how do these compose with the runtime hardening described
   here? Bridges naturally to
   [[sources/summaries/nix_dev_ci_github_actions.md]].
6. **Detection-side runbook.** What does `journalctl -f` actually
   route to? An off-host log destination, alert routing, and
   runbook are mentioned in spirit but never implemented.
7. **Container / microvm fit.** How does the `noexec` invariant
   coexist with services that ship as containers or microvms?
   Open until a project demands an answer.

## Links

- [[sources/tmp/paranoid_nixos_xe_iaso.md]] — raw extraction (staged)
- [[sources/summaries/nix_dev_ci_github_actions.md]] — neighbouring Nix source on build-side integrity
- [[index]] §Projects — `infra` (planned), the likely consumer
