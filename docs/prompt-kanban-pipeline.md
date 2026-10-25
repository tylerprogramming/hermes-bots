# Prompt: run a research → package → code → review pipeline on the Hermes kanban board

Paste this to your Hermes agent after installing the three bot profiles from this repo. Replace the bracketed parts. The result is four linked cards that dispatch themselves; you watch the board.

Before you paste: the Kanban desktop plugin ships off. Turn it on in **Settings → Capabilities → Plugins → Kanban**. Make sure the gateway is running (`hermes gateway status`); the dispatcher lives inside it and ticks every 60 seconds.

---

Set up a kanban pipeline for a new video and run it end to end. Topic: **[TOPIC]**. Video number: **[NNN]**. Content repo: **[/path/to/content]**. Code repo: **[/path/to/code-repo]** (GitHub **[owner/repo]**).

1. **Toolset.** Make sure the `researcher` profile has the kanban tools: `hermes -p researcher tools enable kanban` (and `--platform slack` if it lives in Slack). Confirm with `hermes -p researcher tools list | grep kanban`.

2. **Project.** `hermes project create "[Repo name]" [/path/to/code-repo] --slug [slug]` so code cards get a git worktree and a deterministic branch.

3. **Cards.** Create four cards with `hermes kanban create ... --json --priority 2`, each with a body that tells the worker exactly what to read, what to write, where, and what to put in its completion comment:
   - **Research** → assignee `researcher`, `--workspace dir:[/path/to/content]`. Write the research file to `research/youtube/YYYY-MM-DD-[slug].md`. Completion comment: file path plus the 3 strongest title angles.
   - **Package** → assignee `packager`, same workspace. Build the package with the `yt-package` skill from the research file named in the parent's completion comment. Do not redo research. Completion comment: package files and chosen title.
   - **Code** → assignee `coder`, `--project [slug] --workspace worktree --branch [NNN]-[slug]`. Working demo code in a new folder `[slug]_[NNN]/`, README with install and run, commit, push the branch, open a PR with `gh`, do NOT merge. Completion comment: PR URL and the one-line run command. Say in the body: skip anything that needs an API key (I will add keys myself), do not create `.env`, do not write CLAUDE.md (headless workers cannot get approval for it).
   - **Review** → assignee `coder` (or a reviewer profile), content workspace. Review the package against the voice guide and the code against the research. Completion comment: pass/fail plus a numbered fix list.

4. **Links.** `hermes kanban link <research> <package>`, `<research> <code>`, `<package> <review>`, `<code> <review>`. Children sit in Todo until every parent is Done, then promote to Ready and dispatch on the next tick.

5. **Watch.** Poll `hermes kanban list` every couple of minutes. Report each transition in one line. If a card stalls, read `hermes kanban show <id>` events and the profile's `~/.hermes/profiles/<name>/logs/agent.log` tail; a run of `BLOCKED` lines means the worker is fighting the sandbox, so steer it with `hermes kanban comment <id> "From [me]: skip X, do Y"` (comments reach a running worker mid-turn).

6. **Report** when all four are Done: the research file path, the package folder, the PR URL, and the review verdict. Nothing merged, nothing published.
