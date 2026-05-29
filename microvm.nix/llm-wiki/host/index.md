# Host Module

The `nixosModules.host` module turns a NixOS host into a microvm.nix
runner. Defined in `/p/gh/microvm.nix/nixos-modules/host/`.

| Page | Purpose |
|---|---|
| [host-module](host-module.md) | Importing the host module; `microvm.host.*` options |
| [systemd-services](systemd-services.md) | All `microvm-*@.service` template units and `microvms.target` |
| [microvm-vms](microvm-vms.md) | `microvm.vms.<name>.*` — declarative VM definitions |
| [microvm-command](microvm-command.md) | The imperative `microvm` CLI |
| [state-directory](state-directory.md) | Layout of `/var/lib/microvms/<name>/` |
| [autostart](autostart.md) | `microvm.autostart`, `microvm.vms.<name>.autostart` |
