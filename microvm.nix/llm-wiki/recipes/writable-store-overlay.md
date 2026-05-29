---
id: recipe-writable-store-overlay
title: "Writable /nix/store Overlay"
category: recipe
layer: application
tags: [writableStoreOverlay, overlay, nix-build, volume]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/doc/src/shares.md
source_commit: 0d49083
api_surface: [microvm.writableStoreOverlay, microvm.volumes]
related: [recipe-share-nix-store, concept-store-on-disk, option-store-disk]
see_also: []
---

## Use Case

You want `nix build` to work inside the guest — for example a CI
worker VM, or development VMs that compile code.

## Why a Volume, Not a Share

Linux overlayfs cannot use 9p / virtiofs as the upper (writable)
layer. So even if you share the host's `/nix/store` for the
read-only base, the writable upper layer must be a block-device-
backed filesystem.

## Config

```nix
{ config, ... }: {
  microvm.shares = [{
    tag = "ro-store";
    source = "/nix/store";
    mountPoint = "/nix/.ro-store";
    proto = "virtiofs";
  }];

  microvm.writableStoreOverlay = "/nix/.rw-store";

  microvm.volumes = [{
    image = "nix-store-overlay.img";       # relative -> /var/lib/microvms/$hostName/
    mountPoint = config.microvm.writableStoreOverlay;
    size = 2048;                           # MiB
    # autoCreate = true (default), fsType = "ext4" (default)
  }];
}
```

The initrd mounts `/nix/store` as overlayfs: lower =
`/nix/.ro-store` (the share), upper = `/nix/.rw-store` (the volume).

## Caveat — Nix Database Resets

> The Nix database will forget all built packages after a reboot,
> containing only what is needed for the VM's NixOS system.

The system closure store paths are registered on boot via
`microvm.registerClosure` (default: `microvm.guest.enable`), but the
extra paths you built sit in the overlay without DB entries after
restart. Two coping strategies, both from the upstream docs:

1. Delete and recreate the overlay between shutdowns (cheap if the
   guest is mostly stateless).
2. Use the overlay during a session, then `nix copy` results out
   before reboot.

## With `microvm.registerClosure`

The `microvm.registerClosure` option is `mkEnableOption`'d to
`microvm.guest.enable` (default `true`). The description warns:

> While enabled by default, this option may be incompatible with a
> persistent writable store overlay.

If you persist the overlay across reboots, consider setting it to
`false`.
