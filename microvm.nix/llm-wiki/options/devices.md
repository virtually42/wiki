---
id: option-devices
title: "microvm.devices"
category: option
layer: core
tags: [pci, usb, passthrough, vfio]
source_files:
  - /p/gh/microvm.nix/nixos-modules/microvm/options.nix
  - /p/gh/microvm.nix/nixos-modules/microvm/pci-devices.nix
  - /p/gh/microvm.nix/doc/src/devices.md
source_commit: 0d49083
api_surface:
  - microvm.devices
related: [hypervisor-qemu, host-systemd-services]
see_also: [recipe-device-passthrough]
---

## Shape

```nix
microvm.devices = [{
  bus = "pci";              # "pci" | "usb"
  path = "0000:01:00.0";    # PCI BDF, or USB "vendorid=0x...,productid=0x..."
  qemu = {
    id = null;
    bus = null;
    deviceExtraArgs = null;
  };
}];
```

The `qemu.*` sub-attrs are qemu-specific knobs for naming and bus
attachment.

## PCI Pass-through

```nix
microvm.devices = [
  { bus = "pci"; path = "0000:06:00.1"; }
  { bus = "pci"; path = "0000:06:10.4"; }
];
```

On the host, the `microvm-pci-devices@.service` (provided by the
host module) runs `bin/pci-setup` from the runner. That script binds
each device to `vfio-pci`. PCI passthrough is fully supported on
qemu; cloud-hypervisor has narrower support; firecracker / kvmtool /
stratovirt / alioth / vfkit do not.

## USB Pass-through

```nix
microvm.devices = [
  { bus = "usb"; path = "vendorid=0x0bda,productid=0x2838"; }
];
```

USB pass-through works on qemu only and **does not auto-configure
host permissions**. You must add udev rules:

```nix
services.udev.extraRules = ''
  SUBSYSTEM=="usb", ATTR{idVendor}=="0bda", ATTR{idProduct}=="2838", GROUP="kvm"
'';
```

Setting any device with `bus = "usb"` causes the qemu runner to
rebuild qemu with `--enable-libusb` (see
`/p/gh/microvm.nix/lib/runners/qemu.nix` — `enableLibusb`). This
also implies a heavier qemu machine model (PCIe enabled).

## Runtime Hotplug (qemu only)

`microvm.qemu.pcieRootPorts` declares PCIe root ports that can be
used for runtime device hotplug, especially on the Q35 machine
type. See `/p/gh/microvm.nix/nixos-modules/microvm/options.nix` for
the submodule.
