---
id: recipe-run-as-package
title: "Run a MicroVM Interactively"
category: recipe
layer: application
tags: [nix-run, declaredRunner, interactive, packages]
source_files:
  - /p/gh/microvm.nix/doc/src/packages.md
source_commit: 0d49083
api_surface: [microvm.declaredRunner]
related: [concept-runner-package, recipe-declaring]
see_also: [recipe-declarative]
---

## Run It Directly

```bash
nix run .#nixosConfigurations.my-microvm.config.microvm.declaredRunner
```

You get a serial console. Use this for:

- Testing changes before deploying.
- Demo / dev VMs that you stop when you `Ctrl-]` out.

## Add It to `packages`

```nix
# In flake.nix outputs:
packages.x86_64-linux.my-microvm =
  self.nixosConfigurations.my-microvm.config.microvm.declaredRunner;
```

Then:

```bash
nix run .#my-microvm
```

## Caveats vs. the Host Module

Interactive `nix run` skips a lot:

- **No TAP setup.** `bin/tap-up` is not invoked, so `type = "tap"`
  interfaces require you to pre-create the TAP yourself
  (`ip tuntap add ...`) or use `type = "user"` for SLiRP.
- **No virtiofsd.** virtiofs shares won't work unless you run
  `bin/virtiofsd-run` from the runner separately.
- **No PCI binding.** `bin/pci-setup` is not invoked; PCI passthrough
  needs the host module.
- **No systemd-machined registration.**

For most things beyond a quick try, use the host module —
[[host-host-module]] + [[recipe-declarative]].

## Run on a Specific Hypervisor

To bypass `microvm.hypervisor` and try a different runner ad-hoc:

```bash
nix run .#nixosConfigurations.my-microvm.config.microvm.runner.firecracker
```

Don't use this in production; other options (e.g. `microvm.optimize`)
can branch on `microvm.hypervisor` and produce inconsistent defaults.
