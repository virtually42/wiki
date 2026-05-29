# microvm.nix LLM-Wiki

Query-optimized knowledge base for `microvm.nix` — a Nix flake that
builds and runs NixOS as a MicroVM on eight hypervisors
(qemu, cloud-hypervisor, firecracker, crosvm, kvmtool, stratovirt,
alioth, vfkit).

- **Flake**: `github:microvm-nix/microvm.nix`
- **Source**: `/p/gh/microvm.nix`
- **Upstream**: https://github.com/microvm-nix/microvm.nix
- **Handbook**: https://microvm-nix.github.io/microvm.nix/ (markdown at
  `/p/gh/microvm.nix/doc/src/`)
- **Bridge**: [[sources/raw/code/microvm-nix]]

## Quick Lookup

| I want to... | Start here |
|---|---|
| Understand MicroVM vs container vs VM | [concepts/microvm-model](concepts/microvm-model.md) |
| Pick a hypervisor | [concepts/hypervisor-matrix](concepts/hypervisor-matrix.md) |
| Add the guest module to a flake | [recipes/declaring](recipes/declaring.md) |
| Run a MicroVM interactively (`nix run`) | [recipes/run-as-package](recipes/run-as-package.md) |
| Set up the host for declarative MicroVMs | [host/host-module](host/host-module.md) |
| Define MicroVMs declaratively in the host flake | [recipes/declarative](recipes/declarative.md) |
| Manage MicroVMs imperatively | [host/microvm-command](host/microvm-command.md) |
| Deploy a MicroVM update over SSH | [recipes/ssh-deploy](recipes/ssh-deploy.md) |
| Configure CPU / RAM / hotplug / balloon | [options/cpu-memory](options/cpu-memory.md) |
| Add a volume (block device) | [options/volumes](options/volumes.md) |
| Add a network interface | [options/interfaces](options/interfaces.md) |
| Share a host directory | [options/shares](options/shares.md) |
| Pass through PCI / USB devices | [options/devices](options/devices.md) |
| Configure graphics | [options/graphics](options/graphics.md) |
| Set up `systemd-networkd` bridging | [recipes/simple-network](recipes/simple-network.md) |
| Set up NAT for one public IP | [recipes/advanced-network](recipes/advanced-network.md) |
| Use routed addresses (no bridge) | [recipes/routed-network](recipes/routed-network.md) |
| Use vhost-net for fast TAP | [recipes/vhost-net](recipes/vhost-net.md) |
| Share `/nix/store` from the host | [recipes/share-nix-store](recipes/share-nix-store.md) |
| Emulate a foreign CPU | [recipes/cpu-emulation](recipes/cpu-emulation.md) |
| Run x86_64 binaries on Apple Silicon | [recipes/vfkit-rosetta](recipes/vfkit-rosetta.md) |
| Centralize MicroVM journals | [recipes/journald-merge](recipes/journald-merge.md) |
| Understand the runner package file layout | [conventions/runner-layout](conventions/runner-layout.md) |
| See per-hypervisor restrictions | [hypervisors/](hypervisors/index.md) |

## Sections

- [concepts/](concepts/index.md) — mental models (MicroVM model,
  hypervisor matrix, runner package, store-on-disk)
- [hypervisors/](hypervisors/index.md) — one page per supported
  hypervisor with capabilities and options
- [options/](options/index.md) — guest `microvm.*` option groups
- [host/](host/index.md) — host module, systemd services, `microvm` CLI
- [recipes/](recipes/index.md) — task-oriented how-tos
- [conventions/](conventions/index.md) — runner package contract with the
  host module

## Pipeline Overview

```
flake.nix
  -> nixosConfigurations.<name>      (NixOS config + microvm guest module)
  -> config.microvm.declaredRunner    (runner package, hypervisor selected)
     contains:
       bin/microvm-run                (start hypervisor)
       bin/microvm-shutdown           (graceful shutdown)
       bin/tap-up / tap-down          (TAP setup)
       bin/virtiofsd-run              (virtiofs daemons)
       bin/pci-setup                  (VFIO binding)
       share/microvm/{tap-interfaces,
                      pci-devices,
                      virtiofs/<tag>/{source,socket},
                      system}         (consumed by host module)

host with microvm.host module
  -> systemd template services:
       install-microvm-<name>         (populate /var/lib/microvms/<name>)
       microvm-tap-interfaces@        (run bin/tap-up)
       microvm-macvtap-interfaces@    (run bin/macvtap-up)
       microvm-pci-devices@           (run bin/pci-setup)
       microvm-virtiofsd@             (run bin/virtiofsd-run)
       microvm-set-booted@            (snapshot current -> booted)
       microvm@                       (run bin/microvm-run)
  -> microvms.target                  (wants all autostart entries)
```

## Cross-Platform Notes

- All hypervisors except `vfkit` are Linux-only.
- `vfkit` is macOS-only and supports **only** user-mode networking and
  **only** virtiofs shares (no 9p, no tap/bridge).
- Building the guest still requires `aarch64-linux` / `x86_64-linux` —
  on macOS you need a Linux builder. See [recipes/macos-linux-builder].
- For non-flake hosts, import `nixos-modules/host` directly from a
  `builtins.fetchGit` URL.
