---
id: option-hypervisor-selection
title: "Hypervisor Selection Options"
category: option
layer: core
tags: [hypervisor, runner, declaredRunner]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/default.nix
  - /p/gh/microvm.nix/doc/src/output-options.md
source_commit: 0d49083
api_surface:
  - microvm.hypervisor
  - microvm.runner
  - microvm.declaredRunner
related: [concept-runner-package]
see_also: []
---

## `microvm.hypervisor`

Type: enum (one of `lib.hypervisors`).
Default: `"qemu"`.

Selects which runner `microvm.declaredRunner` resolves to. Set it,
then build / run `microvm.declaredRunner`. The enum is hard-coded
in `/p/gh/microvm.nix/lib/default.nix`.

## `microvm.runner`

Type: `attrsOf package`.

Generated runner for **every** hypervisor regardless of
`microvm.hypervisor`. Useful for testing alternate hypervisors
without changing the option:

```bash
nix run .#nixosConfigurations.my-microvm.config.microvm.runner.firecracker
```

## `microvm.declaredRunner`

Type: `package`.
Default: `microvm.runner.${microvm.hypervisor}`.

The canonical entry point in production. Other options
(e.g. `microvm.optimize`) may key off `microvm.hypervisor`, so
building anything other than `declaredRunner` risks inconsistent
defaults.
