---
id: option-store-disk
title: "Store Disk and Writable Overlay Options"
category: option
layer: core
tags: [store-disk, erofs, squashfs, overlay, writableStoreOverlay]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/store-disk.nix
source_commit: 0d49083
api_surface:
  - microvm.storeOnDisk
  - microvm.storeDiskType
  - microvm.storeDiskErofsFlags
  - microvm.storeDiskSquashfsFlags
  - microvm.writableStoreOverlay
  - microvm.registerClosure
  - microvm.systemSymlink
related: [concept-store-on-disk, option-shares]
see_also: [recipe-share-nix-store, recipe-writable-store-overlay]
---

## Options

| Option | Type | Default | Notes |
|---|---|---|---|
| `microvm.storeOnDisk` | bool | `true` unless a `source = "/nix/store"` share exists | Boot with a generated read-only store disk |
| `microvm.storeDiskType` | enum | `"erofs"` (or `"squashfs"` on hardened profile) | erofs is faster, squashfs smaller |
| `microvm.storeDiskErofsFlags` | list of str | `["-zlz4hc"]` + kernel-version-dependent flags | mkfs.erofs flags |
| `microvm.storeDiskSquashfsFlags` | list of str | `["-c" "zstd" "-j" "$NIX_BUILD_CORES"]` | gensquashfs flags |
| `microvm.writableStoreOverlay` | nullable str | `null` | Path to the writable overlay (e.g. `/nix/.rw-store`) |
| `microvm.registerClosure` | bool (mkEnableOption) | `microvm.guest.enable` | Register system closure store paths in the Nix db. Can conflict with persistent writable overlays |
| `microvm.systemSymlink` | bool | `!microvm.storeOnDisk` | Whether to include a `share/microvm/system` symlink to `config.system.build.toplevel`. Required for `microvm -l` |

## erofs Flag Defaults

```nix
[ "-zlz4hc" ]
  ++ lib.optional (kernelAtLeast "5.16") "-Eztailpacking"
  ++ lib.optionals (kernelAtLeast "6.1") [ "-Efragments" "-Ededupe" ]
```

Note the comment in `options.nix`: omit `-Efragments` and
`-Ededupe` if you want multi-threaded erofs build (they disable it).

## Writable Overlay Caveats

- Linux overlayfs cannot use 9p / virtiofs as the upper layer. Use a
  volume (see [[recipe-writable-store-overlay]]).
- The Nix database in the overlay forgets all built packages after a
  reboot (only the system closure is registered on boot). The
  upstream recommendation is to delete and recreate the overlay
  around VM shutdowns.
