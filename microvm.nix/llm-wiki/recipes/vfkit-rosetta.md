---
id: recipe-vfkit-rosetta
title: "x86_64 Binaries on Apple Silicon via Rosetta"
category: recipe
layer: application
tags: [rosetta, vfkit, macos, apple-silicon, binfmt]
source_files:
  - /p/gh/microvm.nix/doc/src/vfkit-rosetta.md
  - /p/gh/microvm.nix/lib/runners/vfkit.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/rosetta.nix
source_commit: 0d49083
api_surface:
  - microvm.vfkit.rosetta.enable
  - microvm.vfkit.rosetta.install
  - microvm.vfkit.rosetta.ignoreIfMissing
related: [hypervisor-vfkit, recipe-macos-linux-builder]
see_also: []
---

## Requirements

- Apple Silicon Mac (M1/M2/M3/...).
- macOS with Rosetta installed (or set `install = true`).
- `microvm.hypervisor = "vfkit"`.

## Config

```nix
{
  microvm = {
    hypervisor = "vfkit";

    vfkit.rosetta = {
      enable = true;
      install = true;            # auto-install Rosetta if missing
      # ignoreIfMissing = true;  # for shared Apple-Intel configs
    };
  };
}
```

The NixOS module (`nixos-modules/microvm/rosetta.nix`) auto-mounts
the `rosetta` virtiofs share inside the guest and configures
`binfmt` so x86_64 ELF binaries route through `/run/rosetta/rosetta`.
No further guest config required.

## Verification

```nix
environment.systemPackages = with pkgs; [
  file
  pkgsCross.gnu64.hello   # x86_64 hello
];
```

In the guest:

```bash
uname -m            # aarch64
file $(which hello) # ELF 64-bit LSB executable, x86-64
hello               # Hello, world!  (executed via Rosetta)
```

## Compile Any Package as x86_64

`pkgsCross.gnu64.<package>` cross-compiles a nixpkgs package to
x86_64 — useful for legacy tooling that hasn't been ported to ARM.

## Limitations

- Apple Silicon only. On Intel Macs, vfkit fails to start with
  Rosetta enabled — set `ignoreIfMissing = true` if a single config
  must work on both.
- Slower than native ARM64.
- Not every x86_64 binary works; some kernel features Rosetta
  doesn't translate.

## What the Runner Emits

`lib/runners/vfkit.nix` appends:

```
--device rosetta,mountTag=rosetta[,install][,ignoreIfMissing]
```

depending on the boolean flags. The mount tag (`rosetta`) is the
hand-shake; the NixOS-side mount unit picks it up.
