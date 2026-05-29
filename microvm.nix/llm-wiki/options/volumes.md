---
id: option-volumes
title: "microvm.volumes"
category: option
layer: core
tags: [volume, disk, block-device, autoCreate, ext4]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/boot-disk.nix
source_commit: 0d49083
api_surface:
  - microvm.volumes
related: [option-shares, concept-store-on-disk]
see_also: [recipe-writable-store-overlay]
---

## Shape

`microvm.volumes` is a list of submodule entries. Each entry maps a
host-side image file to a guest block device.

```nix
microvm.volumes = [{
  image = "/var/lib/microvms/my-vm/data.img";  # or relative
  mountPoint = "/var/lib/data";
  size = 4096;             # MiB; required for autoCreate
  fsType = "ext4";         # default
  autoCreate = true;       # default
  readOnly = false;
  label = "data";          # optional
  direct = false;          # O_DIRECT
  serial = null;           # user-configured disk serial
  mkfsExtraArgs = [];
  imageType = "raw";       # raw | qcow2 | vhd | vhdx (CHV only)
}];
```

## Per-field Notes

| Field | Type | Default | Notes |
|---|---|---|---|
| `image` | str | required | Host path. Relative paths resolve under `/var/lib/microvms/$hostName` |
| `mountPoint` | nullable path | required | Where to mount inside the guest |
| `size` | int | required | MiB. Used only when `autoCreate = true` |
| `fsType` | str | `"ext4"` | Used for `mkfs` when autoCreated and for the guest fstab entry |
| `autoCreate` | bool | `true` | Create the image on host before VM start |
| `readOnly` | bool | `false` | Read-only on the guest |
| `label` | nullable str | `null` | Filesystem label. Only valid with `autoCreate = true` |
| `direct` | bool | `false` | Open with `O_DIRECT` (bypass page cache). Firecracker logs a warning if set |
| `serial` | nullable str | `null` | Guest-visible disk serial. Firecracker logs a warning if set |
| `mkfsExtraArgs` | list of str | `[]` | Extra args passed to `mkfs.<type>` |
| `imageType` | enum | `"raw"` | `raw`, `qcow2`, `vhd`, `vhdx`. Only `cloud-hypervisor` honours non-`raw` |

## Drive Letters

`microvm-lib.withDriveLetters` (in `/p/gh/microvm.nix/lib/default.nix`)
assigns guest device letters (`/dev/vda`, `/dev/vdb`, …). The offset
is `1` when `storeOnDisk = true` (store disk takes `vda`), else `0`.

## Mounts

`nixos-modules/microvm/mounts.nix` translates each volume into a
`fileSystems` entry by mountPoint with `device =
"/dev/disk/by-label/<label>"` (when `label` is set) or by-id, plus a
boot dependency.

## When To Use a Volume vs a Share

- **Volume**: exclusive guest access, fast, can be ext4/xfs/btrfs.
  Required as the upper layer of a `writableStoreOverlay`.
- **Share** (`microvm.shares`): host directory tree available to
  the guest with concurrent host access. Cannot be the upper layer
  of an overlay.
