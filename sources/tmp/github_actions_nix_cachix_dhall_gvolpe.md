# Raw extraction — "GitHub Actions Powered by Nix Shell & Cachix"

**Source URL:** https://gvolpe.com/blog/github-actions-nix-cachix-dhall/
**Author:** Gabriel Volpe (gvolpe)
**Publication date:** 2020-06-02
**Read time (stated):** 7 minutes
**Tags (author):** nix, nixos, cachix, ci, haskell, scala, dhall
**Fetched:** 2026-05-29
**Method:** WebFetch (HTML → structured markdown). Verbatim code blocks
preserved. Prose paraphrased except where placed in quotation marks.
Staged here for human triage; promote to `sources/raw/docs/` if the
human wants the article preserved as raw source.

---

## Opening motivation

Volpe expresses conviction that Nix represents "the way forward" as a
purely functional package manager, while acknowledging "there's still
room for big improvements." The post documents recent projects where
he has been "*Nixifying*" multiple codebases.

---

## Section 1: Nix shell for reproducible development

### Problem & solution

Nix shell enables creation of reproducible development environments
without system-wide installation. Example provided:

```
$ nix-shell -p redis
[nix-shell:~]$ redis-cli --version
redis-cli 6.0.3
[nix-shell:~]$ exit
$ redis-cli --version
Command 'redis-cli' not found
```

### Reproducibility challenge

> "This is not *that reproducible* since different machines might be
> pointing to a different Nix channel, or to the same channel but
> using a different version."

The solution requires pinning nixpkgs versions.

### Recommended practice

> "Nowadays, it is very common to provide a `shell.nix` per project,
> declaring the dependencies needed to build it."

