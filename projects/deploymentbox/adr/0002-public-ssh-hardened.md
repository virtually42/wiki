---
id: deploymentbox-adr-0002
title: Public SSH on port 22, key-only, hardened, no VPN layer
kind: normative
status: superseded
superseded_by: projects/deploymentbox/adr/0007-build-on-github-with-attestations.md
project: deploymentbox
created: 2026-05-29
compliance:
  adopts: []
  exceptions: []
  deviations: []
  ignores: []
supersedes: []
---

## Context

The deploymentbox must be reachable from the operator's laptop at
release time so the release script can be invoked over SSH with
gpg-agent socket forwarding (per
[[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]]).

Options for SSH reachability:

- **Public SSH on port 22.** Standard. SSH is exposed to the
  internet; access controlled by SSH key auth and login restrictions.
- **WireGuard-only SSH.** SSH listens only on a private interface
  reachable through a WireGuard tunnel. The internet sees only UDP
  on the WireGuard port. Tighter attack surface; one more piece to
  maintain on every laptop / device.
- **Tailscale / managed mesh VPN.** Similar to WireGuard but with
  managed key distribution; third-party control plane.
- **IP allowlist on a cloud firewall.** SSH on port 22 but only from
  the operator's home / office IPs. Cheap; fragile against IP
  changes.

The operator is one person, releasing sporadically, from a laptop
they control. The threat model targets supply-chain compromise of
the *build environment* and *signing keys*, not surveillance of
which IPs SSH to a build box.

## Decision

Run SSH on **public port 22**, accept only **key-based auth** for a
single non-root user (`release`), and enforce the following hardening:

```nix
services.openssh = {
  enable = true;
  settings = {
    PasswordAuthentication = false;
    PermitRootLogin = "no";
    KbdInteractiveAuthentication = false;
    StreamLocalBindUnlink = "yes";    # required for gpg-agent forwarding
    AllowUsers = [ "release" ];
    X11Forwarding = false;
    AllowAgentForwarding = "yes";     # GPG socket forwarding needs this
    AllowTcpForwarding = "yes";       # only for explicit -R / -L usage
    LoginGraceTime = "30s";
    MaxAuthTries = 3;
  };
};

services.fail2ban = {
  enable = true;
  bantime = "1h";
  maxretry = 3;
};

networking.firewall = {
  enable = true;
  allowedTCPPorts = [ 22 ];
  allowedUDPPorts = [ ];
};
```

`StreamLocalBindUnlink yes` is the line that matters for the signing
flow: it lets a subsequent SSH session reclaim the forwarded
gpg-agent socket path. Without it, the second release of the day
silently fails to forward.

## Consequences

- **Standard well-understood posture.** SSH-only-public, key-only,
  fail2ban: this is the default profile every NixOS guide
  describes. Easy to reason about, easy to audit, easy to recover
  from missteps.
- **No extra software on the laptop.** No WireGuard tunnel to bring
  up before releasing. SSH works from anywhere with network access.
- **Acceptable attack surface.** Public SSH with key-only auth +
  fail2ban + `AllowUsers` + `MaxAuthTries 3` is robust against
  bulk-scan brute force. The residual risks are: (a) a zero-day in
  OpenSSH itself (rare, patched fast on NixOS via channel updates);
  (b) the operator's SSH key compromise (mitigated by separate ssh
  key from the GPG key; rotatable).
- **Compromise consequences are bounded** (per the design doc's open
  question #5): the box holds the Sonatype token (rotatable) and
  release-user filesystem. Signature forgery is not possible because
  the GPG key is not present.

## Alternatives Considered

- **WireGuard-only SSH.** Considered. Rejected for v1: adds
  WireGuard config to every device the operator wants to release
  from, plus a fallback story for "what if I lose access to my
  WireGuard config." For one operator with one laptop, the threat
  reduction (no SSH on the open internet) is not worth the
  per-device burden. **Revisit if:** the operator gains a fleet of
  laptops, ssh-from-anywhere becomes a *negative* (e.g. travel
  threat models), or fail2ban telemetry shows persistent targeted
  attacks (unlikely on a fresh Hetzner IP).
- **Tailscale.** Same rejection logic as WireGuard, plus introduces
  a managed third-party identity plane. Out of scope.
- **Cloud firewall IP allowlist.** Considered. Fragile: home IPs
  change, mobile networks rotate. Doesn't usefully add to fail2ban
  + key-only. Not adopted.
- **Move SSH off port 22.** Cosmetic; scanners hit every port. Adds
  confusion (operator has to remember the port) without measurable
  benefit.
- **Disable SSH entirely, manage via Hetzner web console.** Loses
  gpg-agent socket forwarding (the web console is a VNC framebuffer
  — no port forwarding). Defeats the architecture's signing flow.

## Links

- [[projects/deploymentbox/designs/release-pipeline]]
- [[projects/deploymentbox/adr/0001-host-hetzner-nixos]]
- [[projects/deploymentbox/adr/0003-signing-yubikey-forwarded]] —
  the signing flow depends on `StreamLocalBindUnlink yes` + agent
  forwarding being enabled in this ADR
