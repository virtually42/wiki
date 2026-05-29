---
id: deploymentbox-adr-0006
title: Adopt selected hardening from Iaso's Paranoid NixOS, defer the rest
kind: normative
status: accepted
project: deploymentbox
created: 2026-05-29
compliance:
  adopts:
    - sources/summaries/paranoid_nixos_xe_iaso.md
  exceptions:
    - layer: tailscale-only-ssh
      reason: |
        One operator, one laptop. The SSH posture is already public
        (port 22 with key-only auth, fail2ban, `AllowUsers`) per
        [[projects/deploymentbox/adr/0002-public-ssh-hardened]].
        Adding Tailscale would force VPN setup on every laptop the
        operator wants to release from with no measurable threat
        reduction over the existing hardening.
    - layer: per-service-users
      reason: |
        The only meaningful services on the box are sshd
        (system-user `sshd`), MinIO (NixOS module's own `minio`
        user), and the microvm runners (microvm.nix's `microvm`
        system-user, in the `kvm` group). The release-time
        invocations run as `release`. We already have a per-service
        user pattern by adopting upstream NixOS modules; no further
        carving up is needed.
  deviations:
    - layer: tmpfs-root + impermanence
      rationale: |
        High-leverage in principle — see Iaso §"Impermanence as a
        security feature, not a tidiness feature". Defer for v1:
        impermanence is an invasive root-filesystem change that
        requires a careful inventory of "what survives reboot"
        (SSH host keys, MinIO bucket contents, Sonatype token,
        `release` user's `~/.mill/credentials.json`). The
        deploymentbox's persistent surface is currently small
        enough that a clean reinstall via `nixos-anywhere` is
        cheaper than the impermanence ceremony. Revisit when the
        box accrues more state or a second hardening pass is
        triggered.
      severity: medium
      expiry_condition: |
        Either (a) a second NixOS infra project lands and we
        can amortise the impermanence pattern across both, or
        (b) a credible threat appears that an attacker would
        gain persistence on the box across a reboot.
    - layer: lanzaboote / secure-boot / measured-boot
      rationale: |
        Iaso doesn't address it but the staleness note in the
        summary flags it as a gap. Hetzner Cloud doesn't (as of
        2026-05-29) expose TPM or measured-boot primitives in the
        guest, so the practical surface is limited.
      severity: low
      expiry_condition: When the host moves off cloud (e.g. self-managed hardware).
  ignores: []
supersedes: []
---

## Context

The wiki ingested Xe Iaso's "Paranoid NixOS Setup" (2021-07-18)
earlier on 2026-05-29 ([[sources/summaries/paranoid_nixos_xe_iaso]]).
The summary catalogues eight defense-in-depth layers and notes the
deploymentbox project as the most plausible immediate consumer.

This ADR records which layers the deploymentbox adopts for v1, with
explicit modern option names (the original post uses 2021-era
NixOS API that has since shifted — the summary's "Staleness notes"
table is the source of truth for the option-name modernisation).

The pairing is with
[[projects/deploymentbox/adr/0005-build-in-firecracker-microvm]] —
the microVM isolation closes the *build-time* threat surface; this
ADR closes residual *runtime* host hardening.

## Decision

The deploymentbox adopts the following layers from Iaso's post, with
the noted modernisations:

### 1. SSH hardening — *already adopted* in ADR-0002

Listed for completeness. See
[[projects/deploymentbox/adr/0002-public-ssh-hardened]].

### 2. Restricted `nix.settings.allowed-users`

```nix
nix.settings.allowed-users = [ "@wheel" ];
```

After ADR-0005 lands, the `release` user no longer invokes `nix`
directly — `nix develop` runs inside the microVM. The release user
is not in `wheel`. Restricting nix-daemon access to wheel members
(effectively: root only, since no one else is in wheel) removes
the compiler / scripting toolchain as a privilege-escalation
surface for any process running as `release`.

### 3. auditd execve logging

```nix
security.auditd.enable = true;
security.audit.enable = true;
security.audit.rules = [
  "-a exit,always -F arch=b64 -S execve"
];
```

Every `execve` syscall is logged kernel-side to
`/var/log/audit/audit.log`. Combined with the box's small
expected-process catalog (sshd, MinIO, microvm runners, release.sh
+ its callees), an unexpected execve is high-signal.

Off-host log shipping is *deferred* — see "Open follow-ups". For
v1, audit logs stay on the box. The release script can scrape
them on each release if useful, but the active detection workflow
is out of scope here.

### 4. `noexec` on writable mounts

```nix
fileSystems."/tmp".options = [ "noexec" "nosuid" "nodev" ];
fileSystems."/var".options = [ "noexec" "nosuid" "nodev" ];
fileSystems."/home".options = [ "noexec" "nosuid" "nodev" ];
```

The root filesystem itself stays exec-capable because systemd /
nix binaries live in `/nix/store`. The post's *full* invariant
("noexec everywhere but `/nix/store`") requires impermanence,
which is deferred per "Deviations". This partial adoption still
catches the common case: a payload dropped in `/tmp`, `/var/tmp`,
or a writable home directory cannot execute.

**Caveat:** the MinIO data directory under `/var/lib/minio`
inherits `noexec`. MinIO writes binary objects to disk but does
not execute them — should not regress.

### 5. `environment.defaultPackages = [ ]`

```nix
environment.defaultPackages = lib.mkForce [ ];
```

