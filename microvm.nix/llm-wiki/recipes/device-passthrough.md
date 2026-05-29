---
id: recipe-device-passthrough
title: "PCI / USB Pass-Through"
category: recipe
layer: application
tags: [pci, usb, passthrough, vfio, udev]
source_files:
  - /p/gh/microvm.nix/doc/src/devices.md
  - /p/gh/microvm.nix/nixos-modules/microvm/pci-devices.nix
source_commit: 0d49083
api_surface: [microvm.devices]
related: [option-devices, hypervisor-qemu]
see_also: []
---

## Pre-flight

- qemu is the only fully-supported hypervisor for both PCI and USB.
- Identify the device on the host: `lspci -nn` for PCI, `lsusb` for
  USB. Note the BDF (`0000:06:00.1`) or the
  `vendorid=0xVVVV,productid=0xPPPP` pair.
- Confirm the host's IOMMU is enabled (`intel_iommu=on` or
  `amd_iommu=on` in `boot.kernelParams`).
- Make sure no host driver currently owns the PCI device — IOMMU
  group binding to `vfio-pci` requires the device to be free.

## PCI Example

Guest:

```nix
microvm.devices = [
  { bus = "pci"; path = "0000:06:00.1"; }
  { bus = "pci"; path = "0000:06:10.4"; }
];
```

The host module starts `microvm-pci-devices@<name>.service`, which
runs `bin/pci-setup` from the runner. That binds each device to
`vfio-pci` before the VM starts. Permissions are managed by the
host module — no extra udev config needed for PCI.

## USB Example

Guest:

```nix
microvm.devices = [
  # Realtek RTL2838 DVB-T
  { bus = "usb"; path = "vendorid=0x0bda,productid=0x2838"; }
];
```

Host permissions are **not** automatic. Add a udev rule:

```nix
services.udev.extraRules = ''
  SUBSYSTEM=="usb", ATTR{idVendor}=="0bda", ATTR{idProduct}=="2838", GROUP="kvm"
'';
```

Setting any `bus = "usb"` device causes the qemu runner to rebuild
qemu with `--enable-libusb` (see `enableLibusb` in
`/p/gh/microvm.nix/lib/runners/qemu.nix`). This is one of the few
times the closure size noticeably grows.

## qemu Sub-Attrs

For complex setups (Intel iGPU passthrough, multiple devices on the
same guest bus), the `qemu = { id; bus; deviceExtraArgs; }`
sub-attrs let you control naming / placement:

```nix
{ bus = "pci";
  path = "0000:01:01.0";
  qemu.id = "hostId";
  qemu.deviceExtraArgs = "x-igd-opregion=on";
}
```

## Runtime Hotplug

If you need to add/remove devices at runtime, expose PCIe root ports
via `microvm.qemu.pcieRootPorts` (Q35-class machine type only) and
attach devices through the qemu monitor / control socket.
