# Recipes

Task-oriented how-tos.

| Page | Task |
|---|---|
| [declaring](declaring.md) | Add the `microvm` guest module to a `flake.nix` |
| [run-as-package](run-as-package.md) | Run a MicroVM interactively (`nix run`) |
| [declarative](declarative.md) | Define MicroVMs in the host flake (fully-declarative vs declarative-deployment) |
| [simple-network](simple-network.md) | Bridge MicroVMs onto a LAN with `systemd-networkd` |
| [advanced-network](advanced-network.md) | Internal bridge + NAT for one public IP |
| [routed-network](routed-network.md) | Host routes per VM (no bridge) for isolation |
| [vhost-net](vhost-net.md) | Enable `tap.vhost = true` for ~10 Gbps TAP throughput |
| [share-nix-store](share-nix-store.md) | Mount host `/nix/store` into the MicroVM |
| [writable-store-overlay](writable-store-overlay.md) | Build Nix derivations inside the MicroVM |
| [cpu-emulation](cpu-emulation.md) | Run a foreign-architecture MicroVM (qemu only) |
| [vfkit-rosetta](vfkit-rosetta.md) | Run x86_64 binaries in an ARM64 VM on Apple Silicon |
| [ssh-deploy](ssh-deploy.md) | `microvm.deploy.rebuild` — evaluate local, build remote |
| [journald-merge](journald-merge.md) | Merge MicroVM journals into the host's `journalctl -m` |
| [device-passthrough](device-passthrough.md) | PCI / USB passthrough |
| [macos-linux-builder](macos-linux-builder.md) | Build NixOS guests on macOS hosts |
