# factory log

## [2026-05-30] session | Topology interview + design accepted

Interview in `scratch/interview_about_factory.md` + follow-up in
`scratch/interview_about_factory_followup.md` walked through twelve
decision questions. Design distilled into
[[projects/factory/designs/factory-monorepo-topology]] with five
load-bearing ADRs:

- [[projects/factory/adr/0001-single-git-monorepo]] — single-git
  workspace umbrella at `/factory/`
- [[projects/factory/adr/0002-decoupled-mill-builds]] — sibling
  Mill builds, root coordinates via shell
- [[projects/factory/adr/0003-pub-mirror-policy]] — filtered one-way
  rsync, deploymentbox v3 publishes from `pub/`
- [[projects/factory/adr/0004-upstream-fork-rule]] — fork-first rule
  for all external libraries
- [[projects/factory/adr/0005-secrets-adopt-deploymentbox-custody]]
  — sops + YubiKey, encrypted at rest

Key changes from the original `/p/factory/` design
([[scratch/monorepo-design-wip]]): workspace umbrella over true
code monorepo, wiki absorbed via `git subtree`, `upstream/` and
`pub/` retain their own `.git/` outside the monorepo's history.

Open question deferred from `projects/dependency-manager/`
(`dm` absorption) is now **closed** per ADR-0002 — `dm` stays as
a meta-tool.

Open question deferred from `projects/deploymentbox/` v3 design
(`/p/hg/deploymentbox/` disposition) is **untouched** here —
remains a deploymentbox concern.

Migration plan, path-rewrite script, and cutover sequence are
deferred to a forthcoming plan under `projects/factory/plans/`.

Refs: [[projects/factory/index]],
[[scratch/interview_about_factory]],
[[scratch/interview_about_factory_followup]]
