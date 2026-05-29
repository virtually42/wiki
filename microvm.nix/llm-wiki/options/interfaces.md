---
id: option-interfaces
title: "microvm.interfaces"
category: option
layer: core
tags: [interface, network, tap, macvtap, bridge, user, vhost-net]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/interfaces.nix
  - /p/gh/microvm.nix/doc/src/interfaces.md
source_commit: 0d49083
api_surface:
  - microvm.interfaces
related: [recipe-simple-network, recipe-advanced-network, recipe-routed-network, recipe-vhost-net]
see_also: [option-forward-ports]
---

## Shape

```nix
microvm.interfaces = [{
  type = "tap";          # "user" | "tap" | "macvtap" | "bridge"
  id   = "vm-myvm-0";    # host interface name (or guest in `user`)
  mac  = "02:00:00:00:00:01";
  # Type-specific:
  macvtap.link = "eth0";
  macvtap.mode = "bridge";  # private|vepa|bridge|passthru|source
  bridge       = "br0";
  tap.vhost    = false;     # qemu only
}];
```

## Types

| Type | Hypervisor support | Notes |
|---|---|---|
| `user` | qemu, kvmtool, vfkit | SLiRP NAT, no host setup. kvmtool needs static guest IP. Only IPv4 port-forwarding |
| `tap` | qemu, CHV, firecracker, crosvm, kvmtool, stratovirt, alioth | Host must create the TAP device; host module does this via `microvm-tap-interfaces@.service`. `tap.vhost = true` only on qemu |
| `macvtap` | qemu, CHV | Attaches to a host NIC with a separate MAC. Bypasses any host bridge |
| `bridge` | qemu | qemu creates the TAP and attaches to a host bridge via `qemu-bridge-helper`. qemu runs without sandbox |

The runner files (`lib/runners/*.nix`) `throw` on unsupported
combinations — e.g. firecracker rejects anything but `tap`, vfkit
rejects anything but `user`.

## `tap.vhost`

```nix
{ type = "tap"; id = "vm-a1"; mac = "02:..."; tap.vhost = true; }
```

Enables `vhost-net` kernel offload in qemu. ~10 Gbps vs ~1.5 Gbps for
userspace TAP. Needs `vhost_net` module loaded on the host (the
`host` module sets `boot.kernelModules = ["tap" "vhost_net"]`). Only
supported by the qemu runner.

## Host Setup

- **TAP**: `sudo ip tuntap add $IFACE_NAME mode tap user $USER`.
  Under the host module this happens via
  `microvm-tap-interfaces@.service`, which runs the runner's
  `bin/tap-up`.
- **MACVTAP**: `sudo ip l add link $LINK name $ID type macvtap mode
  bridge`, then `chown $USER /dev/tap$IFINDEX`. Host module covers
  this via `microvm-macvtap-interfaces@.service`.
- **bridge**: needs `/etc/qemu/bridge.conf` allowing your bridges
  and `qemu-bridge-helper` with `cap_net_admin`. Host module sets
  both (`security.wrappers.qemu-bridge-helper` and a default
  `etc."qemu/bridge.conf".text = "allow all"`).

## Customising the Generated `tap-up`

The runner exposes script snippets:

```nix
microvm.binScripts.tap-up = lib.mkAfter ''
  ${lib.getExe' pkgs.iproute2 "ip"} link set dev 'vm-foo' master 'my-bridge'
'';
```

This appends a line to the generated `bin/tap-up` (used by the host
module). Useful for attaching to bridges not declared via
`microvm.interfaces.*.bridge`.

## Choosing a Networking Topology

- LAN with cheap IPs → bridge to a `systemd-networkd` bridge. See
  [[recipe-simple-network]].
- One public IPv4 + internal subnet → bridge + NAT. See
  [[recipe-advanced-network]].
- Per-VM host routes, no shared L2 → routed mode. See
  [[recipe-routed-network]].
