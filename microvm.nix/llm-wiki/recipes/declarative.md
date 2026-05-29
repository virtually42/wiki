---
id: recipe-declarative
title: "Declarative MicroVMs in the Host Flake"
category: recipe
layer: application
tags: [declarative, microvm-vms, flake, fully-declarative, deployment]
source_files:
  - /p/gh/microvm.nix/doc/src/declarative.md
  - /p/gh/microvm.nix/nixos-modules/host/options.nix
source_commit: 0d49083
api_surface: [microvm.vms]
related: [host-microvm-vms, host-host-module, host-microvm-command]
see_also: [recipe-ssh-deploy]
---

## Two Variants

| Variant | When | Updates via |
|---|---|---|
| Fully-declarative (`config`) | Small fleets; everything in one host flake | `nixos-rebuild switch` |
| Declarative-deployment (`flake`) | VMs that should outlive host rebuilds and be updated separately | `microvm -u <name>` |

You **cannot** set both `config` and `flake` on the same VM — the
host module's assertions reject it.

## Fully-Declarative

```nix
{ microvm, nixpkgs, ... }: {
  imports = [ microvm.host ];

  microvm.vms.my-microvm = {
    pkgs = import nixpkgs { system = "x86_64-linux"; };

    config = {
      microvm.hypervisor = "qemu";

      # Share host /nix/store — required to keep image size sane
      microvm.shares = [{
        source = "/nix/store";
        mountPoint = "/nix/.ro-store";
        tag = "ro-store";
        proto = "virtiofs";
      }];

      networking.hostName = "my-microvm";  # (defaults to the attr name)
      users.users.root.password = "";
      system.stateVersion = "24.11";
    };
  };
}
```

On `nixos-rebuild switch`, the host:

1. Evaluates the VM's NixOS config in-place.
2. Builds the runner derivation.
3. `install-microvm-my-microvm.service` symlinks `current` to the runner.
4. `microvm-set-booted@my-microvm.service` snapshots `booted`.
5. `microvm@my-microvm.service` starts.

Subsequent rebuilds **do** re-run install and restart the VM (because
`restartIfChanged` defaults to `true` for fully-declarative VMs).

## Declarative-Deployment

```nix
microvm.vms.my-microvm = {
  flake = self;                       # this host's own flake
  updateFlake = "git+file:///etc/nixos";  # remembered for `microvm -u`
};
```

On initial rebuild, `install-microvm-<name>.service` populates the
state directory and writes the `flake` ref. **Subsequent rebuilds
skip the install** (`ConditionPathExists = !${stateDir}/${name}`).
Update with:

```bash
microvm -u my-microvm           # build new runner
microvm -u -R my-microvm        # build + restart
```

## Side Note — Build Cost

Both variants pull each VM's `system.build.toplevel` into the host
build as a `restartTrigger`. For many VMs this can balloon host
build time. For fleets, declarative-deployment (the second variant)
is the cheaper rebuild pattern.

## Autostart

`microvm.vms.<name>.autostart = true` (default) folds the VM into
`microvm.autostart`. See [[host-autostart]].
