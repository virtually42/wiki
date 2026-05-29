---
id: concept-compartmentalization
title: "Why MicroVMs Over `nixos-container`"
category: concept
layer: foundation
tags: [compartmentalization, container-alternative, isolation, security]
source_files:
  - /p/gh/microvm.nix/doc/src/intro.md
source_commit: 0d49083
api_surface: []
related: [concept-microvm-model]
see_also: []
---

## The Argument

The intro to microvm.nix lays out the design motivation:

> NixOS makes running services a breeze. Being able to quickly rollback
> configuration is a life-saver. Not so much however on systems that are
> shared by multiple services where maintenance of one affects others.

A monolithic NixOS host runs many services in one PID namespace and one
kernel. A `nixos-rebuild switch` touches every service unit and can
affect unrelated workloads. MicroVMs cut this:

- Each MicroVM is its own NixOS system with its own update cycle.
- The host's `nixos-rebuild switch` does **not** restart running
  MicroVMs (the `install-microvm-<name>.service` unit checks
  `ConditionPathExists` for declarative-deployment VMs — see
  [[host-systemd-services]]).
- Maintenance is per-VM via the `microvm` CLI or per-service
  `systemctl restart microvm@<name>`.

## Why Not Containers

Containers share the host kernel — one big attack surface across a
fleet of LSM rules, seccomp filters, capability sets. MicroVMs run a
separate kernel; the host only trusts the hypervisor and virtio
drivers.

Performance-wise containers win at memory flexibility, but MicroVMs
catch up via virtio-mem hotplug and ballooning (qemu, cloud-hypervisor)
— see [[option-cpu-memory]].

## When MicroVMs Are Overkill

- All your services already share state and need to be restarted
  together → use a single host.
- You need sub-second cold start of thousands of workloads → use
  containers; even Firecracker is slower than a tuned container
  runtime.
- You have strict memory pressure across many small workloads and
  cannot accept fixed `microvm.mem` defaults → reach for containers
  or accept ballooning complexity.
