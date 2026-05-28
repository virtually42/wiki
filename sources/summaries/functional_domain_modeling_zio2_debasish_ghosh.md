---
id: summary-functional-domain-modeling-zio2-ghosh
title: "Summary: Functional Domain Modeling — The ZIO 2 Way (Debasish Ghosh, 2022)"
kind: descriptive
status: accepted
scope: global
created: 2026-05-28
updated: 2026-05-28
confidence: medium
sources:
  - https://www.slideshare.net/slideshow/functional-domain-modeling-the-zio-2-way/253277754
  - sources/tmp/functional_domain_modeling_zio2_debasish_ghosh.txt
tags: [functional-design, ddd, zio, zio-prelude, repository, domain-service, zlayer, scala]
---

## Source

- **Title**: Functional Domain Modeling: The ZIO 2 way
- **Author**: Debasish Ghosh
- **Published**: 2022-09-22 (SlideShare, 39 slides)
- **URL**: https://www.slideshare.net/slideshow/functional-domain-modeling-the-zio-2-way/253277754
- **Staged snapshot**: [[sources/tmp/functional_domain_modeling_zio2_debasish_ghosh.txt]]
  (text extraction only; pending human review for promotion to `sources/raw/docs/`)
- **Confidence**: medium (extraction via WebFetch — image-only slides may have lost detail)

## Thesis

A pattern language for domain modeling in Scala using **ZIO 2** that
combines DDD vocabulary (entities, value objects, repositories, domain
services) with a functional core. The argument is that *concrete* ZIO
effect types in service/repository contracts give clearer failure and
environment semantics than tagless-final, while **ZLayer** provides
declarative dependency injection with resource scoping.

## Pattern Language Elements

1. **Common vocabulary** — domain terms drive type names.
2. **Modularization** — layered: model → repositories → services → application.
3. **Entities / Value Objects** — pure ADTs, strongly typed
   (newtypes, refinement types via `zio-prelude`).
4. **Repositories** — one per aggregate root, effectful contracts
   abstracting persistence.
5. **Domain Services** — coarse-grained orchestrators expressed in
   model vocabulary.

## Layer-by-Layer Pattern

### Entities / Value Objects (pure core)

```scala
final case class Account private (
  no: AccountNo,
  name: AccountName,
  dateOfOpen: ZonedDateTime,
)

object Account:
  def tradingAccount(...): Validation[String, Account]
  private[model] def validateAccountNo(...): Validation[String, AccountNo]
  def close(a: Account, ...): Validation[String, Account]
```

- ADTs; smart constructors return `Validation[E, A]` (zio-prelude).
- Strong typing via newtypes / refinement types.
- Behavior encapsulated in companion objects.

### Repositories (effectful contracts)

```scala
trait AccountRepository:
  def queryByAccountNo(no: AccountNo): Task[Option[Account]]
  def store(a: Account): Task[Account]
  def store(as: List[Account]): Task[Unit]
  def allOpenedOn(d: LocalDate): Task[List[Account]]
```

- Plain Scala traits, one per aggregate root.
- **Concrete `zio.Task[A] = ZIO[Any, Throwable, A]`** — not tagless `F[_]`.
- No environment dependencies (`R = Any`).
- Live implementations get dependencies via constructor parameters,
  exposed as `ZLayer`:

```scala
final case class AccountRepositoryLive(
  xaResource: Resource[Task, Transactor[Task]]
) extends AccountRepository:
  def all: Task[List[Account]] =
    xaResource.use(xa => SQL.getAll.to[List].transact(xa).orDie)

object AccountRepositoryLive extends CatzInterop:
  val layer: ZLayer[DBConfig, Throwable, AccountRepository] =
    ZLayer.scoped:
      for
        cfg        <- ZIO.service[DBConfig]
        transactor <- mkTransactor(cfg)
      yield AccountRepositoryLive(transactor)
```

### Domain Services (coarse-grained)

```scala
trait TradingService:
  def getAccountsOpenedOn(d: LocalDate): IO[TradingError, List[Account]]
  def orders(...): IO[TradingError, NonEmptyList[Order]]
  def execute(...): IO[TradingError, NonEmptyList[Execution]]
  def allocate(...): IO[TradingError, NonEmptyList[Trade]]
```

- `IO[E, A]` with a **typed domain error** (`TradingError`), not raw `Throwable`.
- Multi-entity workflows composed via `for` over the service's own methods:

```scala
final def generateTrade(
  input: GenerateTradeFrontOfficeInput, userId: UserId
): IO[Throwable, NonEmptyList[Trade]] =
  for
    orders     <- orders(input.frontOfficeOrders)
    executions <- execute(orders, ...)
    trades     <- allocate(executions, ...)
  yield trades
```

- Live implementation depends on **repository interfaces**, not
  implementations, via constructor injection:

```scala
final case class TradingServiceLive(
  ar: AccountRepository,
  or: OrderRepository,
  er: ExecutionRepository,
  tr: TradeRepository,
) extends TradingService
```

### Application Wiring

```scala
ZIO.serviceWithZIO[TradingService](svc => /* program */)
  .provide(
    AccountRepositoryLive.layer,
    TradingServiceLive.layer,
    OrderRepositoryLive.layer,
    TradeRepositoryLive.layer,
    ExecutionRepositoryLive.layer,
    config.live,
  )
```

- ZIO assembles the layer graph automatically.
- Parallel acquisition where possible; scoped lifetimes.

## Concrete Effects vs Tagless-Final (Author's Position)

| Aspect | Concrete ZIO | Tagless `F[_]` |
|--------|--------------|----------------|
| Failure type | Visible in `IO[E, A]` | Hidden in `F` constraints |
| Environment | Visible in `R` of `ZIO[R,E,A]` | Hidden in capability constraints |
| Parametricity | Less abstract, more concrete | More abstract |
| Ergonomics | Direct ZIO API, ZLayer DI | Requires typeclass plumbing |

Author argues concreteness is a feature here: the contract publishes
*which* exceptions/values flow, instead of deferring to instances.

## ZLayer Benefits Highlighted

- Declarative construction recipes.
- Automatic dependency graph from the layer set provided.
- Composable, asynchronous, non-blocking resource acquisition.
- Parallel acquisition (vs. sequential class constructors).
- Scoped lifetimes for resources (DB transactors, etc.).

## Relevance To Our Wiki

- **Cross-reference with**
  [[sources/summaries/introduction_to_functional_design_john_de_goes]]:
  De Goes describes encoding-level functional design (executable vs
  declarative); Ghosh describes *architectural* functional design
  (model/repository/service layers) within an effect system.
- **Kyo parallel**: our stack uses Kyo, not ZIO. The
  layering pattern (pure ADTs → effectful contracts via concrete effect
  types → application wiring) translates: `IO[E, A]` ↔
  `A < Abort[E] & Async`, `ZLayer` ↔ `Env` + `Scope`.
- Candidate input to a future
  `tech/patterns/functional-domain-layering.md` once a second source or
  internal synthesis corroborates.

## Caveats

- Source is a slide deck (no narration), so motivation and tradeoff
  discussion are abbreviated.
- Slide extraction is text-only; diagrams (esp. slide 38 architecture
  diagram) were not captured.

## Links

- Schema: [[meta/schema]]
- Related summary:
  [[sources/summaries/introduction_to_functional_design_john_de_goes]]
- Related skills: `scala:hexagonal-architecture`,
  `scala:functional-patterns`, `scala:kyo-data-env-scope`
