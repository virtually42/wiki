---
id: concept-runner-package
title: "The Runner Package"
category: concept
layer: core
tags: [runner, declaredRunner, package, integration-contract]
source_files:
  - /p/gh/microvm.nix/lib/runner.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/default.nix
  - /p/gh/microvm.nix/doc/src/output-options.md
  - /p/gh/microvm.nix/doc/src/conventions.md
source_commit: 0d49083
api_surface: [microvm.declaredRunner, microvm.runner, microvm.runner.<hypervisor>]
related: [convention-runner-layout, host-systemd-services]
see_also: [recipe-run-as-package]
---

## What a Runner Package Is

`config.microvm.declaredRunner` is a Nix derivation that, when built,
contains everything needed to start one MicroVM:

- The hypervisor binary (qemu, firecracker, …)
- The guest kernel + initrd
- The store disk image (if `storeOnDisk = true`)
- Generated scripts: `bin/microvm-run`, `bin/microvm-shutdown`,
  `bin/tap-up`, `bin/virtiofsd-run`, `bin/pci-setup`, etc.
- Sidecar metadata under `share/microvm/`: tap interfaces list,
  virtiofs sockets, PCI device list, symlink to `system.build.toplevel`.

Built by `microvm-lib.buildRunner` (see `/p/gh/microvm.nix/lib/runner.nix`),
called by `nixos-modules/microvm/default.nix` once per hypervisor:

```nix
microvm.runner = lib.genAttrs microvm-lib.hypervisors (hypervisor:
  microvm-lib.buildRunner {
    inherit pkgs;
    microvmConfig = config.microvm // {
      inherit (config.networking) hostName;
      inherit hypervisor;
    };
    inherit (config.system.build) toplevel;
  });
```

## `microvm.runner` vs `microvm.declaredRunner`

| Option | Description |
|---|---|
| `microvm.runner.<hv>` | One runner per hypervisor, regardless of `microvm.hypervisor` |
| `microvm.declaredRunner` | The runner selected by `microvm.hypervisor` |

**Use `declaredRunner` in production.** Any NixOS configuration that
evaluates `microvm.hypervisor` (e.g. defaults set by
`microvm.optimize`) can be wrong if you pick from
`microvm.runner.<hv>` directly. Switching `microvm.hypervisor` and
using `declaredRunner` keeps the rest of the config consistent.

```bash
# Production
nix run .#nixosConfigurations.my-microvm.config.microvm.declaredRunner

# Ad-hoc: try a specific hypervisor without touching microvm.hypervisor
nix run .#nixosConfigurations.my-microvm.config.microvm.runner.firecracker
```

## Add a Runner to a Flake's `packages`

```nix
packages.x86_64-linux.my-microvm =
  self.nixosConfigurations.my-microvm.config.microvm.declaredRunner;
```

Then: `nix run .#my-microvm`.

## Integration Contract with the Host Module

A runner package is consumed by the host module via fixed file
paths under `bin/` and `share/microvm/`. See
[[convention-runner-layout]] for the full table — this is how the
flake can in principle run non-NixOS guests, as long as the runner
honours the same layout (see [[convention-custom-runner]]).
