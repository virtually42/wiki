# Guest Options

Options under `microvm.*` set on the guest NixOS configuration. Defined
in `/p/gh/microvm.nix/nixos-modules/microvm/options.nix`.

| Page | Options covered |
|---|---|
| [hypervisor-selection](hypervisor-selection.md) | `microvm.hypervisor`, `microvm.declaredRunner`, `microvm.runner` |
| [cpu-memory](cpu-memory.md) | `vcpu`, `mem`, `cpu`, `hugepageMem`, `hotplugMem`, `hotpluggedMem`, `balloon`, `initialBalloonMem`, `deflateOnOOM` |
| [volumes](volumes.md) | `microvm.volumes` submodule list (image, size, fsType, autoCreate, readOnly, …) |
| [interfaces](interfaces.md) | `microvm.interfaces` submodule list (type, id, mac, macvtap, bridge, tap.vhost) |
| [shares](shares.md) | `microvm.shares` submodule list (9p vs virtiofs, source, mountPoint, securityModel) |
| [devices](devices.md) | `microvm.devices` for PCI/USB passthrough |
| [graphics](graphics.md) | `microvm.graphics.{enable,backend,socket,crosvmPackage}` |
| [vsock](vsock.md) | `microvm.vsock.cid` for AF_VSOCK |
| [store-disk](store-disk.md) | `storeOnDisk`, `storeDiskType`, `storeDiskErofsFlags`, `storeDiskSquashfsFlags`, `writableStoreOverlay` |
| [forward-ports](forward-ports.md) | `microvm.forwardPorts` (qemu user networking only) |
| [misc](misc.md) | `socket`, `preStart`, `extraArgsScript`, `user`, `kernel`, `initrdPath`, `kernelParams`, `optimize.enable`, `guest.enable`, `credentialFiles`, `machineId`, `registerWithMachined`, `binScripts`, `prettyProcnames`, `systemSymlink` |
| [hypervisor-extra-args](hypervisor-extra-args.md) | `microvm.<hypervisor>.{package,extraArgs,…}` per-hypervisor knobs |
| [virtiofsd](virtiofsd.md) | `microvm.virtiofsd.*` |
