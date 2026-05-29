---
id: recipe-cpu-emulation
title: "Run a Foreign-Architecture MicroVM"
category: recipe
layer: application
tags: [cpu-emulation, cross-build, qemu, aarch64, riscv]
source_files:
  - /p/gh/microvm.nix/doc/src/cpu-emulation.md
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface: [microvm.cpu, microvm.hypervisor]
related: [hypervisor-qemu, option-cpu-memory]
see_also: []
---

## Constraints

- **qemu only.** No other hypervisor supports CPU emulation.
- **Significant performance hit.** Useful for dev / CI / one-off
  builds, not production.

## Required Settings

| Setting | Value |
|---|---|
| `system` in `nixosSystem` | Host system (e.g. `x86_64-linux`) |
| `nixpkgs.crossSystem.config` | Guest target (e.g. `aarch64-unknown-linux-gnu`) |
| `microvm.hypervisor` | `"qemu"` |
| `microvm.cpu` | Emulated CPU name (e.g. `"cortex-a53"`). See [QEMU system targets](https://www.qemu.org/docs/master/system/targets.html) |

## Example

```nix
{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.microvm.url = "github:microvm-nix/microvm.nix";
  inputs.microvm.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, microvm }: {
    nixosConfigurations.emulated-dev = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = let
        guestSystem = "aarch64-unknown-linux-gnu";
        pkgs = import nixpkgs {
          system = "x86_64-linux";
          crossSystem.config = guestSystem;
        };
      in [
        microvm.nixosModules.microvm
        {
          nixpkgs.crossSystem.config = guestSystem;
          microvm = {
            cpu = "cortex-a53";
            hypervisor = "qemu";
          };
          environment.systemPackages = with pkgs; [ cowsay htop ];
          services.getty.autologinUser = "root";
          system.stateVersion = "24.11";
        }
      ];
    };
  };
}
```

Run:

```bash
nix run .#nixosConfigurations.emulated-dev.config.microvm.declaredRunner
```

## What the Runner Does

In `lib/runners/qemu.nix`:

- `microvm.cpu` is passed verbatim to `-cpu`.
- `accel` falls back to `tcg` (Tiny Code Generator, software-only)
  when KVM can't be used for the foreign arch.
- `microvm.vmHostPackages` defaults to `pkgs.buildPackages` when
  `microvm.cpu != null`, so the hypervisor is built for the *host*
  arch.
