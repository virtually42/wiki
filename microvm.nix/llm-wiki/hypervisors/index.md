# Hypervisors

One page per supported hypervisor. All except `vfkit` are Linux-only;
`vfkit` is macOS-only.

| Hypervisor | Language | Major restrictions |
|---|---|---|
| [qemu](qemu.md) | C | most featureful; supports `vhost-net`, all interface types, 9p+virtiofs |
| [cloud-hypervisor](cloud-hypervisor.md) | Rust | no 9p shares |
| [firecracker](firecracker.md) | Rust | no 9p/virtiofs shares, no shares at all; TAP-only networking |
| [crosvm](crosvm.md) | Rust | 9p shares broken |
| [kvmtool](kvmtool.md) | C | no virtiofs shares, no control socket |
| [stratovirt](stratovirt.md) | Rust | no 9p/virtiofs shares, no control socket |
| [alioth](alioth.md) | Rust | no virtiofs shares, no control socket |
| [vfkit](vfkit.md) | Go | macOS only, no 9p, no tap/bridge networking |

See [[concepts/hypervisor-matrix]] for a feature comparison and decision
flow. The set of hypervisors is hard-coded in
`/p/gh/microvm.nix/lib/default.nix` (`hypervisors` list).
