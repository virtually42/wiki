# Agentic Coding Through the Lens of Cellular Automata

## Abstract

Complex computation can emerge from simple local rules — that is the central lesson of cellular automata. This talk applies the same principle to LLM-assisted software development and argues that effective agentic coding needs no orchestration framework. It needs structured local knowledge, simple rules, and the discipline to let emergence work.

We introduce the **llm-wiki**: a schema-governed knowledge base where every page is a cell carrying typed state (frontmatter), connected to neighbors (related pages, compliance chains), and evolved through deterministic operations — *ingest*, *query*, *implement*, *lint*, *promote*. Each operation reads local context, applies the schema's transition rules, and writes back. A feedback force closes the loop: drift detection catches inconsistencies, the promote operation elevates locally-discovered patterns into global rules, and the system self-organizes over time — precisely as in a cellular automaton.

We validate this approach through three Scala projects that span the platform's full diversity: **toolbox** (JVM CLI utilities), **paladium** (a cross-platform JVM/JS/Native library exploiting Mill's `Cross[]` matrix), and **swc** (a Wayland compositor written entirely in Scala Native with Kyo effects). Same wiki. Same rules. Same operations. Radically different targets — from command-line tools to browser-ready libraries to a bare-metal desktop compositor.

The takeaway is actionable: a concrete schema for structuring LLM-assisted development, evidence that simple local rules outperform complex agent frameworks, and a demonstration that Scala's unique cross-platform reach makes it the ideal language to prove it.
