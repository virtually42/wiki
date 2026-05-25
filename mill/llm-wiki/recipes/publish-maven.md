---
id: publish-maven
title: Publish to Maven Central
section: recipes
source_commit: 41ce6c977c4
related:
  - modules/publish-module.md
  - configuration/publishing.md
---

# Publish to Maven Central

## Step 1: Add PublishModule

```scala
import mill._, scalalib._, publish._

object mylib extends ScalaModule with PublishModule {
  def scalaVersion = "3.6.4"
  def publishVersion = "1.0.0"

  def pomSettings = PomSettings(
    description = "My awesome library",
    organization = "com.example",
    url = "https://github.com/user/repo",
    licenses = Seq(License.Apache2),
    versionControl = VersionControl.github("user", "repo"),
    developers = Seq(
      Developer("user", "Full Name", "https://github.com/user")
    )
  )
}
```

## Step 2: Test Locally

```bash
mill mylib.publishLocal      # publish to ~/.ivy2/local
mill mylib.publishM2Local    # publish to ~/.m2/repository
```

## Step 3: Publish to Sonatype

```bash
mill mill.scalalib.PublishModule/publishAll \
  --publishArtifacts mylib.publishArtifacts \
  --sonatypeUri https://s01.oss.sonatype.org/service/local \
  --sonatypeStagingUrl https://s01.oss.sonatype.org/content/repositories/snapshots \
  --gpgArgs --passphrase=$GPG_PASS,--batch,--yes,-a,-b \
  --readTimeout 600000 \
  --credentials $SONATYPE_USER:$SONATYPE_PASS
```

## Prerequisites for Maven Central

1. Sonatype account (https://central.sonatype.com)
2. GPG key for signing
3. Namespace verification (groupId ownership)
4. Complete POM metadata (description, license, SCM, developers)
