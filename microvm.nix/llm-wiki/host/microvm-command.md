---
id: host-microvm-command
title: "The `microvm` CLI"
category: host
layer: integration
tags: [microvm-command, cli, imperative, update, list, create]
source_files:
  - /p/gh/microvm.nix/pkgs/microvm-command.nix
  - /p/gh/microvm.nix/doc/src/microvm-command.md
source_commit: 0d49083
api_surface: []
related: [host-host-module, host-microvm-vms, host-state-directory]
see_also: [recipe-ssh-deploy]
---

## Where It Comes From

The host module installs `pkgs.callPackage ../../pkgs/microvm-command.nix`
on `environment.systemPackages`. It's a shell wrapper that
manipulates `/var/lib/microvms/<name>/{current,booted,flake}`.

## Operations

### Create

```bash
microvm -f git+https://example.org/infra -c my-microvm
```

- Builds the runner from the flake's `nixosConfigurations.my-microvm`.
- Creates `/var/lib/microvms/my-microvm/`, symlinks `current` to the
  runner, writes the flake ref to `flake`.
- If `-f` is omitted, defaults to `git+file:///etc/nixos`.

### Update

```bash
microvm -u my-microvm           # build
microvm -u -R my-microvm        # build + restart if changed
```

*Updating* re-builds against the saved flake ref — it **does not**
refresh nixpkgs. To update package versions, `nix flake update` the
source flake first.

### List

```bash
microvm -l
```

Reads each VM's current and booted system versions, evaluates the
flake to compare. Slow but useful. Quick alternative:

```bash
ls -l /var/lib/microvms/*/{current,booted}/share/microvm/system
```

### Remove

```bash
systemctl stop microvm@$NAME
rm -rf /var/lib/microvms/$NAME
```

The `microvm@.service` `ConditionPathExists` is the runner script;
removing the state directory makes the unit a no-op on next start.

## Enabling Autostart

Declaratively only — `microvm` itself does not flip autostart:

```nix
microvm.autostart = [ "my-microvm" ];
```

## CI Pattern

`/p/gh/microvm.nix/doc/src/faq.md` shows an `update-microvm`
shell script you'd install via
`pkgs.writeShellScriptBin` to:

1. For each VM, check whether the saved `flake` matches a CI flake ref.
2. Curl Hydra's latest job output, `nix copy` it down.
3. Diff `current` against the new closure with
   `nix store diff-closures`.
4. If different, swap `current`, mark `old`, restart
   `microvm@$NAME`.