Strips perl, rsync, nano, less, etc. from the system closure.
What we explicitly install (`git`, `curl`, `gnupg`,
`pinentry-curses`, `jq`, `minio-client`) is exactly what we want.
Anything else has to be added explicitly — a useful forcing
function against accidental surface accumulation.

### 6. Documentation off

```nix
documentation.enable = false;
documentation.nixos.enable = false;
```

Already set in v1 (default.nix). Iaso lists it as a hardening
item; we kept it for closure-size reasons originally but it
serves both purposes.

### 7. systemd `Protect*` on long-running services

Applied to `services.minio` (the only long-running service we
add beyond NixOS upstream defaults):

```nix
systemd.services.minio.serviceConfig = {
  ProtectSystem = "strict";
  ProtectHome = true;
  PrivateTmp = true;
  PrivateDevices = true;
  NoNewPrivileges = true;
  ProtectKernelTunables = true;
  ProtectKernelModules = true;
  ProtectControlGroups = true;
  RestrictAddressFamilies = [ "AF_UNIX" "AF_INET" "AF_INET6" ];
  RestrictRealtime = true;
  RestrictNamespaces = true;
  LockPersonality = true;
  MemoryDenyWriteExecute = true;
  SystemCallArchitectures = "native";
  ReadWritePaths = [ "/var/lib/minio" ];
};
```

Upstream NixOS already sets sensible defaults for `services.minio`;
this layers extras. sshd's upstream module is already strongly
hardened — no additional `Protect*` flags applied there.

### 8. Strip kernel attack surface where cheap

```nix
boot.kernel.sysctl = {
  "kernel.dmesg_restrict" = 1;
  "kernel.kptr_restrict" = 2;
  "kernel.yama.ptrace_scope" = 2;
  "net.ipv4.conf.all.send_redirects" = 0;
  "net.ipv4.conf.default.send_redirects" = 0;
  "net.ipv4.conf.all.accept_redirects" = 0;
  "net.ipv6.conf.all.accept_redirects" = 0;
};
```

Standard cheap-wins sysctls.

## Consequences

- **No semantic change for the release flow.** `release.sh` still
  works the same way; the additions are passive controls
  (logging, restricted exec, kernel hardening).
- **Audit log volume.** Every `execve` produces a line. On a quiet
  build box this is fine; if it ever grows noisy, `auditctl` lets
  us narrow the rule. Logrotate is on by default.
- **`release` user cannot run `nix` ad-hoc.** Operator-side
  troubleshooting that worked before (e.g. `ssh release@box;
  nix-shell -p sometool`) now fails. The intended escape hatch is
  `ssh release@box; sudo -i` — but `release` isn't in `wheel`,
  so this also fails. For real emergencies, use the Hetzner web
  console as root. This matches the v1 ADR-0002 posture and is a
  deliberate friction-as-defense choice.
- **`noexec` may break ad-hoc scripts dropped in `/tmp`.** The
  microVM build flow doesn't use the host's `/tmp`; it's
  microVM-local. The host's release.sh writes its tmpdirs under
  `/var/lib/deploymentbox/work` (also noexec). No script there
  is expected to be executed directly — `gpg`, `mc`, `curl`, and
  Mill artifacts are data, not executables.
- **Hardening is partial.** The tmpfs-root + impermanence layer
  is the post's most powerful idea and we're not adopting it
  yet. Recorded as a deviation with an explicit expiry
  condition.

## Alternatives Considered

- **Adopt impermanence in v1.** Considered. Rejected for the
  reasons listed under §"Deviations" — invasive change for
  marginal gain at v1 scale.
- **Tailscale-only SSH.** See §"Exceptions". One-operator one-
  laptop scale doesn't justify it.
- **Skip auditd, use journald only.** Rejected: journald is good
  for service logs but doesn't catch kernel-level execve. The
  marginal cost of auditd is negligible.
- **Skip noexec.** Rejected: cheap defense, occasionally useful,
  no observed friction in v2 design.

## Open Follow-ups

1. **Off-host log shipping.** Iaso recommends shipping audit
   logs off the host so an attacker who gains root can't tamper
   with the evidence. Not adopted in v1 (no second host to ship
   to, no log-sink infrastructure). Tracked as a v2-or-later
   addition if a logging stack ever lands in the infra project.
2. **Impermanence.** Deferred per §"Deviations". The expiry
   condition is recorded; reopen this ADR when triggered.
3. **`/boot` integrity / measured boot.** Hetzner Cloud doesn't
   currently expose the primitives. If the box ever moves to
   self-managed hardware (per ADR-0001 §"Alternatives"), revisit.
4. **MinIO bucket access policies.** The release user has full
   bucket access; the microVM has prefix-scoped put-only. This
   ADR doesn't enumerate the IAM policies — that lives in
   `modules/minio.nix`. If we ever add a second microVM
   (e.g. a Scala Native cross-compile box), revisit to ensure
   per-microVM scoping.

## Links

- [[sources/summaries/paranoid_nixos_xe_iaso]] — source of truth
  for the layered model and the option-name staleness notes.
- [[projects/deploymentbox/adr/0002-public-ssh-hardened]] — SSH
  layer already adopted.
- [[projects/deploymentbox/adr/0005-build-in-firecracker-microvm]]
  — paired build-time isolation; this ADR is the runtime-side
  complement.
- [[projects/deploymentbox/designs/release-pipeline-v2-microvm]] —
  v2 design.
