# microvm.nix Wiki Page Schema

All content pages use this frontmatter:

```yaml
---
id: <category>-<name>              # unique within this wiki (kebab-case)
title: "Human Title"
category: concept | hypervisor | option | host | recipe | convention
layer: foundation | core | integration | application
tags: [searchable, keywords]
source_files:
  - /p/gh/microvm.nix/path/to/file.nix      # absolute paths
source_commit: <short-hash>
api_surface: [microvm.option.path, ...]    # Nix option paths for grep
related: [other-page-ids]
see_also: [recipe-or-pattern-ids]
---
```

## Layers

- **foundation** — primitives that don't depend on the rest of the flake
  (`lib/default.nix`, `lib/runner.nix`, hypervisor enum).
- **core** — the guest module (`nixos-modules/microvm/`): boot disk, store
  disk, mounts, interfaces, options.
- **integration** — the host module (`nixos-modules/host/`) and per-hypervisor
  runner generators (`lib/runners/*.nix`).
- **application** — task-oriented recipes that compose guest + host + hypervisor
  config (declarative VMs, SSH deploy, networking topologies).

## Source File Conventions

- Use absolute paths under `/p/gh/microvm.nix/`.
- When a topic spans guest module + handbook doc + runner code, list all
  three so refresh detects any side moving.
- For per-hypervisor pages, the runner file (`lib/runners/<hv>.nix`) is the
  source of truth for capabilities; handbook restrictions table is a summary.

## Categories

| Category | Location | Purpose |
|----------|----------|---------|
| concept | concepts/ | Mental model: MicroVM vs container, hypervisor matrix, runner package layout, store-on-disk |
| hypervisor | hypervisors/ | One page per supported hypervisor: capabilities, restrictions, options |
| option | options/ | Guest `microvm.*` option groups: cpu/mem, volumes, interfaces, shares, devices, graphics, vsock |
| host | host/ | `microvm.host.*`, systemd template services, declarative `microvm.vms`, `microvm` CLI |
| recipe | recipes/ | Task-oriented: "how do I run a MicroVM as a package", "how do I deploy via SSH", "how do I do routed networking" |
| convention | conventions/ | Runner package file layout, integration contract with host module |

## Naming

- Files: lowercase kebab-case (`cloud-hypervisor.md`, `simple-network.md`)
- IDs: `<category>-<name>` (`hypervisor-qemu`, `recipe-ssh-deploy`)
- Page titles: title case
