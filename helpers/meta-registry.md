# Project Registry

| Project     | Status   | Stack                              | Description                        | Wiki Pages |
|-------------|----------|------------------------------------|------------------------------------|------------|
| compositor  | active   | Scala Native, Kyo, Wayland, wlroots | Wayland compositor                 | 0          |
| webapp      | active   | Scala 3, Kyo, Tapir, PostgreSQL    | Web application                    | 0          |
| cli-tool    | active   | Scala 3, Kyo, SQLite               | CLI utility                        | 0          |
| infra       | active   | NixOS, PostgreSQL, Envoy           | Infrastructure configurations      | 0          |

## Adding a Project

1. Add a row to this table.
2. Create `projects/<name>/CLAUDE.md` from the project template.
3. Create `projects/<name>/log.md` (empty, append-only).
4. Create at least one ADR with a compliance block.
5. Run `lint` to verify structure.
