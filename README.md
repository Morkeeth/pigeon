# 🐦 pigeon

**Your API keys are copied across a dozen `.env` files, and you have no idea which copies still work.** `coo` is one command that finds every copy on your machine, asks each provider which keys are actually dead or out of credit, and replaces them everywhere at once.

**macOS only right now** — keys are stored in the macOS Keychain. [Linux support is the first thing we want help with →](https://github.com/Morkeeth/pigeon/issues)

```
$ coo test
🐦 asking each provider if the key still works…

  anthropic/API_KEY      ALIVE     anthropic
  openrouter/API_KEY     LOW       only $2.14 left
  supabase/SERVICE_KEY   DEAD      supabase says invalid (HTTP 401)
  sendgrid/API_KEY       UNKNOWN   no probe for this shape

  2 alive · 1 dead · 1 unverified
  a dead key that still sits in a config is an agent that fails silently.
```

---

## Why

You run agents now, not just apps. A handful of them, across your laptop, a VPS, Vercel, and each agent's own auth store. Every one needs keys, and the keys drift: you copy one to four places, one copy gets revoked, and **an agent goes dark for days while your dashboard says healthy.** (That happened. It's why this exists.)

Every secrets manager on the market solves *storage*. None of them answer the question you actually have:

> which of my keys is dead, drained, or the wrong role — right now?

They also all charge **per human seat**. Your "team" is five agents and zero humans. pigeon is free, local, and priced for fleets, not seats.

## Use it

```
coo                          the whole tool. run it, everything happens there.
```

That's the interface. The rest are shortcuts into the same flow:

```
coo add                      skip the menu, go straight to adding a key
coo test                     ask every provider: are my keys still alive?
coo keys                     list what you've got (names only, never values)
coo scan                     find keys scattered across this machine
coo rotate <ref>             replace a key everywhere, then revoke the old one
coo push <ref> [--redeploy]  re-send a stored key to its files and Vercel env
coo pending                  what still needs a human paste
coo delete <ref>             remove a key
```

Two words used throughout: a **`<ref>`** is one key, written `service/NAME` — `openrouter/API_KEY`, `stripe/WEBHOOK_SECRET`. The **nest** is where pigeon keeps them: on macOS, your Keychain.

<details>
<summary>older command names still work</summary>

`check` → `test`, `nest` → `keys`, `gather` → `scan`, `fan` → `push`, `remove` (or `rm`) → `delete`, and `stash` is the non-interactive form of `add`. Verified against the dispatch table in `coo`.
</details>

### Pick

Bare `coo` opens a picker over 60 providers that filters as you type — `ant` is enough to land on Anthropic. It marks what's already in your nest, floats what you reached for last, and runs as a modal that leaves nothing in your scrollback.

No fzf, no config, no dependencies — raw zsh against `/dev/tty`, speaking synchronized output (DEC 2026), the alternate screen and OSC 8 hyperlinks. Terminals that don't implement those ignore them, and it degrades to a plain numbered list where there's no TTY at all.

### Paste — or don't

If the key is already on your clipboard, that *is* the paste:

```
📋 your clipboard holds a stripe key — ffa6fa48, 34 chars
use it for stripe/SECRET_KEY? [Y/n] ▸
```

One keypress. The value is never printed — you get the provider it looks like, its length and its fingerprint. The retrieval steps and console link only appear when the clipboard has nothing usable, so they stop being a toll booth.

**pigeon names a value from its prefix.** Paste an `sk-or-v1-…` into the OpenAI slot and it stops you — *"that looks like an OpenRouter key, not openai"* — before storing anything. Same catch that saves you from Supabase's publishable row when you wanted a secret key, generalised to every provider in the table.

Copied it out of a terminal and dragged your shell prompt along? It trims the prompt and tells you. Anything non-ASCII left over is refused outright — macOS re-encodes such values in the Keychain, which would silently store bytes you never pasted.

### Then it lands

A vault stores your key. pigeon **puts it where it belongs**, in the same breath as the paste. The moment a value is verified it looks for every copy already on your machine — matching the value's *shape*, not the variable name, because the fourth copy is always the one somebody called `OR_KEY` at 2am:

```
🐦 this key already lives in 3 place(s) on this machine:
    1  ~/CODE/proj1/.env        OPENROUTER_API_KEY   stale (48693564)
    2  ~/CODE/proj2/.env.local  OR_KEY               stale (9d8616c3)
    3  ~/.zshrc                 OPENROUTER_API_KEY   stale (2e1fb636)  ⚠ shell profile

overwrite the 2 stale copy(ies) with what you just pasted? [Y/n/p=pick] ▸
```

Every changed file is backed up as `<file>.bak-pigeon` first, and **shell profiles are never bulk-written** — a `.zshrc` is a bigger deal than a `.env`, so it needs `p` and an explicit yes.

### Account keys vs project keys — the rule that matters

**pigeon only offers to overwrite copies of a key that is one-per-account.** OpenRouter, Anthropic, OpenAI, GitHub and friends: one account, one key, so a differing copy is stale and worth fixing.

Supabase, Vercel, Clerk, Neon, Stripe test/live and anything not on that list are **per-project**. A different value there is a *different project*, not a stale copy, and overwriting it breaks that project. Those are listed and left alone:

```
🐦 other supabase keys on this machine (NOT touched):
      1  ~/CODE/litmus/.env   SUPABASE_SECRET_KEY   stale (248b772b)
  ↑ supabase keys are PER-PROJECT. A different value there is a different
    project, not a stale copy — overwriting it would break that project.
```

The list is conservative on purpose: absent means never bulk-write. This rule exists because the first version didn't have it and wrote one project's Supabase key over another's.

