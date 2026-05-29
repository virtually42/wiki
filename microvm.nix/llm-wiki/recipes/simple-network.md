---
id: recipe-simple-network
title: "Simple LAN Bridge"
category: recipe
layer: application
tags: [networking, bridge, systemd-networkd, tap, lan]
source_files:
  - /p/gh/microvm.nix/doc/src/simple-network.md
source_commit: 0d49083
api_surface: []
related: [option-interfaces, recipe-advanced-network, recipe-routed-network]
see_also: []
---

## When To Use

You have plenty of IPs on the LAN and want each MicroVM directly on
the LAN behind its own MAC and IP.

## Host: Bridge `eno1 + vm-*` → `br0`

```nix
networking.useNetworkd = true;
systemd.network.enable = true;

systemd.network.networks."10-lan" = {
  matchConfig.Name = ["eno1" "vm-*"];
  networkConfig.Bridge = "br0";
};

systemd.network.netdevs."br0" = {
  netdevConfig = { Name = "br0"; Kind = "bridge"; };
};

systemd.network.networks."10-lan-bridge" = {
  matchConfig.Name = "br0";
  networkConfig = {
    Address = ["192.168.1.2/24" "2001:db8::a/64"];
    Gateway = "192.168.1.1";
    DNS = ["192.168.1.1"];
    IPv6AcceptRA = true;
  };
  linkConfig.RequiredForOnline = "routable";
};
```

The `vm-*` glob picks up MicroVM TAP interfaces by their `id`.

## Guest: TAP Interface + Static IP

```nix
microvm.interfaces = [{
  type = "tap";
  id   = "vm-test1";
  mac  = "02:00:00:00:00:01";
}];

networking.useNetworkd = true;
systemd.network.enable = true;
systemd.network.networks."20-lan" = {
  matchConfig.Type = "ether";
  networkConfig = {
    Address = ["192.168.1.3/24" "2001:db8::b/64"];
    Gateway = "192.168.1.1";
    DNS = ["192.168.1.1"];
    IPv6AcceptRA = true;
    DHCP = "no";
  };
};
```

## Docker Conflict

If the guest runs Docker, the host's `vm-*` rule will try to bridge
Docker's `veth*` interfaces too. Carve them out:

```nix
systemd.network.networks."19-docker" = {
  matchConfig.Name = "veth*";
  linkConfig.Unmanaged = true;
};
```

## Performance Notes

The doc suggests two alternatives if inter-VM communication isn't a
priority:

- `type = "macvtap"` to attach directly to the host NIC, bypassing
  the bridge.
- SR-IOV Virtual Functions for PCI passthrough.

For higher throughput on the same TAP, see [[recipe-vhost-net]].
