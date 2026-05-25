---
id: publishing
title: Publishing
section: configuration
source_commit: 41ce6c977c4
related:
  - modules/publish-module.md
  - modules/scala-module.md
---

# Publishing

How to publish artifacts to local and remote repositories.

## Local Publishing

### Ivy Local (for Mill consumers)

```bash
mill mylib.publishLocal
# Published to: ~/.ivy2/local/com.example/mylib_3/1.0.0/
```

### Maven Local (for Maven/Gradle consumers)

```bash
mill mylib.publishM2Local
# Published to: ~/.m2/repository/com/example/mylib_3/1.0.0/
```

## Sonatype / Maven Central

```bash
mill mill.scalalib.PublishModule/publishAll \
  --publishArtifacts mylib.publishArtifacts \
  --sonatypeUri https://s01.oss.sonatype.org/service/local \
  --sonatypeStagingUrl https://s01.oss.sonatype.org/content/repositories/snapshots \
  --gpgArgs --passphrase=$GPG_PASS,--batch,--yes,-a,-b \
  --readTimeout 600000 \
  --credentials $SONATYPE_USER:$SONATYPE_PASS
```

## Cross-Published Library

```scala
object mylib extends Cross[MylibModule]("2.13.16", "3.6.4")
trait MylibModule extends CrossScalaModule with PublishModule {
  def publishVersion = "1.0.0"
  def pomSettings = PomSettings(
    description = "My library",
    organization = "com.example",
    url = "https://github.com/user/repo",
    licenses = Seq(License.MIT),
    versionControl = VersionControl.github("user", "repo"),
    developers = Seq(Developer("user", "Name", "https://github.com/user"))
  )
}
```

Publish all cross-versions:
```bash
mill mylib[_].publishLocal
```

## Artifact Naming

Mill automatically appends the correct suffix:
- ScalaModule: `mylib_3` or `mylib_2.13`
- ScalaJSModule: `mylib_sjs1_3`
- ScalaNativeModule: `mylib_native0.5_3`

Override with:
```scala
def artifactName = "my-custom-name"
```

## Version from Git

```scala
import mill.util.VcsVersion

def publishVersion = Task {
  VcsVersion.calcVcsState(Task.log).format()
}
```
