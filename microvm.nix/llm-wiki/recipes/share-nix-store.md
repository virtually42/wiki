---
id: recipe-share-nix-store
title: "Share Host /nix/store"
category: recipe
layer: application
tags: [shares, nix-store, virtiofs, 9p, build-time, image-size]
source_files:
  - /p/gh/microvm.nix/doc/src/shares.md
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface: [microvm.shares, microvm.storeOnDisk]
related: [concept-store-on-disk, option-shares]
see_also: [recipe-writable-store-overlay]
---

## Why

Without sharing the host's `/nix/store`, the runner builds a
read-only erofs/squashfs containing the **full guest closure** —
which dominates image size and build time. Sharing skips that step.

## With virtiofs (Preferred on qemu / cloud-hypervisor / crosvm)

```nix
microvm.shares = [{
  tag = "ro-store";
  source = "/nix/store";
  mountPoint = "/nix/.ro-store";
  proto = "virtiofs";
}];
```

The initrd binds `/nix/.ro-store` to `/nix/store` at boot.
`microvm.storeOnDisk` defaults to `false` once this share is present
— no store disk is generated.

Under the host module, `microvm-virtiofsd@.service` runs the daemon.
For interactive `nix run` use, see [[recipe-run-as-package]] — you'd
have to launch `bin/virtiofsd-run` yourself.

## With 9p (qemu / kvmtool / alioth)

```nix
microvm.shares = [{
  tag = "ro-store";
  source = "/nix/store";
  mountPoint = "/nix/.ro-store";
  proto = "9p";   # default
}];
```

Slower than virtiofs but no sidecar daemon needed.

## With Firecracker — You Can't

Firecracker has no share support at all. Either:

- Live with the read-only store disk (a fresh closure per build).
- Pre-build a volume image with the closure baked in.

## ZFS Source

If `/nix/store` is on ZFS, the dataset must be created/configured with:

```
zfs set xattr=sa acltype=posixacl <pool>/<store>
```

Without these, virtiofs ACL handling breaks. See [[option-shares]].

## Combined With a Writable Overlay

If the guest needs `nix build`, also add a `writableStoreOverlay` —
must be a volume, not a share. See [[recipe-writable-store-overlay]].
