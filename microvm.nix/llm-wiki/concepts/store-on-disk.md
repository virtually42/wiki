---
id: concept-store-on-disk
title: "Store on Disk vs. Host Share"
category: concept
layer: core
tags: [store, erofs, squashfs, virtiofs, 9p, overlay]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/store-disk.nix
  - /p/gh/microvm.nix/doc/src/shares.md
source_commit: 0d49083
api_surface: [microvm.storeOnDisk, microvm.storeDiskType, microvm.writableStoreOverlay, microvm.shares]
related: [concept-microvm-model, option-store-disk, option-shares]
see_also: [recipe-share-nix-store, recipe-writable-store-overlay]
---

## Two Models for `/nix/store`

A NixOS guest needs access to the store closure of its system. The
flake gives you two ways:

### Option A — Read-only store disk (default)

`microvm.storeOnDisk = true` (the default unless a share with
`source = "/nix/store"` exists).

- Build a read-only erofs (default) or squashfs containing **just**
  the guest's system closure.
- File systems controlled by `microvm.storeDiskType` (`erofs` or
  `squashfs`), `microvm.storeDiskErofsFlags`,
  `microvm.storeDiskSquashfsFlags`.
- Pros: VM is self-contained, fast boot, smallest attack surface.
- Cons: build time and image size grow with the guest closure;
  every guest rebuild produces a new disk.

### Option B — Share host `/nix/store`

```nix
microvm.shares = [{
  tag = "ro-store";
  source = "/nix/store";
  mountPoint = "/nix/.ro-store";
  proto = "virtiofs";  # or "9p"
}];
```

- The host's full `/nix/store` is available to the guest at
  `/nix/.ro-store`; the standard initrd binds it to `/nix/store`.
- `microvm.storeOnDisk` defaults to `false` when this share exists.
- Pros: no per-guest store disk, faster rebuilds, guests can
  hard-link from any host-built path.
- Cons: host store is exposed; sandboxing weaker; needs virtiofsd
  (qemu/CHV) or 9p (qemu/kvmtool). Not available on Firecracker.

See [[recipe-share-nix-store]] for the full pattern.

## Writable Overlay

`microvm.writableStoreOverlay = "/nix/.rw-store"` mounts an overlay
on top of the read-only store, letting the guest run `nix build`.

Caveat from the upstream docs: the upper (writable) layer of a Linux
overlay cannot be a 9p / virtiofs share. Use a volume:

```nix
microvm.writableStoreOverlay = "/nix/.rw-store";
microvm.volumes = [{
  image = "nix-store-overlay.img";
  mountPoint = config.microvm.writableStoreOverlay;
  size = 2048;
}];
```

The Nix database in the overlay is **not persisted across reboots**
of the VM (only the system closure entries are registered on boot).
Recommended pattern: delete and recreate the overlay around shutdown.
See [[recipe-writable-store-overlay]].