Volpe recommends [nix-direnv](https://github.com/nix-community/nix-direnv)
so that dependencies are available as soon as we cd into the directory
("highly recommended").

### Blog project `shell.nix` configuration

```nix
let
  nixpkgs = fetchTarball {
    name   = "NixOS-unstable-13-05-2020";
    url    = "https://github.com/NixOS/nixpkgs-channels/archive/6bcb1dec8ea.tar.gz";
    sha256 = "04x750byjr397d3mfwkl09b2cz7z71fcykhvn8ypxrck8w7kdi1h";
  };
  pkgs = import nixpkgs {};

  ruby = pkgs.ruby_2_7;
  rubygems = (pkgs.rubygems.override { ruby = ruby; });

in pkgs.mkShell {
  buildInputs = [
    pkgs.haskellPackages.dhall-json # v1.6.2
    ruby # v2.7.1p83
  ];

  shellHook = ''
    mkdir -p .nix-gems
    export GEM_HOME=$PWD/.nix-gems
    export GEM_PATH=$GEM_HOME
    export PATH=$GEM_HOME/bin:$PATH
  '';
}
```

### Configuration explanation

1. `fetchTarball` retrieves a specified nixpkgs version for reproducibility.
2. `rubygems` overrides ruby version to match project needs (2.7.x).
3. `pkgs.mkShell` creates a shell using the specified nixpkgs version.
4. `buildInputs` declares two dependencies; only Ruby builds the blog;
   `dhall-json` generates YAML locally.
5. `shellHook` executes commands preparing the shell environment.

### Ruby-specific note

> "In a Ruby project, the best way to guarantee reproducibility is by
> using [bundix](https://github.com/nix-community/bundix), but I didn't
> bother in using it just to build my blog. After all, I prefer to
> write code in statically-typed languages."

---

## Section 2: GitHub Actions powered by Dhall

### Rationale for Dhall

> "Why not defining the YAML files directly? One may ask. The answer
> is I really [dislike YAML files](https://noyaml.com/)."

[Dhall](https://dhall-lang.org/) "can generate YAML from a sane Dhall
definition via the `dhall-to-yaml` program."

### Blog CI definition in Dhall

```dhall
let GithubActions =
      https://raw.githubusercontent.com/gvolpe/github-actions-dhall/steps/cachix/package.dhall sha256:4cd8f64770d8b015c2fd52bae5ddfb5b393eb7e0936f7f8e18f311c591b888a5

let setup =
      [ GithubActions.steps.checkout
      , GithubActions.steps.cachix/install-nix
      , GithubActions.steps.cachix/cachix { cache-name = "gvolpe-blog" }
      , GithubActions.steps.run
          { run = "nix-shell run -- \"bundle install && bundle exec jekyll build\"" }
      ]

in  GithubActions.Workflow::{
    , name = "Blog"
    , on = GithubActions.On::{
      , pull_request = Some GithubActions.PullRequest::{=}
      , push = Some GithubActions.Push::{ branches = Some [ "master" ] }
      }
    , jobs = toMap
        { build = GithubActions.Job::{
          , name = "build"
          , needs = None (List Text)
          , runs-on = GithubActions.types.RunsOn.`ubuntu-18.04`
          , steps = setup
          }
        }
    }
```

### Dhall advantages

> "Besides giving us types, Dhall gives us
> [semantic integrity checks](http://www.haskellforall.com/2017/11/semantic-integrity-checks-are-next.html),
> which is a great and secure way of versioning files."

### Unified build approach

> "Notice how we use the same `shell.nix` we use for local development
> to build our software in the CI pipeline. Isn't that awesome? No more
> duplicate ways of building packages! This way, we guarantee that
> whatever works locally, also works on our CI."

### Tooling attribution

> "Now, what am I using to write this nice Dhall definition? The
> answer is [Github Actions Dhall](https://github.com/regadas/github-actions-dhall),
> a project by Filipe Regadas."
>
> "In this particular example, I'm pointing at my fork, which contains
> the definitions of the `cachix/install-nix` and `cachix/cachix`
> actions."

### Generation command

```bash
$ dhall-to-yaml --file ci.dhall > ci.yml
```

### GitHub feature request

> "I know this is a bit annoying at the moment, but I'd do this 1000
> times over writing YAML directly. The interesting thing is that
> Github could support Dhall definitions natively - I actually
> submitted a feature request but I don't know if they will consider it."
>
> "All they need to do is to have `dhall-json` installed, take in a
> Dhall definition and run the same `dhall-to-yaml` command."

---

## Section 3: Caching derivations with Cachix

### Cachix overview

> "[Cachix](https://cachix.org/) is a binary cache as a service, and
> it is free for public caches and open-source projects. It helps
> speeding up your CI build as well as builds in other machines that
> share the same `shell.nix`."

### Standard documentation pattern

```bash
$ cachix create <name>
$ nix-build | cachix push <name>
$ cachix use <name>
```

### `shell.nix`-specific challenge

Direct `nix-build` of `shell.nix` fails: *"This derivation is not
meant to be built, aborting"*.

### Solution: building Nix shell derivations

> "Don't worry. Cachix supports building and pushing the derivations
> of a Nix shell but it is currently an under-documented feature!"

```bash
$ nix-shell
$ nix-store -qR --include-outputs $(nix-instantiate shell.nix) | cachix push <name>
```

> "The first step might not be necessary if you already evaluated
> your shell or are using Nix Direnv."

### GitHub Actions integration

> "Once you learn how to use Cachix, you could take advantage of it
> on Github actions by using
> [Cachix Action](https://github.com/cachix/cachix-action), which is
> the action used in our Dhall file above."

### Real-world assessment

> "So far, I have been trying this configuration on
> [this blog](https://github.com/gvolpe/blog), on a
> [Scala project](https://github.com/profunktor/redis4cats) and on a
> [Haskell project](https://github.com/gvolpe/shopping-cart-haskell).
> The conclusion is that for a CI build job I could probably get away
> without using Cachix and it'll still be the same. However, as soon
> as the Nix dependencies of your project start to grow, you may
> notice a difference."

---

## Section 4: Microsite publishing automation (Scala/sbt example)

### Use case

> "The Redis4Cats project (Scala) is particularly interesting because
> I use Nix only to publish the static site (microsite) that contains
> the documentation."

### Standard approach vs. Nix

> "This is normally done via the command `sbt publishMicrosite`, which
> requires not only `sbt` and `openjdk` but also `jekyll`."

### Redis4Cats `shell.nix`

```nix
let
  nixpkgs = fetchTarball {
    name   = "NixOS-unstable-13-05-2020";
    url    = "https://github.com/NixOS/nixpkgs-channels/archive/6bcb1dec8ea.tar.gz";
    sha256 = "04x750byjr397d3mfwkl09b2cz7z71fcykhvn8ypxrck8w7kdi1h";
  };
  pkgs = import nixpkgs {};
in
  pkgs.mkShell {
    buildInputs = with pkgs; [
      haskellPackages.dhall-json # 1.6.2
      jekyll # 4.0.1
      openjdk # 1.8.0_242
      sbt # 1.3.10
    ];
  }
```

### Microsite publication Dhall workflow

```dhall
let GithubActions =
      https://raw.githubusercontent.com/gvolpe/github-actions-dhall/steps/cachix/package.dhall sha256:4cd8f64770d8b015c2fd52bae5ddfb5b393eb7e0936f7f8e18f311c591b888a5

let setup =
      [ GithubActions.steps.checkout
      , GithubActions.steps.cachix/install-nix
      , GithubActions.steps.cachix/cachix { cache-name = "scala-microsite" }
      , GithubActions.steps.run { run = "nix-shell --run \"sbt publishSite\"" }
      ]

in  GithubActions.Workflow::{
    , name = "Microsite"
    , on = GithubActions.On::{
      , push = Some GithubActions.Push::{
        , branches = Some [ "master" ]
        , paths = Some [ "site/**" ]
        }
      }
    , jobs = toMap
        { publish = GithubActions.Job::{
          , name = "publish-site"
          , needs = None (List Text)
          , runs-on = GithubActions.types.RunsOn.`ubuntu-18.04`
          , steps = setup
          , env = Some (toMap { GITHUB_TOKEN = "\${\{ secrets.GITHUB_TOKEN }}" })
          }
        }
    }
```

### Key features

- Triggers only on master branch pushes
- Filters to changes in `site/**` paths
- Uses `GITHUB_TOKEN` secret for authentication
- Runs `sbt publishSite` within the `nix-shell` context

### Performance and results

> "You can see it in action [here](https://github.com/profunktor/redis4cats/runs/732431811).
> It takes about 13 minutes because the `sbt publishMicrosite` is a
> slow task, not because of Nix, but the point is that this is now an
> automated task and I can forget about it."

---

## Conclusion (verbatim)

> "I like all this stuff a lot so I hope to adopt it in other projects
> quite soon."

---

## Related content the article links to

- "Parallel typeclass for Haskell" — gvolpe.com/blog/parallel-typeclass-for-haskell/ (2020-04-20)
- "Setting up Ghcide in Ubuntu with Nixpkgs" — gvolpe.com/blog/setting-up-ghcide-nixpkgs-ubuntu/ (2020-03-21)
- "Entering a Purely Functional World @ Scala MDE Meetup 2019" — gvolpe.com/talks/medellin-2019/ (2019-08-09)

## External tools / projects referenced

- [Nix](https://nixos.org/), Nix shell, Nix channels, `nix-build`, `nix-store -qR`, `nix-instantiate`
- [nix-direnv](https://github.com/nix-community/nix-direnv)
- [Cachix](https://cachix.org/) + [cachix-action](https://github.com/cachix/cachix-action)
- [Dhall](https://dhall-lang.org/) + `dhall-to-yaml`
- [github-actions-dhall](https://github.com/regadas/github-actions-dhall) (Filipe Regadas) and Volpe's fork with cachix steps
- [bundix](https://github.com/nix-community/bundix)
- [noyaml.com](https://noyaml.com/)
- [Haskell For All — semantic integrity checks](http://www.haskellforall.com/2017/11/semantic-integrity-checks-are-next.html)

## Topics the article does *not* cover

- GPG / Maven Central artifact signing
- Sonatype Central Portal publishing
- Self-hosted runners or alternative CI hosts
- Build reproducibility verification (hash comparison) as a supply-chain
  control — the article uses Nix to *produce* reproducible environments
  but does not propose CI-output verification against a local rebuild
- Secret management beyond `GITHUB_TOKEN` for site publishing
- Flakes (article predates flakes being mainstream; uses
  `fetchTarball` + pinned channel URL instead)
- Mill, Mill `publishSigned`, or any Mill-specific wiring
