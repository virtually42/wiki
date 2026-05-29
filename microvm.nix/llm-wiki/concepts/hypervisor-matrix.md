---
id: concept-hypervisor-matrix
title: "Hypervisor Matrix"
category: concept
layer: foundation
tags: [hypervisor, comparison, qemu, firecracker, cloud-hypervisor, crosvm, vfkit]
source_files:
  - /p/gh/microvm.nix/lib/default.nix
  - /p/gh/microvm.nix/README.md
  - /p/gh/microvm.nix/doc/src/shares.md
  - /p/gh/microvm.nix/doc/src/interfaces.md
source_commit: 0d49083
api_surface: [microvm.hypervisor]
related: [concept-microvm-model, hypervisor-qemu]
see_also: []
---

## Supported Hypervisors

Hard-coded in `/p/gh/microvm.nix/lib/default.nix`:

```nix
hypervisors = [
  "qemu" "cloud-hypervisor" "firecracker" "crosvm"
  "kvmtool" "stratovirt" "alioth" "vfkit"
];
```

`microvm.hypervisor` accepts any of these. The default is `"qemu"`.

## Feature Matrix

| Feature              | qemu | cloud-hyp. | firecracker | crosvm | kvmtool | stratovirt | alioth | vfkit |
|----------------------|:----:|:----------:|:-----------:|:------:|:-------:|:----------:|:------:|:-----:|
| Linux                | ✓    | ✓          | ✓           | ✓      | ✓       | ✓          | ✓      | ✗     |
| macOS                | (✓)  | ✗          | ✗           | ✗      | ✗       | ✗          | ✗      | ✓     |
| 9p shares            | ✓    | ✗          | ✗           | broken | ✓       | ✗          | ✓      | ✗     |
| virtiofs shares      | ✓    | ✓          | ✗           | ✓      | ✗       | ✗          | ✗      | ✓ (built-in) |
| `type = "tap"`       | ✓    | ✓          | ✓           | ✓      | ✓       | ✓          | ✓      | ✗     |
| `type = "macvtap"`   | ✓    | ✓          | ✗           | ✗      | ✗       | ✗          | ✗      | ✗     |
| `type = "bridge"`    | ✓    | ✗          | ✗           | ✗      | ✗       | ✗          | ✗      | ✗     |
| `type = "user"`      | ✓    | ✗          | ✗           | ✗      | ✓       | ✗          | ✗      | ✓     |
| `vhost-net` accel    | ✓    | ✗          | ✗           | ✗      | ✗       | ✗          | ✗      | ✗     |
| PCI passthrough      | ✓    | ✓          | ✗           | (✓)    | (✓)     | ✗          | ✗      | ✗     |
| USB passthrough      | ✓    | ✗          | ✗           | ✗      | ✗       | ✗          | ✗      | ✗     |
| Control socket       | ✓    | ✓          | ✓           | ✓      | ✗       | ✗          | ✗      | ✓     |
| CPU emulation        | ✓    | ✗          | ✗           | ✗      | ✗       | ✗          | ✗      | ✗     |
| Hugepage memory      | (✓)  | ✓          | ✗           | ✗      | ✗       | ✗          | ✗      | ✗     |
| Virtio-mem hotplug   | ✓    | ✓          | ✗           | ✗      | ✗       | ✗          | ✗      | ✗     |
| Balloon              | ✓    | ✓          | ✓           | ✗      | ✗       | ✗          | ✗      | ✓     |
| AF_VSOCK             | ✓    | ✓          | ✓           | ✓      | ✗       | ✗          | ✗      | ✓     |
| Graphics             | ✓    | ✓ (gtk)    | ✗           | ✓      | ✗       | ✗          | ✗      | ✓ (cocoa) |
| Rosetta (x86_64-on-ARM) | ✗ | ✗          | ✗           | ✗      | ✗       | ✗          | ✗      | ✓     |

Source: README hypervisor table + per-runner `.nix` files in
`/p/gh/microvm.nix/lib/runners/`. The `throw` calls in those files
are the canonical "not supported" markers.

## Decision Flow

1. **macOS host?** → `vfkit`. No other choice; only user-mode
   networking; only virtiofs shares.
2. **Need foreign CPU?** → `qemu`. Only qemu supports `microvm.cpu`
   for emulation. See [[recipe-cpu-emulation]].
3. **Need PCI passthrough?** → `qemu` (most mature) or
   `cloud-hypervisor`.
4. **Need 9p (no virtiofsd setup)?** → `qemu` or `kvmtool` or `alioth`.
   Most other hypervisors require virtiofs and a sidecar daemon.
5. **Need maximum network throughput on Linux?** → `qemu` with
   `tap.vhost = true`. See [[recipe-vhost-net]].
6. **Need minimal attack surface?** → `firecracker` is the smallest;
   limited features (TAP only, no shares).
7. **Default** → `qemu`. Most featureful, most documented, and
   accepts every `microvm.*` option.

## What "no control socket" Means

`kvmtool`, `stratovirt`, and `alioth` cannot accept runtime commands.
Implications:

- `microvm.socket` is ignored.
- `microvm-balloon` cannot adjust memory at runtime.
- `microvm-shutdown` triggers shutdown via signal rather than ACPI;
  guest kernel must handle reboot=k correctly.
