---
id: convention-custom-runner
title: "Custom OS Runner Packages"
category: convention
layer: integration
tags: [custom-runner, non-nixos, solo5, buildRunner]
source_files:
  - /p/gh/microvm.nix/doc/src/conventions.md
  - /p/gh/microvm.nix/lib/runner.nix
source_commit: 0d49083
api_surface: [lib.buildRunner]
related: [convention-runner-layout, concept-runner-package]
see_also: []
---

## Why

A runner package fully encodes how to run a hypervisor — kernel,
disks, sockets, scripts. So in principle you can run any guest OS
on a microvm.nix host, as long as you produce a package that
satisfies the [[convention-runner-layout]] contract.

The example called out by the upstream docs:

> [microvm-solo5-spt](https://github.com/microvm-nix/microvm-solo5-spt)
> is an example of a Flake that can run on a microvm.nix host.

## Two Approaches

### Approach A — Reuse `microvm-lib.buildRunner`

`/p/gh/microvm.nix/lib/runner.nix` is exposed as
`microvm-lib.buildRunner`. Call it with a `microvmConfig` attrset
that has the same shape the NixOS module would produce:

```nix
microvm-lib.buildRunner {
  inherit pkgs;
  microvmConfig = {
    hypervisor = "qemu";
    hostName = "my-non-nixos-vm";
    kernel = pkgs.linuxKernel.kernels.linux_6_6;
    initrdPath = ...;
    kernelParams = [ "console=ttyS0" "init=/bin/init" ];
    vcpu = 2; mem = 1024;
    storeOnDisk = false;
    storeDisk = null;
    volumes = [ ... ];
    interfaces = [ ... ];
    shares = [];
    # ... plus the per-hypervisor sub-attrs
  };
  toplevel = null;  # not a NixOS toplevel, but you must pass *something*
}
```

This way the resulting package automatically satisfies the
file-layout contract.

### Approach B — Write Your Own

Build a derivation with the same `bin/` + `share/microvm/` layout.
The host module doesn't care how you got there. You take on the
responsibility for:

- `bin/microvm-run` that exec-s your hypervisor.
- `bin/microvm-shutdown` that initiates ACPI-style shutdown.
- `bin/tap-up` / `bin/virtiofsd-run` / `bin/pci-setup` if you use
  those features.
- The `share/microvm/*` metadata files that the host module's
  systemd services key off.

Reading `nix path-info -rs $(nix build -L --print-out-paths
.#nixosConfigurations.demo.config.microvm.declaredRunner)` is a
good way to inspect what an existing runner ships.

## Why You Might Want To

- Boot a unikernel (e.g. Solo5).
- Boot a non-NixOS Linux distro inside the microvm.nix systemd
  harness.
- Run prebuilt cloud images on the same host as your NixOS MicroVMs
  with consistent management.

For most users, this is unnecessary — the upstream guest module
covers NixOS guests on all eight hypervisors.
