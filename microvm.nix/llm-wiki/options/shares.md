---
id: option-shares
title: "microvm.shares"
category: option
layer: core
tags: [shares, virtiofs, 9p, host-directory, zfs]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/virtiofsd
  - /p/gh/microvm.nix/doc/src/shares.md
source_commit: 0d49083
api_surface:
  - microvm.shares
  - microvm.virtiofsd.inodeFileHandles
  - microvm.virtiofsd.threadPoolSize
  - microvm.virtiofsd.group
  - microvm.virtiofsd.extraArgs
  - microvm.virtiofsd.package
related: [option-virtiofsd, concept-store-on-disk]
see_also: [recipe-share-nix-store, recipe-writable-store-overlay]
---

## Shape

```nix
microvm.shares = [{
  proto = "virtiofs";   # "9p" (default) | "virtiofs"
  tag   = "home";       # unique daemon tag
  source = "/srv/home"; # absolute or relative to /var/lib/microvms/$hostName
  mountPoint = "/home"; # guest path (required)
  readOnly = false;
  securityModel = "none";   # passthrough|none|mapped|mapped-file
  socket = null;            # 9p ignores; virtiofs default = $hostName-virtiofs-$tag.sock
  cache  = "auto";          # virtiofs only: auto|always|metadata|never
}];
```

## proto

| Value | Notes |
|---|---|
| `9p` | Built into qemu, kvmtool, alioth. No sidecar. Lower throughput. |
| `virtiofs` | Needs a `virtiofsd` daemon (sidecar). Higher performance. vfkit has it built-in; on Linux the host module starts `microvm-virtiofsd@.service` |

Hypervisor support for protos: see [[concept-hypervisor-matrix]].

## Host-side Daemon (`virtiofsd`)

On Linux, virtiofs shares are served by `pkgs.virtiofsd`. The runner
generates `bin/virtiofsd-run` which the host module's
`microvm-virtiofsd@.service` invokes (template service, one process
per VM, KillMode=mixed, Restart=always).

`microvm.virtiofsd.*` tune the daemon:

| Option | Default | Purpose |
|---|---|---|
| `inodeFileHandles` | `"prefer"` | When to use file handles vs `O_PATH` fds. Switch to `never` if you hit "too many open files" on ZFS |
| `threadPoolSize` | `` "`nproc`" `` | Thread count; string `` "`nproc`" `` substitutes at runtime |
| `group` | `"kvm"` | Unix group owning the virtiofsd socket |
| `extraArgs` | `[]` | Extra CLI args |
| `package` | `cfg.vmHostPackages.virtiofsd` | Override the package |

## ZFS Caveat

When the share source is on ZFS, the dataset must be created with:

```
zfs set xattr=sa acltype=posixacl <pool>/<dataset>
```

Without these, virtiofs ACL handling breaks.

## Special Case — `/nix/store`

If `source = "/nix/store"` is present, `microvm.storeOnDisk`
defaults to `false` — the build skips creating a store disk image.
The initrd binds the share at `/nix/.ro-store` to `/nix/store`. See
[[recipe-share-nix-store]] for the standard recipe.
