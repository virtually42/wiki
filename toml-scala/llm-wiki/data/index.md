# Data

Core ADTs and value types.

| Page | Type | Purpose |
|------|------|---------|
| [value](value.md) | `toml.Value` | Semantic AST: scalars, tables, arrays, date/time |
| [node](node.md) | `toml.Node`, `toml.Root` | Syntactic AST emitted before `Embed.root` |
| [extension](extension.md) | `toml.Extension` | Opt-in non-standard grammar features |
| [parse-error](parse-error.md) | `toml.Parse.Error` | Address + message error tuple shared across the pipeline |
