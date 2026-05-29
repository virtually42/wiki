---
id: recipe-journald-merge
title: "Centralize MicroVM journals on the Host"
category: recipe
layer: application
tags: [journald, machine-id, virtiofs, observability]
source_files:
  - /p/gh/microvm.nix/doc/src/faq.md
source_commit: 0d49083
api_surface: [microvm.shares, microvm.machineId]
related: [option-shares, option-misc]
see_also: []
---

## Idea

journald identifies hosts by `/etc/machine-id`. If you mount each
MicroVM's `/var/log/journal` from a host directory and symlink it
back into the host's `/var/log/journal/$machineId`, the host's
`journalctl -m` (merge) picks up the MicroVM logs natively.

## Guest Side

```nix
microvm.shares = [{
  source = "/var/lib/microvms/${config.networking.hostName}/journal";
  mountPoint = "/var/log/journal";
  tag = "journal";
  proto = "virtiofs";
  socket = "journal.sock";
}];
```

Also set `microvm.machineId` (or rely on the deterministic
hash-derived default) so the guest's `/etc/machine-id` is stable.

## Host Side

```nix
systemd.tmpfiles.rules = map (vmHost:
  let machineId = self.lib.addresses.machineId.${vmHost}; in
    "L+ /var/log/journal/${machineId} - - - - /var/lib/microvms/${vmHost}/journal/${machineId}"
) (builtins.attrNames self.lib.addresses.machineId);
```

The pattern assumes a `self.lib.addresses.machineId` attrset
mapping VM names to their machine IDs — adjust to your own
provenance source.

## Reading Logs

```bash
journalctl -m            # merge mode: show local + linked machine IDs
journalctl -m _MACHINE_ID=<vm-machine-id>
```

## Trade-Offs

- One symlink per VM; small ops cost.
- No network transport needed — relies on virtiofs share + machine-id
  uniqueness.
- VM logs survive VM restarts because the journal lives on the host
  side of the share.
