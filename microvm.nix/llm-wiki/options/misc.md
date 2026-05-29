---
id: option-misc
title: "Miscellaneous Guest Options"
category: option
layer: core
tags: [misc, socket, preStart, kernel, optimize, machineId, credentialFiles, binScripts]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/optimization.nix
source_commit: 0d49083
api_surface:
  - microvm.guest.enable
  - microvm.optimize.enable
  - microvm.socket
  - microvm.preStart
  - microvm.extraArgsScript
  - microvm.user
  - microvm.kernel
  - microvm.initrdPath
  - microvm.kernelParams
  - microvm.machineId
  - microvm.registerWithMachined
  - microvm.credentialFiles
  - microvm.binScripts
  - microvm.prettyProcnames
related: [host-systemd-services]
see_also: []
---

## Core Toggles

| Option | Type | Default | Notes |
|---|---|---|---|
| `microvm.guest.enable` | bool | `true` | Master switch for the guest module (lets you set MicroVM options on a non-guest config) |
| `microvm.optimize.enable` | bool | `true` | Optimisations that cut closure size and boot time (doc off, systemd-in-initrd, systemd-networkd, etc.) |
| `microvm.prettyProcnames` | bool | `true` | Set a recognisable host process name before exec-ing the hypervisor |

`microvm.optimize.enable` is the most impactful toggle — disabling it
brings back ~hundreds of MB of closure. Read
`/p/gh/microvm.nix/nixos-modules/microvm/optimization.nix` for the
full list of defaults applied.

## Hypervisor Process

| Option | Type | Default | Notes |
|---|---|---|---|
| `microvm.socket` | nullable str | `"$hostName.sock"` | Hypervisor control socket path (ignored by hypervisors without one) |
| `microvm.preStart` | lines | `""` | Commands run before starting the hypervisor |
| `microvm.extraArgsScript` | nullable str | `null` | Script outputting a single line of extra hypervisor args at runtime |
| `microvm.user` | nullable str | `null` | User to switch to when started as root |

## Kernel

| Option | Type | Default | Notes |
|---|---|---|---|
| `microvm.kernel` | package | `config.boot.kernelPackages.kernel` | Override the kernel package (prefer setting `boot.kernelPackages`) |
| `microvm.initrdPath` | path | `${config.system.build.initialRamdisk}/${config.system.boot.loader.initrdFile}` | Override the initrd path |
| `microvm.kernelParams` | list of str | — | Includes `boot.kernelParams` but doesn't end up in toplevel, allowing references to toplevel |

## Identity

| Option | Type | Default | Notes |
|---|---|---|---|
| `microvm.machineId` | nullable str | Deterministic SHA256-derived UUIDv5 from `${hostName}` | UUID for systemd-machined registration, SMBIOS, and `/etc/machine-id` initialization |
| `microvm.registerWithMachined` | bool | `false` | Register with `systemd-machined` (`class=vm`). Adds `systemd-machined.service` to `wants` / `after`. Notes: `machinectl reboot` stops the VM without restart; use `systemctl restart microvm@<name>` |

## Credentials

`microvm.credentialFiles` — `attrsOf path`. Each pair loads a file
into the guest via systemd's `io.systemd.credential` mechanism. E.g.:

```nix
microvm.credentialFiles = {
  SOPS_AGE_KEY = "/run/secrets/guest_microvm_age_key";
};
```

## Generated Script Hooks

`microvm.binScripts` — `attrsOf lines`. Each entry becomes / appends
to a file under `bin/` in the runner package. Common entry: extend
`tap-up`:

```nix
microvm.binScripts.tap-up = lib.mkAfter ''
  ${lib.getExe' pkgs.iproute2 "ip"} link set dev 'vm-myvm-0' master 'br0'
'';
```
