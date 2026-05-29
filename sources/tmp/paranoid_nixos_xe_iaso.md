# Raw extraction — "Paranoid NixOS Setup"

**Source URL:** https://xeiaso.net/blog/paranoid-nixos-2021-07-18/
**Author:** Xe Iaso
**Publication date:** 2021-07-18
**Length (stated):** 4278 words, ~16 minutes
**Tags (author):** paranoid, noexec
**Fetched:** 2026-05-29
**Method:** WebFetch (HTML → structured markdown). Code blocks
preserved verbatim. Prose paraphrased only where necessary; the
author's wording is preferred and direct quotations are placed in
blockquotes. Staged here for human triage; promote to
`sources/raw/docs/` if the article is to be preserved as raw source.

**Author disclaimer (verbatim from post):** "The author is a Tailscale
employee. Tailscale did not review this post for accuracy or content,
though this setup is based on conversations with a Tailscale
coworker."

---

## High-level Ideas

The setup assumes the following design intent (author's bullets):

- It should be very difficult to get in as a passive attacker
- But the defense doesn't stop at "just hope they don't get in"
- It should be annoying for attackers to get a user-level shell
- But ensure they'll be able to anyways if they're dedicated enough
- It should be difficult for attackers to run their own code on the system
- But assume that it could happen and make evidence of that very loud
- It should be aggravating for attackers to access the package manager
- But ensure they can't do anything very easily even if they can access the package manager itself

Additional goals:

- Make the system only manageable by a central management system such as morph or nixops
- Only make SSH visible over a VPN of some kind (Tailscale or another WireGuard setup)
- Mount the root filesystem on a tmpfs
- Have explicitly defined persistent folders
- Mark everything as `noexec` except the mount that `/nix/store` is on
- Don't make the system too difficult to use in the process

---

## Low-hanging Fruit

### The Firewall

```nix
# hosts/meeka/firewall.nix
{ ... }:

{
  networking.firewall.enable = true;
}
```

### VPN for Access

```nix
# hosts/meeka/tailscale.nix
{ ... }:

{
  services.tailscale.enable = true;

  # Tell the firewall to implicitly trust packets routed over Tailscale:
  networking.firewall.trustedInterfaces = [ "tailscale0" ];
}
```

After booting, log in via `tailscale up`. ACLs can isolate the server
further. A second access path is advisable. Production-facing
paranoid servers should only be reachable over a VPN.

---

## Locking Down the Hatches

### Each Service Gets its own User Account

> "In this world, a 'service' is a human-oriented view of 'computer
> does the thing I want it to do'. This website you're reading this
> post on could be one service, and it should have a separate account
> from other services."

### Lock Down Services Within Systemd

systemd manages a huge chunk of NixOS. The `Protect*` unit options
in `systemd.exec(5)` lock down permissions at the resource and
syscall level. `systemd-analyze security yourservicename.service`
surfaces more options to look up in systemd docs.

#### `ProtectHome` / `ProtectSystem`

Change how systemd presents critical system files and `/home` to a
given process. Used to remove the ability for a service to modify
system files or peek into user home directories, even as root.

#### `NoNewPrivileges`

If set, child processes of this service cannot gain more privileges,
period. Even if the child is a suid binary.

> "A suid binary is a binary that has the suid flag set. This makes
> the Linux kernel change the active user field of that binary to the
> owner of the binary when you run it. This is a huge part of how the
> magic behind sudo and ping works."

#### `ProtectKernel{Logs,Modules,Tunables}`

- `ProtectKernelLogs` — service cannot access the kernel message
  buffer (`dmesg`, `/proc/kmsg`).
- `ProtectKernelModules` — service cannot load or unload kernel modules.
- `ProtectKernelTunables` — `/proc` and `/sys` tunables become read-only.

> "These settings prevent the service's view of the system from having
> too much detail, which can make the attacking process more annoying.
> The goal here isn't to make the system attack-proof, nothing is.
> The goal is to annoy the attacker enough that they give up. You may
> also want to look into `InaccessiblePaths` to block away other
> folders that you deem 'forbidden' as facts and circumstances demand."

### Lock Down Nix Access

Nix is the package manager for NixOS. Users invoking Nix gain access
to compilers and scripting languages — useful for exploit tooling.
`nix.allowedUsers` restricts who can talk to the Nix daemon.

```nix
# configuration/meeka/nix.nix
{ ... }:

{
  nix.allowedUsers = [ "@wheel" ];
}
```

Or, more restrictively:

```nix
# configuration/meeka/nix.nix
{ ... }:

{
  nix.allowedUsers = [ "root" ];
}
```

To block the NixOS cache CDN externally if untrusted, block the
fastly range `151.101.0.0/16`.

> "Do this firewall change on the level above the NixOS machine
> itself, just in case the machine gets owned and then they ditch
> your firewall rules in an effort to aid in exfiltration."

---

## Making the System Amnesiac

Most of these steps limit persistent storage so persistence is
opted into, not opted out of. The root filesystem becomes a tmpfs
cleared on every reboot; persistent data is written to a subfolder
in `/nix` that a symlink / bindmount farm is linked to.

Builds on:

- impermanence
- "NixOS ❄: tmpfs as root"
- "Erase your darlings"

### Partitioning / Setup

Default NixOS partition shape:

- `/boot` for BIOS boot or EFI files
- 2× RAM for swap
- `/` for everything else

> "Technically NixOS works fine if you make only one big filesystem
> and put `/boot` on there directly, but this may only pan out for
> BIOS booting systems."

With `/` becoming a tmpfs, repartition as:

- `/boot`
- 2× RAM swap
- `/nix` for everything else

Example partition commands (testing in a VM):

```bash
dev=/dev/vda # replace me with the actual device
parted ${dev} -- mklabel msdos
parted ${dev} -- mkpart primary ext4 1M 512M
parted ${dev} -- set 1 boot on
parted ${dev} -- mkpart primary ext4 512MiB 100%
mkfs.ext4 -L boot ${dev}1
mkfs.ext4 -L nix ${dev}2
```

> "Normally the author is a zfs stan, however in this case it's
> probably better to keep the scary production servers as boring and
> vanilla as possible, especially when doing a more weird setup like
> this."

`/boot` of 512 MB is "not-terrible" as a default.

Make the root mount with a tmpfs:

```bash
mount -t tmpfs none /mnt
```

Then create the persistent folders:

```bash
mkdir -p /mnt/{boot,nix,etc/{nixos,ssh},var/{lib,log},srv}
```

> "`/srv` is used as the home for services. Adjust this as your facts
> and circumstances demand."

Mount the two real partitions:

```bash
mount ${dev}1 /mnt/boot
mount ${dev}2 /mnt/nix
```

Create matching folders in `/mnt/nix/persist`:

```bash
mkdir -p /mnt/nix/persist/{etc/{nixos,ssh},var/{lib,log},srv}
```

Initial bind mounts (later handled by impermanence):

```bash
mount -o bind /mnt/nix/persist/etc/nixos /mnt/etc/nixos
mount -o bind /mnt/nix/persist/var/log /mnt/var/log
```

Generate the base config:

```bash
nixos-generate-config --root /mnt
```

Edit `/etc/nixos/hardware-configuration.nix`. Change:

```nix
fileSystems."/" = {
  device = "none";
  fsType = "tmpfs";
  options = [ "defaults" "mode=755" ];
};
```

to:

```nix
fileSystems."/" = {
  device = "none";
  fsType = "tmpfs";
  options = [ "defaults" "size=2G" "mode=755" ];
};
```

The 2 GB cap holds temporary files; adjust to system RAM. The author
"personally thinks that 512 MB could make sense depending on what
you are doing."

### Using Impermanence

Add the impermanence module to the Nix search path:

```bash
export NIX_PATH=nixpkgs=channel:nixos-21.05:impermanence=https://github.com/nix-community/impermanence/archive/refs/heads/master.tar.gz:nixos-config=/etc/nixos/configuration.nix
```

> "Depending on your security needs you may want to mirror the
> impermanence git repo, but keep in mind it needs to point to a
> tarball for Nix to understand what to do with it."

Add the impermanence config to `/etc/nixos/configuration.nix`:

```nix
environment.persistence."/nix/persist" = {
  directories = [
    "/etc/nixos" # nixos system config files, can be considered optional
    "/srv"       # service data
    "/var/lib"   # system service persistent data
    "/var/log"   # the place that journald dumps it logs to
  ];
};
```

SSH host key paths require direct `environment.etc` wiring — putting
them in `environment.persistence.<name>.directories` breaks
`sshd.service`'s host-key generation:

```nix
environment.etc."ssh/ssh_host_rsa_key".source
  = "/nix/persist/etc/ssh/ssh_host_rsa_key";
environment.etc."ssh/ssh_host_rsa_key.pub".source
  = "/nix/persist/etc/ssh/ssh_host_rsa_key.pub";
environment.etc."ssh/ssh_host_ed25519_key".source
  = "/nix/persist/etc/ssh/ssh_host_ed25519_key";
environment.etc."ssh/ssh_host_ed25519_key.pub".source
  = "/nix/persist/etc/ssh/ssh_host_ed25519_key.pub";
```

Persist machine-id if logs / machine-id-dependent services must survive reboot:

```nix
environment.etc."machine-id".source
  = "/nix/persist/etc/machine-id";
```

Continue with `nixos-install` as usual (add `--no-root-passwd` if a
bootstrap-only root password was set).

### Repeatable Base Image with an ISO

The post links to a `nixos-configs` repo `iso/` folder with a `build`
script that constructs an automatic install ISO encoding the
sections above. The ISO bootstrap snippet:

```nix
users.users.root.initialPassword = "hunter2";
users.users.root.openssh.authorizedKeys.keyFiles = [ (fetchKeys "Xe") ];
```

> "This sets the root password to `hunter2` (a reasonably secure
> default for bootstrapping systems only, holy crap do not use this
> in production) so you can log in with the console and the list of
> SSH keys from the author's GitHub. Replace `Xe` with your GitHub
> username. This is not the most deterministic, but if GitHub is down
> you probably have bigger problems."

