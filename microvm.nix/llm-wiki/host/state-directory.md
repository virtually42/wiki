---
id: host-state-directory
title: "/var/lib/microvms Layout"
category: host
layer: integration
tags: [state-directory, var-lib-microvms, current, booted, flake]
source_files:
  - /p/gh/microvm.nix/nixos-modules/host/default.nix
  - /p/gh/microvm.nix/doc/src/microvm-command.md
source_commit: 0d49083
api_surface:
  - microvm.stateDir
related: [host-host-module, host-microvm-command, host-systemd-services]
see_also: []
---

## Per-VM Layout

```
/var/lib/microvms/                   # stateDir, owned microvm:kvm 0775
├── <name>/                          # one per VM
│   ├── current -> /nix/store/...-microvm-run   (the runner package)
│   ├── booted  -> /nix/store/...-microvm-run   (last successful boot — set by microvm-set-booted)
│   ├── old     -> /nix/store/...-microvm-run   (previous current — set by microvm CLI on update)
│   ├── flake                                  (only for declarative-deployment / imperative VMs)
│   ├── toplevel -> ...                         (only for fully-declarative VMs)
│   ├── journal/                                (custom share dirs from microvm.shares with relative source)
│   ├── data.img                                (volume images with relative `image` path)
│   ├── <hostName>-virtiofs-<tag>.sock          (virtiofsd sockets)
│   └── notify.vsock                            (vsock socket if microvm.vsock.cid set)
```

## Symlink Semantics

- `current` — the runner that will be used on the **next** start of
  `microvm@<name>.service`. Updated by `install-microvm-<name>.service`
  (declarative) or by `microvm -u` (imperative).
- `booted` — set during `microvm-set-booted@<name>.service` (oneshot,
  RemainAfterExit) to mirror `current` at boot. `ExecStop`s on tap /
  virtiofsd / microvm-shutdown use scripts from `booted/bin/` so the
  shutdown matches the runner that actually started.
- `old` — written by the `microvm` CLI on update before changing
  `current`. Lets you `nix store diff-closures old current`.
- `flake` — flake ref string for `microvm -u`.

## Why `current` vs `booted`

When you `microvm -u` (or run `install-microvm` for a fully-
declarative VM), `current` points at the *new* runner. The VM is
still running off the *previous* runner — that's what `booted`
captures, so `ExecStop` can call the same shutdown script that the
running hypervisor expects. Without this split, restarting a VM
after an update would invoke the new shutdown script against the
old hypervisor, which can mismatch (e.g. different ACPI flags).

## Custom State Dir

`microvm.stateDir` defaults to `/var/lib/microvms`. Override on the
host to put VM state on a separate filesystem (XFS, ZFS dataset
per VM, etc.). The path is owned by `microvm:kvm` mode `0775`.
