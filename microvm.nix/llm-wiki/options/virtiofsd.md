---
id: option-virtiofsd
title: "microvm.virtiofsd"
category: option
layer: integration
tags: [virtiofsd, virtiofs, daemon, zfs]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/virtiofsd
source_commit: 0d49083
api_surface:
  - microvm.virtiofsd.inodeFileHandles
  - microvm.virtiofsd.threadPoolSize
  - microvm.virtiofsd.group
  - microvm.virtiofsd.extraArgs
  - microvm.virtiofsd.package
related: [option-shares, host-systemd-services]
see_also: []
---

## Options

| Option | Type | Default | Notes |
|---|---|---|---|
| `microvm.virtiofsd.inodeFileHandles` | enum nullable | `"prefer"` | `never` / `prefer` / `mandatory`. Switch to `never` if you hit "too many open files" on ZFS — [virtiofsd#121](https://gitlab.com/virtio-fs/virtiofsd/-/issues/121) |
| `microvm.virtiofsd.threadPoolSize` | str or unsigned int | `` "`nproc`" `` | Number of daemon threads. The string `` "`nproc`" `` substitutes at start-up |
| `microvm.virtiofsd.group` | nullable str | `"kvm"` | Group owning the daemon's Unix socket |
| `microvm.virtiofsd.extraArgs` | list of str | `[]` | Extra command-line switches to virtiofsd |
| `microvm.virtiofsd.package` | package | `cfg.vmHostPackages.virtiofsd` | Override the daemon package |

## How It's Invoked

- The runner generates `bin/virtiofsd-run` which `exec`s one
  virtiofsd per virtiofs share (one per tag).
- The host module's `microvm-virtiofsd@.service` runs that script
  with `Restart=always`, `NotifyAccess=all`, `Type=notify`,
  `KillMode=mixed`, `LimitNOFILE=1048576`.
- Sockets live under `/var/lib/microvms/$NAME/$hostName-virtiofs-$tag.sock`
  (default naming from the `socket` field of a share).

## When To Touch These

- **ZFS-backed shares**: drop `inodeFileHandles` to `"never"` and set
  the dataset's `xattr=sa acltype=posixacl`.
- **High concurrent IO**: set `threadPoolSize` to a fixed number
  rather than letting it default to `nproc`.
- **Custom daemon build**: override `package` (e.g. to a debug build).
