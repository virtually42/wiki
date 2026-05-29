---
id: recipe-vhost-net
title: "vhost-net for High-Throughput TAP"
category: recipe
layer: application
tags: [vhost-net, performance, tap, qemu, throughput]
source_files:
  - /p/gh/microvm.nix/doc/src/interfaces.md
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/host/default.nix
source_commit: 0d49083
api_surface: [microvm.interfaces.*.tap.vhost]
related: [option-interfaces, hypervisor-qemu]
see_also: []
---

## What It Does

`tap.vhost = true` enables Linux's `vhost-net` kernel module to take
packet processing off qemu's userspace fast-path. Reported numbers:

- TAP without vhost-net: ~1.5 Gbps
- TAP with vhost-net:   ~10 Gbps

## Requirements

- `qemu` hypervisor (only one supported).
- `vhost_net` kernel module loaded on the host. The host module
  already declares it:

  ```nix
  boot.kernelModules = [ "tap" "vhost_net" ];
  ```

  If you run a runner standalone (`nix run` without the host module),
  load it manually: `modprobe vhost_net`.

## Guest Config

```nix
microvm.interfaces = [{
  type = "tap";
  id   = "vm-a1";
  mac  = "02:00:00:00:00:01";
  tap.vhost = true;
}];
```

That's it. The qemu runner appends `vhost=on` to the netdev args.

## When It Won't Help

- Workloads bottlenecked on the guest's kernel stack rather than
  the host-side virtio path.
- Many concurrent small connections may benefit more from multi-queue
  TAPs (`multi_queue` flag at `ip tuntap add` time and matching
  vCPU count).

## Multi-Queue Notes

If the guest has more than one CPU core and you want multi-queue,
add `multi_queue` when pre-creating the TAP:

```bash
sudo ip tuntap add $IFACE_NAME mode tap user $USER multi_queue
```

Under the host module the TAP is created by
`microvm-tap-interfaces@.service` running `bin/tap-up` — you'd
override the generated script via
`microvm.binScripts.tap-up = lib.mkBefore ''...''`.