Or skip GitHub fetching:

```nix
users.users.root.openssh.authorizedKeys.keys = [
  "ssh-yolo swag420blazeit"
];
```

The ISO can be turned into an EC2 image with packer.

---

## Audit Tracing

> "The Linux kernel has some fancy auditing powers that are
> criminally under-used."

Initial audit rule logging every execve:

```nix
# hosts/meeka/auditd.nix
{ ... }:
{
  security.auditd.enable = true;
  security.audit.enable = true;
  security.audit.rules = [
    "-a exit,always -F arch=b64 -S execve"
  ];
}
```

Watch with `journalctl -f`. If nothing shows, SSH in and run `ls`
from another window — a flurry of audit records should appear.

### Send All Logs Off-Machine

> "You should really treat all system-local logs as radioactive. They
> are liabilities and in some cases can present problematic
> situations when faced with questionable interpretations of things
> like the GDPR. Not to mention attackers will be tempted to wipe all
> record of their attacks from them. Get them off the system as fast
> as possible."

A scraper should flag programs executed outside `/nix/store` — a
common break-in signal.

---

## Optional Steps

> "Just be aware that these things may make debugging an errant
> system difficult."

### Rip Out `sudo`

```nix
# hosts/meeka/sudo.nix
{ ... }:

{
  security.sudo.enable = false;
}
```

