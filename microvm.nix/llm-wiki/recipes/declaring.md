---
id: recipe-declaring
title: "Declare a MicroVM in a Flake"
category: recipe
layer: application
tags: [getting-started, flake, nixosModule, microvm]
source_files:
  - /p/gh/microvm.nix/doc/src/declaring.md
  - /p/gh/microvm.nix/flake-template
source_commit: 0d49083
api_surface: [microvm.hypervisor]
related: [concept-microvm-model, recipe-run-as-package]
see_also: []
---

## Quick Start From the Template

```bash
nix flake init -t github:microvm-nix/microvm.nix
```

This drops a minimal `flake.nix` with a `nixosConfigurations.my-microvm`
entry and a packages entry exposing the runner.

## Minimal flake.nix

```nix
{
  inputs.nixpkgs.url = "github:nixos/nixpkgs/nixos-unstable";
  inputs.microvm.url = "github:microvm-nix/microvm.nix";
  inputs.microvm.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { self, nixpkgs, microvm }: {
    nixosConfigurations.my-microvm = nixpkgs.lib.nixosSystem {
      system = "x86_64-linux";
      modules = [
        microvm.nixosModules.microvm
        {
          networking.hostName = "my-microvm";
          microvm.hypervisor  = "cloud-hypervisor";

          # Don't forget at least one user
          users.users.root.password = "";

          system.stateVersion = "24.11";
        }
      ];
    };
  };
}
```

## Run It

```bash
nix run .#nixosConfigurations.my-microvm.config.microvm.declaredRunner
```

See [[recipe-run-as-package]] for adding it to `packages.<system>` so
you can `nix run .#my-microvm`.

## Defaults Worth Knowing

- 1 vCPU, 512 MB RAM, qemu hypervisor with KVM.
- Read-only erofs store disk (so no shared host store yet — see
  [[recipe-share-nix-store]]).
- No network (until you add `microvm.interfaces`).
- No shares.

## Next Steps

- Networking: [[recipe-simple-network]] or [[recipe-advanced-network]].
- Host integration: [[host-host-module]] for systemd / declarative VMs.
- Picking a hypervisor: [[concept-hypervisor-matrix]].
