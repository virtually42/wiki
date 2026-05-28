---
id: publish-module
title: PublishModule
section: modules
source_files:
  - /p/gh/mill/libs/javalib/src/mill/javalib/PublishModule.scala
source_commit: 41ce6c977c4
related:
  - configuration/publishing.md
  - modules/java-module.md
---

# PublishModule

Mixin trait for publishing artifacts to Maven/Ivy repositories.

## Import

```scala
import mill._, scalalib._, publish._
```

## Minimal Example

```scala
object mylib extends ScalaModule with PublishModule {
  def scalaVersion = "3.6.4"
  def publishVersion = "1.0.0"

  def pomSettings = PomSettings(
    description = "My library",
    organization = "com.example",
    url = "https://github.com/user/repo",
    licenses = Seq(License.MIT),
    versionControl = VersionControl.github("user", "repo"),
    developers = Seq(
      Developer("user", "Full Name", "https://github.com/user")
    )
  )
}
```

## Key Tasks

| Task | Type | Description |
|------|------|-------------|
| `publishVersion` | `T[String]` | Artifact version |
| `pomSettings` | `T[PomSettings]` | POM metadata |
| `artifactName` | `T[String]` | Artifact name (default: module name) |
| `pomPackagingType` | `String` | `"jar"`, `"pom"`, etc. |
| `publishLocal()` | `Command` | Publish to local Ivy repo |
| `publishM2Local()` | `Command` | Publish to local Maven repo (~/.m2) |

## PomSettings Fields

```scala
PomSettings(
  description: String,
  organization: String,
  url: String,
  licenses: Seq[License],
  versionControl: VersionControl,
  developers: Seq[Developer]
)
```

### Common Licenses

```scala
License.MIT
License.Apache2
License.`BSD-3-Clause`
License.`GPL-3.0-only`
```

### VersionControl

```scala
VersionControl.github("user", "repo")
VersionControl(
  url = "https://github.com/user/repo",
  connection = "scm:git:...",
  developerConnection = "scm:git:...",
  tag = Some("v1.0.0")
)
```

## Publishing Commands

```bash
mill mylib.publishLocal          # publish to ~/.ivy2/local
mill mylib.publishM2Local        # publish to ~/.m2/repository
```

## Publishing to Maven Central (Sonatype)

```bash
mill mill.scalalib.PublishModule/publishAll \
  --publishArtifacts mylib.publishArtifacts \
  --sonatypeUri https://oss.sonatype.org/service/local \
  --sonatypeStagingUrl https://oss.sonatype.org/content/repositories/snapshots \
  --gpgArgs --passphrase=mypassword,--batch,--yes,-a,-b \
  --readTimeout 600000 \
  --credentials myuser:mypassword
```
