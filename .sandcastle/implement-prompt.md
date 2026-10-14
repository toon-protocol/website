/mattpocock-skills:implement {{ISSUE_URL}}

You are running AFK in a sandbox, on branch `{{BRANCH}}`, which is already checked out.
Nobody will answer a question, so do not ask one. Treat the issue, its comments and its
parent spec (if it has one) as settled. Read them with `gh issue view {{ISSUE_NUMBER}} --comments`.

Commit to `{{BRANCH}}`, and reference `#{{ISSUE_NUMBER}}` in each commit message. Do not
push, open a PR or close the issue. The runner does all three once you finish.

## This repository

- This is the source of [toon.ar.io](https://toon.ar.io): the TOON Protocol landing page,
  the docs, and the ecosystem, apps and agents pages. It is static HTML and CSS with one
  build step, `python3 build.py`, which uses the Python standard library only. There is no
  package manager and nothing to install.
- `CLAUDE.md` says how the factory works, and `README.md` says how the site is edited
  ("Editing") and checked ("Before publishing"). Read both first. Read `CONTEXT.md` (the
  vocabulary) and `.agents/adr/` (decisions) when they exist and the ticket touches them.
  `docs/` is the built site, not documentation for you. Where an ADR and another document
  disagree, the ADR wins. Use the glossary's terms.
- Edit the sources, never the build output: `src/docs/<slug>.html`, `src/ecosystem.html`,
  `src/apps.html`, `src/agents.html`, `assets/site.css`, and `index.html` outside its
  `<!-- header -->`/`<!-- footer -->` markers and its `<style>` copy. Then run
  `python3 build.py` and commit what it rewrote (`docs/`, `ecosystem/`, `apps/`, `agents/`,
  `index.html`, `manifest.template.json`) together with the source change.
- Before you commit, run the internal checks from README.md's "Before publishing": the
  one-script grep must print only `./index.html`, and no page may load a stylesheet, font
  or image from another host.
- The issues labelled `wayfinder:*` are planning tickets for a human. Never work on one,
  and never edit a wayfinder map.
- After you finish, the runner runs the gate itself and won't open a PR while it is red.
  The gate is the `gate` (or `checks`) job of `.github/workflows/ci.yml` on `main`, and if
  there is none it runs nothing. Run those commands yourself before you commit if the
  file exists. Never weaken, skip or delete a test, and never loosen a lint, to get green.
- A ticket that needs a live box, a funded key or an on-chain write is not something you
  can do from here. Say so in a comment on the issue rather than guessing. Here that means
  publishing: uploading to Arweave, filling transaction ids into the manifest, pointing the
  ArNS record `toon`, and adding receipts to `src/docs/proof.html`. It also means rereading
  the live node's prices for the ecosystem page. Leave all of that to a human.
- `install.sh` is served at `https://toon.ar.io/install.sh` and piped into `sh` by every
  install command on the site. Do not change it unless the ticket is about it.

## When you cannot finish

Stop only when a genuinely new decision is needed, the action is irreversible, it touches
real funds, or it needs a credential that no workflow exposes. In that case, commit nothing
and explain what blocks you in a comment on the issue (`gh issue comment {{ISSUE_NUMBER}}`).
The runner moves an issue with no commits to `needs-triage`.

If your context is getting full (around 150k tokens) before you are done, commit what works,
write the remaining steps to `.sandcastle/logs/handoff-{{ISSUE_NUMBER}}.md`, commit it with
`git add -f`, and end your turn. A fresh session continues from your commits.

When the ticket is done and committed, output <promise>COMPLETE</promise>.

If you stopped because you're blocked, output <promise>BLOCKED</promise> instead, after your
comment on the issue. The runner then ends the run. Otherwise it starts another session, which
hits the same blocker and posts the same comment again.
