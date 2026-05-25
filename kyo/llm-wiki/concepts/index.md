# Concepts

Foundational ideas behind the Kyo effect system.

| Page | Summary |
|------|---------|
| [pending-type](pending-type.md) | The `A < S` type — what it means, how effects appear in S |
| [algebraic-effects](algebraic-effects.md) | How Kyo's effect system works (suspend/handle, no monads) |
| [effect-composition](effect-composition.md) | Combining effects via intersection types, handling order |
| [effect-widening](effect-widening.md) | How `A < S1` automatically widens to `A < (S1 & S2)` |
| [direct-syntax](direct-syntax.md) | The `direct { }` block, `.now`, `.later`, control flow |
| [resource-management](resource-management.md) | Scope for acquire/release, resource safety |
