---
id: recipe-advanced-network
title: "Internal Bridge + NAT"
category: recipe
layer: application
tags: [networking, nat, bridge, internal, port-forwarding]
source_files:
  - /p/gh/microvm.nix/doc/src/advanced-network.md
source_commit: 0d49083
api_surface: []
related: [recipe-simple-network, recipe-routed-network, option-forward-ports]
see_also: []
---

## When To Use

You rent a server with one public IP, no LAN. Build an internal
bridge for VMs and NAT them to the Internet.

## Host: Internal Bridge

```nix
systemd.network.netdevs."10-microvm".netdevConfig = {
  Kind = "bridge";
  Name = "microvm";
};

systemd.network.networks."10-microvm" = {
  matchConfig.Name = "microvm";
  networkConfig = {
    DHCPServer = true;
    IPv6SendRA = true;
  };
  addresses = [
    { addressConfig.Address = "10.0.0.1/24"; }
    { addressConfig.Address = "fd12:3456:789a::1/64"; }
  ];
  ipv6Prefixes = [{ ipv6PrefixConfig.Prefix = "fd12:3456:789a::/64"; }];
};

# DHCP server inbound
networking.firewall.allowedUDPPorts = [ 67 ];
```

The doc recommends switching off `DHCPServer = true` for production
and using static, versioned IPs instead.

## Attach TAPs

```nix
systemd.network.networks."11-microvm" = {
  matchConfig.Name = "vm-*";
  networkConfig.Bridge = "microvm";
};
```

## NAT to the Outside

```nix
networking.nat = {
  enable = true;
  enableIPv6 = true;                  # NAT66; remove if you route a proper /64
  externalInterface = "eth0";
  internalInterfaces = [ "microvm" ];
};
```

## Inbound Port Forwarding

For services in the MicroVMs to be reachable from the public Internet:

```nix
networking.nat.forwardPorts = [
  { proto = "tcp"; sourcePort = 80;  destination = "10.0.0.10:80"; }
  { proto = "tcp"; sourcePort = 443; destination = "10.0.0.10:443"; }
];
```

This is **host-side** NAT forwarding, not `microvm.forwardPorts`
(which is SLiRP user-networking only — see [[option-forward-ports]]).

## Compare With

- [[recipe-simple-network]] — direct LAN attachment, no NAT.
- [[recipe-routed-network]] — per-VM host routes, no shared L2 (more
  isolated, more setup).
