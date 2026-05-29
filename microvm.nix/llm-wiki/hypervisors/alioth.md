---
id: hypervisor-alioth
title: "alioth"
category: hypervisor
layer: integration
tags: [alioth, rust, google]
source_files:
  - /p/gh/microvm.nix/lib/runners/alioth.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
source_commit: 0d49083
api_surface:
  - microvm.alioth.package
related: [concept-hypervisor-matrix]
see_also: []
---

## Overview

Google's research / experimental Rust hypervisor. Supports 9p shares
but not virtiofs; no control socket. Driver:
`/p/gh/microvm.nix/lib/runners/alioth.nix`.

## Key Options

| Option | Purpose |
|---|---|
| `microvm.alioth.package` | Defaults to `pkgs.alioth` |

## Restrictions

- **No virtiofs shares.** Use `proto = "9p"` for shares.
- **No control socket.** `microvm.socket` is ignored.
- No PCI/USB passthrough.
- No CPU emulation.

## When To Pick It

- Experimental; reach for it intentionally, not as a default.
