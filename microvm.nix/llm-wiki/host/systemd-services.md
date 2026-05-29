---
id: host-systemd-services
title: "Host systemd Services"
category: host
layer: integration
tags: [systemd, template-units, microvm-service, virtiofsd, tap, pci]
source_files:
  - /p/gh/microvm.nix/nixos-modules/host/default.nix
  - /p/gh/microvm.nix/doc/src/host-systemd.md
source_commit: 0d49083
api_surface: []
related: [host-host-module, convention-runner-layout]
see_also: []
---

## Template Units

The host module declares these template services (one instance per
MicroVM `%i = <name>`):

| Unit | Purpose | Runs |
|---|---|---|
| `install-microvm-<name>.service` | Populate `/var/lib/microvms/<name>` for declarative deployment | One-shot. Symlinks `current` to the runner; writes `flake` file for declarative-deployment VMs. For VMs with `updateFlake` set, only runs if `${stateDir}/<name>` doesn't already exist (so `nixos-rebuild switch` doesn't restart running VMs) |
| `microvm-tap-interfaces@.service` | Create TAP devices for the `microvm` user | `bin/tap-up` (Type=oneshot, RemainAfterExit=yes). `ExecStop` = `bin/tap-down` from `booted/` |
| `microvm-macvtap-interfaces@.service` | Create MACVTAP devices | `bin/macvtap-up` / `macvtap-down` |
| `microvm-pci-devices@.service` | Bind PCI devices to `vfio-pci` | `bin/pci-setup` |
| `microvm-virtiofsd@.service` | Run all virtiofsd daemons for shares | `bin/virtiofsd-run` (Type=notify, Restart=always, KillMode=mixed, LimitNOFILE=1048576) |
| `microvm-set-booted@.service` | Snapshot `current` symlink as `booted` | One-shot. Sets `booted -> $(readlink current)`. `ExecStop` removes `booted` |
| `microvm@.service` | Run the hypervisor | `bin/microvm-run`. `Type=notify` if runner advertises `supportsNotifySocket` or `microvm.host.useNotifySockets = true`, else `Type=simple`. `ExecStop = bin/microvm-shutdown` from `booted/`. Runs as `microvm:kvm` with `LimitMEMLOCK=infinity` |
| `microvms.target` | Aggregates `microvm@<name>.service` for all `microvm.autostart` | `WantedBy=multi-user.target` |

## Service Graph

```
microvms.target
  └─ wants: microvm@<name>.service (one per autostart entry)

microvm@<name>.service
  requires/after:
    microvm-tap-interfaces@<name>.service
    microvm-macvtap-interfaces@<name>.service
    microvm-pci-devices@<name>.service
    microvm-virtiofsd@<name>.service
    microvm-set-booted@<name>.service
  before:    install-microvm-<name>.service (via that unit's `before`)
  partOf:    install-microvm-<name>.service
```

`ExecStartPost` / `ExecStopPost` for `microvm@.service` invoke
`bin/microvm-register` / `microvm-unregister` if present (used for
systemd-machined integration when `microvm.registerWithMachined =
true`).

## Notify Mode

Two ways to flip a VM's service from `Type=simple` to `Type=notify`:

1. **Per-VM**: the runner advertises `supportsNotifySocket = true`
   when the hypervisor + VSOCK config can send `READY=1` over VSOCK.
   Currently cloud-hypervisor when `microvm.vsock.cid != null`.
2. **Host-wide**: `microvm.host.useNotifySockets = true`. Forces
   `Type=notify` for **all** MicroVMs — every guest must send
   `READY=1` or the service times out.

## `install-microvm-<name>.service`

The unit's `ConditionPathExists` for VMs with `flake != null` and
`updateFlake != null` is `!${stateDir}/${name}` — i.e. only runs
on initial install. This lets the operator update those VMs
imperatively with the `microvm` command without `nixos-rebuild` ever
clobbering them. Fully-declarative VMs (where `microvm.vms.<name>.config`
is set) always re-run install.

## `restartIfChanged`

`microvmConfig.restartIfChanged` (default: `true` for fully-declarative,
`false` for `flake`-based) controls whether systemd restarts the VM
when its unit definition changes. The setting is propagated to all
template units via `serviceConfig.X-RestartIfChanged`.