### Vercel

Declare it once and every future rotation goes to Vercel too:

```bash
coo site supabase/SERVICE_KEY --vercel ~/CODE/myapp SUPABASE_KEY production
coo push supabase/SERVICE_KEY --redeploy
```

An env var doesn't exist for the app until the next build, so `--redeploy` runs `vercel --prod` after a confirmed write. Deploying is never automatic: the flag for scripts, an explicit `y` at a terminal, otherwise a line telling you it isn't live.

Vercel marks Production variables *sensitive*, meaning write-only — `env pull` returns `""` for them. pigeon confirms the variable is **present** and says plainly that it could not read the value back, rather than claiming a check it didn't do.

## For agents

An agent can do everything except the paste. That's the point — the key never passes through it.

```bash
coo site <ref> <file> <VAR>      # declare where a key must live. no secret involved.
coo pending --json               # ["stripe/SECRET_KEY"] — exit 1 while any wait
coo test --json                  # {alive, dead, unverified, keys:[{ref,verdict,detail,fingerprint}]}
coo keys --json                  # the refs, as a JSON array
printf %s "$KEY" | coo add <ref> --stdin
coo add <ref> --clipboard        # take what the human copied, verify, land it. no prompts.
```

The handshake: the agent declares homes and reports `pending`; the human runs `coo` and presses Enter. With `--clipboard` even that disappears — the agent triggers it and the value goes clipboard → keychain → files without passing through the caller.

`--clipboard` **refuses rather than guesses**, because nobody is watching to answer a question: a short clipboard, a different provider than the ref says, or a missing `pbpaste` all stop with nothing stored.

`coo test` exits `0` when nothing is dead and `1` when something is — `coo test || alert` is the whole monitoring integration. Values never appear in any output, JSON included. You get fingerprints.

## What it is not

- **Not a vault.** Storage is solved (1Password, SOPS, age). pigeon sits on top and keeps what's stored *alive*. Point it at your existing store.
- **Not a server.** No account, no cloud, no telemetry. It runs against your machine and the providers' public APIs.
- **Not a security product.** It's key *ops* for people who run agents. The real control is a spend cap per key — set yours to €10 and a leak is a €10 problem.

## Install

```bash
git clone https://github.com/Morkeeth/pigeon
mkdir -p ~/.local/bin                      # a fresh mac does not have this
ln -s "$PWD/pigeon/coo" ~/.local/bin/coo   # or anywhere on your PATH
coo --version                              # 👈 if this says "command not found", see below
```

<details>
<summary><code>coo: command not found</code></summary>

`~/.local/bin` is not on the default macOS `PATH`. Either put it there —

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc && exec zsh
```

— or skip the symlink entirely and run `./coo` from the clone. Both work; nothing about pigeon needs to be installed.
</details>

Requires `zsh`, `curl`, `python3`, and the macOS Keychain. `pbpaste` for clipboard mode, `vercel` (Node 18+) only if you declare a Vercel site. A portable [age](https://github.com/FiloSottile/age) backend for Linux and shared nests is the next slice.

## Providers

Two different claims, and the difference is the honest part.

**Recognised — 60 providers.** One line each in the `REGISTRY` table at the top of `coo`: display name, key prefixes, env-var convention, default ref, console URL. That table powers the picker, the wrong-provider catch, and the retrieval guides. Adding a provider is **one line and no code**.

**Probed live — 5 key shapes.** OpenRouter (returns remaining credit), Anthropic, OpenAI, GitHub, and any JWT (decoded locally, shows the role). Everything else is stored and reported `UNKNOWN` — pigeon says it can't check rather than implying it did. Notably there is **no probe for `sb_secret_`**, so a wrong Supabase secret will store and deploy without complaint.

A probe that can't reach the provider reports `UNKNOWN — couldn't reach anthropic, network not your key`, never `DEAD`. Telling someone their live key is dead is how a good key gets revoked by mistake.

**Cited — 33 of 70 prefixes.** As of 2026-08-01, every prefix in `REGISTRY` has been checked against the vendor's own documentation, and the result is in [PREFIXES.md](PREFIXES.md), one row per prefix with the source URL:

| | prefixes | provider rows |
|---|---|---|
| **VERIFIED** — vendor doc URL on file | **33 / 70** | 15 / 60 fully cited |
| **UNVERIFIED** — no vendor doc found | **37 / 70** | 27 / 60 with ≥1 uncited prefix |
| rows claiming no prefix at all | — | 18 / 60 |

⚠️ **37 of 70 prefixes remain unverified** — written from memory in v0.1 and never confirmed. They may be correct; they are not proven, and pigeon does not claim they are. A wrong one causes a false "wrong provider" block. Correcting one is a one-line PR, and that's deliberate: key formats churn constantly, so the rules should be community-owned.

The pass also found four defects, all listed in [PREFIXES.md](PREFIXES.md#findings). One is live: **Twilio's `SK` is attached to the wrong field** — it's the API Key SID prefix, not the Auth Token, so pigeon currently rejects a correct Twilio auth token as "wrong provider."

## Status

v0.3 — one file, 1,643 lines, ~60 of which are the provider table. Built and dogfooded on a real 46-repo, multi-agent, VPS-and-Vercel fleet, and driven end-to-end against real keys and real production.

Done: the picker, clipboard paste, live verification, post-paste landing, account-vs-project safety, Vercel push + redeploy, the agent handshake, JSON output.

Not done: no probe for most providers, 37 of 70 prefixes still uncited (see [PREFIXES.md](PREFIXES.md)), four known prefix defects unfixed, macOS only, and it has never been run by anyone who isn't its author. See ROADMAP.md.

MIT.
