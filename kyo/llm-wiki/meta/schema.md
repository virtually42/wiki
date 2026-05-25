# LLM-Wiki Page Schema

## Common Frontmatter (all pages)

```yaml
---
id: string                    # unique within this wiki, format: kyo-{category}-{name}
title: string                 # human-readable title
category: enum                # concept | effect | data | module | pattern | convention | recipe
layer: enum                   # foundation | prelude | core | integration | application
tags: [string]                # searchable keywords
source_files: [string]        # relative paths to source files this page describes
source_commit: string         # short commit hash when page was last verified
api_surface: [string]         # key Type.method entries for grep-based discovery
related: [string]             # other page IDs (same or adjacent category)
see_also: [string]            # pattern/recipe page IDs for practical usage
platforms: [jvm, js, native]  # platform availability
---
```

## Category-Specific Fields

### concept

No additional required fields.

### effect

```yaml
effect_type: ArrowEffect | ContextEffect
suspend_methods: [string]     # methods that introduce this effect
handle_methods: [string]      # methods that eliminate this effect
pending_type: string          # what appears in S position, e.g. "Abort[E]"
```

### data

```yaml
opaque: boolean               # whether this is an opaque type (zero-cost)
replaces: string              # stdlib type it replaces, e.g. "Option" for Maybe
```

### module

```yaml
module_name: string           # sbt module name, e.g. "kyo-http"
platforms: [jvm, js, native]
dependencies: [string]        # other kyo modules required
```

### pattern

```yaml
when_to_use: string           # one-line guidance
when_not_to_use: string       # one-line anti-guidance
```

### convention

No additional required fields.

### recipe

```yaml
modules_needed: [string]      # kyo modules required
complexity: simple | moderate | advanced
```

## Page Content Structure

### effect pages

```
## What It Does
## Key APIs
### Suspending (introducing the effect)
### Handling (eliminating the effect)
## Composition
## Common Patterns
## Gotchas
```

### concept pages

```
## Core Idea
## How It Works
## Examples
## Relationship to Other Concepts
```

### data pages

```
## What It Is
## When to Use (vs stdlib alternative)
## Key APIs
## Performance Characteristics
## Common Patterns
```

### module pages

```
## Purpose
## Setup
## Key APIs
## Common Patterns
## Integration Notes
```

### pattern pages

```
## Problem
## Solution
## Examples
## Trade-offs
## Related Patterns
```

### convention pages

```
## Rule
## Rationale
## Examples (Do / Don't)
## Exceptions
```

### recipe pages

```
## Goal
## Prerequisites
## Steps
## Complete Example
## Variations
```

## Naming Conventions

- File names: kebab-case, e.g. `error-handling.md`
- IDs: `kyo-{category}-{name}`, e.g. `kyo-effect-abort`
- One page per concern — split rather than overload

## Index Pages

Each section has an `index.md` with:
- Brief section description
- Table of all pages with id, title, one-line summary
- Grouping by sub-concern where useful (e.g. effects grouped by layer)
