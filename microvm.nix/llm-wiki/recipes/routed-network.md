---
id: recipe-routed-network
title: "Routed Per-VM Addresses"
category: recipe
layer: application
tags: [networking, routed, host-routes, isolation, no-bridge]
source_files:
  - /p/gh/microvm.nix/doc/src/routed-network.md
source_commit: 0d49083
api_surface: []
related: [recipe-simple-network, recipe-advanced-network]
see_also: []
---

## Why

Shared L2 (a bridge) lets a compromised VM:

- Forge MAC addresses
- Run a rogue DHCP server
- ARP / NDP spoof its neighbours
- Meddle with link-local multicast

To eliminate this, drop the bridge and route each VM as a /32 (v4)
or /128 (v6) host route.

## Host: One `.network` per VM, Generated

```nix
{ lib, ... }:
let maxVMs = 64; in {
  networking.useNetworkd = true;

  systemd.network.networks = builtins.listToAttrs (
    map (index: {
      name = "30-vm${toString index}";
      value = {
        matchConfig.Name = "vm${toString index}";
        address = [
          "10.0.0.0/32"
          "fec0::/128"
        ];
        routes = [
          { Destination = "10.0.0.${toString index}/32"; }
          { Destination = "fec0::${lib.toHexString index}/128"; }
        ];
        networkConfig = {
          IPv4Forwarding = true;
          IPv6Forwarding = true;
        };
      };
    }) (lib.genList (i: i + 1) maxVMs)
  );
}
```

`maxVMs` is cheap to bump — it just generates more `.network` files.

## Host: NAT

```nix
networking.nat = {
  enable = true;
  internalIPs = [ "10.0.0.0/24" ];   # one CIDR rather than per-tap rules
  externalInterface = "enp0s3";
};
```

## Guest

Each guest gets a unique `index`. **Reuse means broken routing**, so
keep a central file with each VM's index or write a NixOS assertion.

```nix
{ lib, ... }:
let
  index = 5;
  mac = "00:00:00:00:00:01";
in {
  microvm.interfaces = [{
    id = "vm${toString index}";
    type = "tap";
    inherit mac;
  }];

  networking.useNetworkd = true;
  systemd.network.networks."10-eth" = {
    matchConfig.MACAddress = mac;
    address = [
      "10.0.0.${toString index}/32"
      "fec0::${lib.toHexString index}/128"
    ];
    routes = [
      { Destination = "10.0.0.0/32"; GatewayOnLink = true; }
      { Destination = "0.0.0.0/0"; Gateway = "10.0.0.0"; GatewayOnLink = true; }
      { Destination = "::/0"; Gateway = "fec0::"; GatewayOnLink = true; }
    ];
    networkConfig = {
      DNS = [ "9.9.9.9" "149.112.112.112" "2620:fe::fe" "2620:fe::9" ];
    };
  };
}
```

## Tradeoffs

| Pro | Con |
|---|---|
| No L2 attacks between VMs | More config; one `.network` per VM |
| No DHCP server needed | DNS must be set explicitly |
| Smallest waste of address space (no subnet network/broadcast) | Migration scripts need to track the `index` |
