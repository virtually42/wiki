---
id: host-autostart
title: "Autostart"
category: host
layer: integration
tags: [autostart, microvms-target, multi-user]
source_files:
  - /p/gh/microvm.nix/nixos-modules/host/default.nix
  - /p/gh/microvm.nix/nixos-modules/host/options.nix
source_commit: 0d49083
api_surface:
  - microvm.autostart
  - microvm.vms.<name>.autostart
related: [host-host-module, host-systemd-services]
see_also: []
---

## Two Layers

1. **Per-VM opt-in**: `microvm.vms.<name>.autostart` (default `true`).
   In the host module's config, every `microvm.vms.*` entry with
   `autostart = true` gets folded into `microvm.autostart`.
2. **Host-level list**: `microvm.autostart` is `listOf str`. The
   host module wires `microvms.target` with one `wants` entry per
   name.

```nix
microvm.autostart = [
  "my-microvm"
  "your-microvm"
];
```

## `microvms.target`

```nix
systemd.targets.microvms = {
  wantedBy = [ "multi-user.target" ];
  wants    = map (name: "microvm@${name}.service") config.microvm.autostart;
};
```

On boot, `multi-user.target` pulls in `microvms.target`, which pulls
in each `microvm@<name>.service`. Each service in turn requires its
tap / macvtap / pci / virtiofsd / set-booted sibling units.

## Imperative MicroVMs

A VM created via `microvm -c my-vm` lives under
`/var/lib/microvms/my-vm` but **does not autostart** unless it's
listed in the host's `microvm.autostart`. To opt in:

```nix
microvm.autostart = [ "my-vm" ];
```

then `nixos-rebuild switch`. The doc emphasises this:

> Extension of the host's systemd units must happen declaratively in
> the host's NixOS configuration.

## Excluding a Declarative VM

Set `microvm.vms.<name>.autostart = false`. The VM is still built
and installed; you start it on demand with `systemctl start
microvm@<name>`.