Keep it but wheel-only:

```nix
# hosts/meeka/sudo.nix
{ ... }:

{
  security.sudo.execWheelOnly = true;
}
```

### Rip Out Default Packages

Default NixOS bundles include `nano`, `perl`, `rsync`, etc. To strip
them:

```nix
# hosts/meeka/no-defaults.nix
{ lib, ... }:

{
  environment.defaultPackages = lib.mkForce [];
}
```

> "The `lib.mkForce` function forcibly overrides the contents of that
> value to what you give as an argument."

### Disable sshd Features

Restrict sshd as a jumpbox:

```nix
# configuration/meeka/sshd.nix
{ ... }:

{
  services.openssh = {
    passwordAuthentication = false;
    allowSFTP = false; # Don't set this if you need sftp
    challengeResponseAuthentication = false;
    extraConfig = ''
      AllowTcpForwarding yes
      X11Forwarding no
      AllowAgentForwarding no
      AllowStreamLocalForwarding no
      AuthenticationMethods publickey
    '';
  };
}
```

### Mark All Partitions but `/nix/store` as `noexec`

> "This is the most paranoid of the ideas in this post."

Combined with locked-down package manager and systemd isolation,
non-`/nix/store` execution becomes blocked — attackers must achieve
code execution within a running service to do damage.

> "Keep in mind that doing this will likely break the heck out of
> Nix when it needs to build things. In the author's testing it's
> been fine, however they are not an expert in these things."

Services should be denied `/nix/persist` access and only granted
specific paths under `/`, lest they smuggle executables into the
exec-allowed mount. `bash ./foo.sh` is not blocked by this; C
executables effectively are.

```nix
# hosts/meeka/noexec.nix
{ ... }:

{
  fileSystems."/".options = [ "noexec" ];
  fileSystems."/etc/nixos".options = [ "noexec" ];
  fileSystems."/srv".options = [ "noexec" ];
  fileSystems."/var/log".options = [ "noexec" ];
}
```

> "This should fairly sufficiently prevent any attacker from getting
> very far with exploits written in languages like C (which also
> means that it prevents bitcoin miner bots from running)."

---

## PCI Compliance Tip

> "PCI Compliance requires you to have an antivirus program installed
> on every server. It doesn't say anything about the program
> _running_, but just it being installed is enough. Get one step
> closer to PCI compliance with this one neat trick:"

```nix
# hosts/meeka/pci-compliance-pass.nix
{ pkgs, ... }:

{
  environment.systemPackages = with pkgs; [ clamav ];
}
```

---

## Conclusion

> "All in all, this entire setup will let you get a rather paranoid
> configuration that will reject everything outside of the golden
> path of what you told the machines to do."

> "Obligatory warning: Don't put this directly into production unless
> you know what you are doing, or at least can claim you know what
> you are doing with enough certainty to make servers difficult to
> debug. Have a way to 'break the glass' and go back to a less noexec
> setup if you need to, it will save your ass."

> "Be sure to import all of those random `.nix` files if you want to
> use it in one cohesive system config. That may be a slight bit
> entirely essential."

Footer (verbatim): *"Facts and circumstances may have changed since
publication. Please contact the author before jumping to conclusions
if something seems wrong or unclear."*
