# Follow up

## Q1

yes, the inidividual git pr repo today at /p/gh is just temporary and not of importance at all, we will create one git commit as the initial one after everything is settled in /factory.

The piont about upstream is also true, it needs to be ignored, we should have a script updating those forks nightly I believe and also the ability to run them manually if needed. This could be a job defined in the meta build.

The wiki should be part of the monorepo, everything here needs to be synced at all time with the actual source code. Also, the git policy will be equal for the complete monorepo, except the pub folder and the uptream folder, which needs to follow other policies.

We can use a merge commit so that the git history of the wiki is preserved in the new monorepo using a git subtree merge strategy I believe.

topology is then as follows:

 /factory/.git/                          ← single monorepo
  ├── build.mill                          ← tracked
  ├── flake.nix                           ← tracked
  ├── tools/                              ← tracked
  ├── hg/<lib>/                           ← tracked (no per-lib .git)
  ├── wiki/                               ← tracked
  ├── upstream/<lib>/                     ← gitignored, own .git (forks)
  ├── pub/<lib>/                          ← gitignored, own .git (rsync target)
  ├── secrets/                            ← gitignored
  └── out/                                ← gitignored

Having pub and upstream outside of the monorepo is a hassle, but I see no way around it, we need to build tooling that works in our favor.

## Q2

yes, root an children should be decoupled, i.e. the main thing is that we can treat each repository indipendently from the the root with respect to the mill tooling perspective. We might later generate the root build file in such a way that it includes some or all of the children projects, but this is something we deferr until later, we could create a plugin or something special, but this has no priority atm.

## Q4

I confirm and agree to everything except:

we do NOT sync `.github/workflows`, they might not be identical and the private one may contain wording I do not want to have public.

Everything else is fine.

## Q9

I confirm and support your vision on all points, I didn't remember that the secrets actually are encrypted.

## Q10

yes, let's do it in python to have more control, also we will use git and can see the diff afterwards that it is clean.

## Q11

yes confirm A over B

## Q12

yes, confirm, let's keep things to protocols but at a bear minimum.


