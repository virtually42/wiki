---
id: option-graphics
title: "microvm.graphics"
category: option
layer: core
tags: [graphics, gpu, gtk, cocoa, virtio-gpu, wayland]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/graphics.nix
source_commit: 0d49083
api_surface:
  - microvm.graphics.enable
  - microvm.graphics.backend
  - microvm.graphics.socket
  - microvm.graphics.crosvmPackage
related: [hypervisor-qemu, hypervisor-cloud-hypervisor, hypervisor-vfkit]
see_also: []
---

## Options

| Option | Type | Default | Notes |
|---|---|---|---|
| `microvm.graphics.enable` | bool | `false` | Enable GUI. Such MicroVMs cannot be started via systemd jobs — interactive only |
| `microvm.graphics.backend` | enum | `"cocoa"` on Darwin, else `"gtk"` | qemu display backend |
| `microvm.graphics.socket` | str | `"$hostName-gpu.sock"` | vhost-user GPU socket path |
| `microvm.graphics.crosvmPackage` | package | `pkgs.crosvm` | crosvm package used as the vhost-user GPU sidecar for cloud-hypervisor / crosvm graphics |

## Hypervisor Behaviour

- **qemu**: uses `-display gtk` (or cocoa on Darwin). Forces non-
  microvm machine type (`requirePci` becomes true).
- **cloud-hypervisor**: uses `pkgs.cloud-hypervisor-graphics` and a
  vhost-user GPU sidecar from `crosvmPackage`.
- **crosvm**: native graphics support via `--gpu`.
- **vfkit**: adds `virtio-gpu` + `virtio-input,keyboard` +
  `virtio-input,pointing`. Console moves from `hvc0` to `tty0`.
- Other hypervisors: not supported.

## Wayland Forwarding

The flake exposes `nix run microvm#graphics <pkgs...>` (see
`flake.nix`) which uses `waypipe` over AF_VSOCK to forward Wayland
applications from inside the guest. The host runs
`nix run microvm#waypipe-client` to accept connections on
`AF_VSOCK port 6000`.

## When To Avoid

- Headless servers — leave graphics disabled, save a lot of closure.
- Anywhere you want the lightweight `microvm` machine type (graphics
  forces full PCIe).
