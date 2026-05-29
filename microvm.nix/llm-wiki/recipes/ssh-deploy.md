---
id: recipe-ssh-deploy
title: "Deploy a MicroVM Over SSH"
category: recipe
layer: application
tags: [ssh-deploy, deploy, rebuild, switch-to-configuration, evaluate-local-build-remote]
source_files:
  - /p/gh/microvm.nix/doc/src/ssh-deploy.md
  - /p/gh/microvm.nix/nixos-modules/microvm/ssh-deploy.nix
source_commit: 0d49083
api_surface:
  - microvm.deploy.rebuild
  - microvm.deploy.installOnHost
  - microvm.deploy.sshSwitch
related: [host-microvm-command, host-microvm-vms]
see_also: []
---

## When To Use

You develop a MicroVM config on your laptop, want to update a running
production VM without:

- Building the full closure locally and `nix copy`ing (drains the
  laptop battery, heavy network).
- Pushing the repo to the remote and building there with no
  reference to your local `--override-input`s.

`microvm.deploy.rebuild` does **evaluate locally, build remotely,
activate in-guest**.

## One-Shot Form

```bash
nix run .#nixosConfigurations.my-microvm.config.microvm.deploy.rebuild \
  root@host.example.com root@my-microvm.example.com switch
```

Arg order: **host SSH target**, **MicroVM SSH target**, then the
final argument is the `switch-to-configuration` action (`switch`,
`boot`, `test`, `dry-activate`).

## What Happens Internally

`microvm.deploy.rebuild` composes two pieces:

1. **`microvm.deploy.installOnHost`** — evaluates the system's
   derivations locally, transfers them and their dependencies to the
   remote host, builds there, installs under `/var/lib/microvms/$NAME`
   so the host module's systemd services can pick it up.
2. Then one of:
   - **`microvm.deploy.sshSwitch`** — if the host's `/nix/store` is
     mounted in the guest and SSH is up: switch in the guest.
   - Otherwise: restart `microvm@$NAME.service` on the host.

## `microvm.deploy.sshSwitch` Details

For a clean activation it does more than `switch-to-configuration`:

1. Compares `config.networking.hostName` against the running system
   (safety check — prevents activating the wrong system into a VM).
2. Imports the Nix DB registration of the new closure — important
   when using `microvm.writableStoreOverlay`.
3. Installs the new system into `/nix/var/nix/profiles/system`
   (optional but expected by tooling).
4. Runs `switch-to-configuration` with the requested action.

## Alternatives the Doc Calls Out

| Alternative | Drawback |
|---|---|
| Build locally + `nix copy` | Laptop battery, network |
| `git push` then build remotely | Operators see "weird" repo state; loses local `--override-input` |

`microvm.deploy.rebuild` is the recommended path for production
updates.
