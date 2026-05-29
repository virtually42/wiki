---
id: option-vsock
title: "microvm.vsock"
category: option
layer: core
tags: [vsock, af_vsock, systemd-notify]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/vsock-ssh.nix
source_commit: 0d49083
api_surface:
  - microvm.vsock.cid
related: [hypervisor-cloud-hypervisor, host-systemd-services]
see_also: []
---

## `microvm.vsock.cid`

Type: nullable int.
Default: `null`.

Sets a VM AF_VSOCK context ID, enabling guest-host VSOCK communication.
Reserved CIDs:

- `0` — Hypervisor
- `1` — Loopback
- `2` — Host

So practical CIDs start at `3`.

## Why Set It

- **systemd-notify integration**: on cloud-hypervisor, setting a CID
  lets the runner mark `supportsNotifySocket = true`. The host
  module then uses `Type=notify` instead of `Type=simple` for
  `microvm@.service`. Without the CID, CHV warns at eval time.
- **AF_VSOCK SSH**: `vsock-ssh.nix` provides patterns for SSHing
  into the guest over VSOCK without IP networking.
- General fast host-guest IPC.

## Hypervisor Support

Supported on qemu, cloud-hypervisor, firecracker, crosvm, vfkit. Not
on kvmtool, stratovirt, alioth (no control socket / no VSOCK device).
