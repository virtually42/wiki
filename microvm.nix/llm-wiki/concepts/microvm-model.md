---
id: concept-microvm-model
title: "What a MicroVM Is"
category: concept
layer: foundation
tags: [microvm, virtio, isolation, container-alternative]
source_files:
  - /p/gh/microvm.nix/doc/src/intro.md
  - /p/gh/microvm.nix/README.md
source_commit: 0d49083
api_surface: []
related: [concept-hypervisor-matrix, concept-compartmentalization]
see_also: [recipe-declaring]
---

## What a MicroVM Is

A **MicroVM** is a full virtual machine, but with the emulated device
surface replaced by **virtio** interfaces optimised for VM-only use.
The guest gets a real kernel and a separate isolation boundary; the
host pays only the hypervisor + virtio overhead instead of full QEMU
device emulation.

`microvm.nix` builds NixOS guests for eight hypervisors and provides
a `host` module that runs them as systemd services with bind-mounted
state under `/var/lib/microvms/<name>/`.

## Defaults

- 1 vCPU, 512 MB RAM (`microvm.vcpu`, `microvm.mem`)
- Read-only root disk: erofs (or squashfs) holding just the guest
  closure
- Hypervisor: `qemu` with KVM on Linux
- Network: none until you add `microvm.interfaces`
- Shares: none until you add `microvm.shares`

The root disk can be replaced by sharing the host's `/nix/store` over
9p or virtiofs — see [[recipe-share-nix-store]]. A writable Nix store
needs an overlay; see [[recipe-writable-store-overlay]].

## Why Not a Container

- Containers share the host kernel; MicroVMs run their own. Attack
  surface is the hypervisor + virtio drivers, not the full Linux
  syscall surface.
- `nixos-container` exists, but maintenance on one container can
  destabilise others. MicroVMs isolate the *kernel and userspace*
  rather than just userspace.
- Trade-off: MicroVMs have a fixed RAM allocation by default
  (`microvm.mem`); ballooning / virtio-mem can recover unused RAM but
  is hypervisor-specific. See [[option-cpu-memory]].

## Why Not Plain QEMU

- The MicroVM machine type and virtio-only device set boot faster and
  use less RAM than emulating a PC.
- Several hypervisors (Firecracker, cloud-hypervisor, crosvm, alioth,
  stratovirt) are written in Rust and specifically scoped to this
  use-case. See [[concept-hypervisor-matrix]] for picking one.

## How a MicroVM Gets Run

1. You write a `nixosConfiguration` that imports
   `microvm.nixosModules.microvm`.
2. `microvm-lib.buildRunner` (see
   `/p/gh/microvm.nix/lib/runner.nix`) generates a runner package
   exposed as `config.microvm.declaredRunner`.
3. You either:
   - `nix run` the runner directly — interactive use, no host module
     setup, no TAP / virtiofsd prep ([[recipe-run-as-package]]); or
   - Run it under the host module's `microvm@.service` — full
     systemd integration with TAP / virtiofsd / PCI setup
     ([[recipe-declarative]]).
