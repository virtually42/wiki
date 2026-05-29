---
id: option-forward-ports
title: "microvm.forwardPorts"
category: option
layer: core
tags: [forwardPorts, slirp, port-forwarding, user-networking]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface:
  - microvm.forwardPorts
related: [option-interfaces, hypervisor-qemu]
see_also: []
---

## Shape

```nix
microvm.forwardPorts = [
  # Local host:2222 -> guest:22 (ssh into VM)
  { from = "host"; host.port = 2222; guest.port = 22; }

  # Guest sees host:80 forwarded to 10.0.2.10:80 in the VLAN
  { from = "guest";
    guest.address = "10.0.2.10"; guest.port = 80;
    host.address  = "127.0.0.1"; host.port  = 80;
  }
];
```

Submodule fields:

- `from` — `"host"` or `"guest"`; controls direction.
- `proto` — `"tcp"` or `"udp"`.
- `host.address`, `host.port` — host-side endpoint.
- `guest.address`, `guest.port` — guest-side endpoint.

## When It Applies

Only when using **SLiRP user networking** (`type = "user"`
interfaces) on qemu. The interface type that supports `forwardPorts`
is restricted by the underlying hypervisor:

- qemu: ✓
- vfkit: user networking is supported but `forwardPorts` is **not**
  honoured by the vfkit runner; use `vfkit.extraArgs` or attach a
  proxy in the guest.
- kvmtool: user networking has no DHCP; static IP required.

## Caveats

- Guest firewall must open the forwarded port (the option description
  carries the warning).
- qemu's user networking only supports **IPv4** forwarding.
- Once you're past user-mode networking and onto TAP / bridge, port
  forwarding becomes a host-side concern — use
  `networking.nat.forwardPorts` on the host. See
  [[recipe-advanced-network]].
