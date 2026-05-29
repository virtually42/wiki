---
id: host-host-module
title: "The Host Module"
category: host
layer: integration
tags: [host-module, microvm-host, autostart, useNotifySockets]
source_files:
  - /p/gh/microvm.nix/nixos-modules/host/default.nix
  - /p/gh/microvm.nix/nixos-modules/host/options.nix
  - /p/gh/microvm.nix/doc/src/host.md
source_commit: 0d49083
api_surface:
  - microvm.host.enable
  - microvm.host.startupTimeout
  - microvm.host.useNotifySockets
  - microvm.stateDir
  - microvm.autostart
related: [host-systemd-services, host-microvm-vms, host-state-directory]
see_also: [recipe-declarative]
---

## Importing

```nix
{
  imports = [ microvm.nixosModules.host ];
  # then:
  microvm.autostart = [ "my-vm1" "my-vm2" ];
}
```

Non-flake hosts can pull it directly:

```nix
imports = [ (builtins.fetchGit {
  url = "https://github.com/microvm-nix/microvm.nix";
} + "/nixos-modules/host") ];
```

## What It Does

`nixos-modules/host/default.nix` activates (when
`microvm.host.enable`, default `true`):

- Creates a `microvm` system user (group `kvm`) with
  `memlock = infinity` PAM limits.
- Loads `tap` and `vhost_net` kernel modules.
- Creates `/var/lib/microvms` (`stateDir`) owned by `microvm:kvm`,
  mode `0775`.
- Installs the `microvm` CLI on `environment.systemPackages`.
- Generates the `microvm-*@.service` template units (see
  [[host-systemd-services]]).
- Generates `install-microvm-<name>.service` and per-VM service
  dropins for each entry of `microvm.vms`.
- Sets up the `microvms.target` with `wants` for every
  `microvm.autostart` entry.
- Enables KSM (`hardware.ksm.enable = lib.mkDefault true`).
- Installs `qemu-bridge-helper` setuid wrapper with `cap_net_admin`
  (unless `virtualisation.libvirtd.enable`).
- Writes default `/etc/qemu/bridge.conf` (`allow all`).

## Options

| Option | Type | Default | Notes |
|---|---|---|---|
| `microvm.host.enable` | bool | `true` | Master toggle |
| `microvm.host.startupTimeout` | positive int | `150` (seconds) | `TimeoutSec` for `microvm@.service` |
| `microvm.host.useNotifySockets` | bool | `false` | Use `Type=notify` for `microvm@.service`. **Danger:** if any MicroVM doesn't send `READY=1`, its service won't start cleanly. Per-VM the same is decided by the runner's `supportsNotifySocket` (CHV with vsock CID set) |
| `microvm.stateDir` | path | `/var/lib/microvms` | Where MicroVM state directories live |
| `microvm.autostart` | list of str | `[]` | MicroVMs started by `microvms.target` |

`microvm.autostart` is also auto-populated from declarative VMs in
`microvm.vms.*.autostart = true` (default).

## Backwards-Compat Activation Script

A `system.activationScripts.microvm-update-check` (marked
`TODO: remove in 2026`) warns about old MicroVMs that still have
`share/microvm/virtiofs|tap-interfaces|macvtap-interfaces|pci-devices`
but lack the corresponding `bin/virtiofsd-run|tap-up|macvtap-up|pci-setup`
scripts. Rebuild and re-deploy those VMs.
