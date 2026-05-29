---
id: host-microvm-vms
title: "microvm.vms"
category: host
layer: integration
tags: [microvm-vms, declarative, declarative-deployment, flake, evaluatedConfig]
source_files:
  - /p/gh/microvm.nix/nixos-modules/host/options.nix
  - /p/gh/microvm.nix/nixos-modules/host/default.nix
  - /p/gh/microvm.nix/doc/src/declarative.md
source_commit: 0d49083
api_surface:
  - microvm.vms
  - microvm.vms.<name>.config
  - microvm.vms.<name>.flake
  - microvm.vms.<name>.updateFlake
  - microvm.vms.<name>.evaluatedConfig
  - microvm.vms.<name>.specialArgs
  - microvm.vms.<name>.extraModules
  - microvm.vms.<name>.nixpkgs
  - microvm.vms.<name>.pkgs
  - microvm.vms.<name>.autostart
  - microvm.vms.<name>.restartIfChanged
related: [host-host-module, host-systemd-services, recipe-declarative]
see_also: []
---

## Two Modes

A `microvm.vms.<name>` entry can be either:

- **Fully declarative** — `config` is a NixOS module evaluated in-place.
- **Declarative deployment** — `flake` points to an external
  `nixosConfigurations` entry, deployed on initial install.

The two are mutually exclusive (enforced by `assertions` in
`nixos-modules/host/default.nix`):

> vm \<name\>: Fully-declarative VMs cannot also set a flake!
> vm \<name\>: Fully-declarative VMs cannot set a updateFlake!

## Options

| Option | Type | Default | Notes |
|---|---|---|---|
| `config` | nullable module | `null` | Inline NixOS config. When set, the option's `merge` function calls `eval-config.nix` directly |
| `evaluatedConfig` | nullable unspecified | `null` | An already-evaluated config; lets you bypass the default `eval-config` invocation |
| `nixpkgs` | path | `pkgs.path` | Source for the eval-config call (only used with `config`) |
| `pkgs` | nullable unspecified | inherited `pkgs` | Package set; determines guest system. Set to `null` to instantiate a new one |
| `specialArgs` | attrs | `{}` | Extra `specialArgs` for the eval (only with `config`) |
| `extraModules` | list of deferredModule | `[]` | Modules merged into the MicroVM (only with `config`) |
| `flake` | nullable path | `null` | Source flake for declarative deployment |
| `updateFlake` | nullable str | `null` | Flake-ref string saved in `/var/lib/microvms/<name>/flake` for later `microvm -u` |
| `autostart` | bool | `true` | Add to `config.microvm.autostart` |
| `restartIfChanged` | bool | `true` when `config != null` | systemd restart-on-change |

## Fully-Declarative Example

```nix
{ microvm, ... }: {
  imports = [ microvm.host ];
  microvm.vms.my-microvm = {
    pkgs = import nixpkgs { system = "x86_64-linux"; };
    config = {
      microvm.shares = [{
        source = "/nix/store";
        mountPoint = "/nix/.ro-store";
        tag = "ro-store";
        proto = "virtiofs";
      }];
      # plus any other NixOS config
    };
  };
}
```

## Declarative-Deployment Example

```nix
microvm.vms.my-microvm = {
  flake = self;
  updateFlake = "git+file:///etc/nixos";  # remembered for `microvm -u`
};
```

`flake.nixosConfigurations.my-microvm` is read on the host;
`install-microvm-<name>.service` populates `/var/lib/microvms/my-microvm`
once and never overwrites it on subsequent rebuilds. Updates go
through `microvm -u my-microvm`.

## Build-Time Cost

Both modes increase the host's build time and closure: every
`microvm.vms.*` entry pulls in its toplevel as a `restartTrigger`.
For many VMs, prefer declarative deployment (cheaper rebuilds) +
imperative updates over fully-declarative.
