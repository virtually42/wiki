---
id: recipe-macos-linux-builder
title: "Building NixOS Guests on macOS"
category: recipe
layer: application
tags: [macos, vfkit, linux-builder, remote-builder, cross-build]
source_files:
  - /p/gh/microvm.nix/doc/src/faq.md
source_commit: 0d49083
api_surface: []
related: [hypervisor-vfkit, recipe-vfkit-rosetta]
see_also: []
---

## The Problem

On macOS, `vfkit` runs natively but the guest is Linux. macOS
toolchains can't (cross-)compile NixOS, so `nix run
.#nixosConfigurations.my-microvm.config.microvm.declaredRunner`
errors with:

```
error: Cannot build '/nix/store/...-nixos-system-....drv'.
       Reason: required system or feature not available
       Required system: 'aarch64-linux' with features {}
       Current system: 'aarch64-darwin' with features {apple-virt, ...}
```

You need a Linux builder. Pick one:

## Options (Pick One)

### 1. nix-darwin `linux-builder` (recommended for casual use)

`nixpkgs` ships a small Linux builder VM that nix-darwin can manage:

```nix
# darwin-configuration.nix
nix.linux-builder.enable = true;
```

See the [nixcademy write-up](https://nixcademy.com/posts/macos-linux-builder/).

### 2. Determinate Nix native Linux builder

[Determinate Nix](https://docs.determinate.systems/troubleshooting/native-linux-builder/)
ships a native Linux builder on macOS (currently closed beta).

### 3. `nix-rosetta-builder`

[`nix-rosetta-builder`](https://github.com/cpick/nix-rosetta-builder)
runs an `x86_64-linux` builder on Apple Silicon via Rosetta — handy
when you specifically need x86_64-linux outputs.

### 4. Existing Remote Linux Machine

Add it to `/etc/nix/machines` as a Nix remote builder. Same shape
as any other distributed builder. Best when you already operate
Linux infrastructure.

## Optional: microvm.cachix.org

The flake advertises `https://microvm.cachix.org` as a substituter.
If you don't want extra trusted caches, decline the prompt or pass
`--no-accept-flake-config`. The local Linux builder will build
everything from source.

## Building & Running

Once a Linux builder is in place:

```bash
nix run .#nixosConfigurations.my-mac-vm.config.microvm.declaredRunner
```

The guest closure gets built on the Linux builder; vfkit runs the
result natively on macOS.

## See Also

- [[hypervisor-vfkit]] — what vfkit supports.
- [[recipe-vfkit-rosetta]] — running x86_64 binaries inside the
  guest on Apple Silicon.
