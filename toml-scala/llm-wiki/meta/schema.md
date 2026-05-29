# toml-scala Wiki Page Schema

All content pages use this frontmatter:

```yaml
---
id: <category>-<name>              # unique within this wiki (kebab-case)
title: "Human Title"
category: concept | api | data | codec | derivation | recipe
layer: foundation | core | integration | application
tags: [searchable, keywords]
source_files:
  - /p/gh/toml-scala/path/to/file.scala   # absolute paths
source_commit: <short-hash>
api_surface: [Type.method, ...]    # for grep-based discovery
related: [other-page-ids]
see_also: [recipe-or-pattern-ids]
---
```

## Layers

- **foundation** — primitives that do not depend on other library types
  (Constants, Escape, Unescape).
- **core** — the AST model and parser rules (`Value`, `Node`, `Root`,
  `Rules`, `Embed`).
- **integration** — typeclass-driven mapping between Scala types and the
  AST (`Codec`, derivation, `Generate`).
- **application** — task-oriented recipes that compose the above.

## Source File Conventions

- Use absolute paths under `/p/gh/toml-scala/`.
- When a concept has Scala 2 and Scala 3 implementations, list **both**
  source files so refresh detects either side moving.
- When a page mixes JVM-only code with cross-platform code, note the
  platform suffix in the page body.

## Categories

| Category | Location | Purpose |
|----------|----------|---------|
| concept | concepts/ | Mental model: AST, parser pipeline, error model |
| api | api/ | Top-level entry points on `toml.Toml` |
| data | data/ | ADT shapes: `Value`, `Node`, `Root`, `Extension`, errors |
| codec | codecs/ | Built-in codecs and how to write custom ones |
| derivation | derivation/ | Automatic codec derivation (Scala 2 + Scala 3) |
| recipe | recipes/ | Task-oriented "how do I…" guides |

## Naming

- Files: lowercase kebab-case (`custom-codec.md`)
- IDs: `<category>-<name>` (`codec-custom`, `api-parse-as`)
- Page titles: title case
