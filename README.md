# 🐦 pigeon

**Gather, check, and rotate API keys across your agent fleet.** One command finds every key scattered across your machine and tells you which ones are already dead.

A carrier pigeon for your API keys. It gathers them, checks them, and keeps them alive.

```
$ coo check
🐦 asking each provider if the key still works…

  anthropic/API_KEY      DEAD    anthropic rejected
  openrouter/API_KEY     LOW     only $2.14 left
  supabase/SERVICE_KEY   ALIVE   jwt role=anon

  2 alive · 1 dead · 0 unverified
  a dead key that still sits in a config is an agent that fails silently.
```

---

## Why

You run agents now, not just apps. A handful of them, across your laptop, a VPS, Vercel, and each agent's own auth store. Every one needs keys, and the keys drift: you copy one to four places, one copy gets revoked, and **an agent goes dark for days while your dashboard says healthy.** (That happened. It's why this exists.)

Every secrets manager on the market solves *storage*. None of them answer the question you actually have:

> which of my keys is dead, drained, or the wrong role — right now?

They also all charge **per human seat**. Your "team" is five agents and zero humans. pigeon is free, local, and priced for fleets, not seats.

## What it does

```
coo                 the picker: type to filter 60 providers, then add/rotate/fan/remove
coo gather          find every key scattered across your machine, flag divergence
coo check           ask each provider: alive? dead? drained? wrong role?
coo nest            list what you've gathered (names only, never values)
coo stash <ref>     paste one key into the nest (hidden)
coo rotate <ref>    paste a new value, verify it live, fan it, revoke the old
coo remove <ref>    delete a key from the nest
coo fan <ref>       push the canonical value everywhere it should live
```

`coo gather` is the one you run first. It reads your `~/CODE/*/.env`, your shell profile, your agent auth stores, and shows you the mess you didn't know you had — grouped by service, with **divergence flagged**: the same account key wearing three different values across three repos means two of them are stale.

`coo check` is the one that makes people share a screenshot. It asks each provider directly — not the file, the provider — so a key that exists, parses, and is *wrong* gets caught. That's the failure storage tools can't see.

Bare `coo` is the one you actually use. It opens a picker over 60 providers that
filters as you type — `ant` is enough to land on Anthropic — marks the ones
already in your nest, and remembers what you reached for last. Take one and you
get its retrieval steps, its console opened in your browser, and a hidden paste.

Then the part that saves you: **pigeon reads the value's prefix and names it.**
Paste an `sk-or-v1-…` into the OpenAI slot and it stops you — *"that looks like
an OpenRouter key, not openai"* — before it stores anything. Same catch that
saves you from copying Supabase's `anon` row when you wanted `service_role`,
generalised to every provider in the table. Nothing you paste is ever echoed.

No fzf, no config, no deps — it's raw zsh against `/dev/tty`, and it degrades to
a plain numbered list wherever there's no terminal.

### Then it actually lands

A vault stores your key. pigeon **puts it where it belongs**, in the same breath
as the paste. The moment a value is verified, pigeon goes looking for every copy
already on your machine — matching on the value's *shape*, not the variable
name, because the fourth copy is always the one somebody called `OR_KEY` at 2am:

```
🐦 this key already lives in 3 place(s) on this machine:
    1  ~/CODE/proj1/.env        OPENROUTER_API_KEY   stale (48693564)
    2  ~/CODE/proj2/.env.local  OR_KEY               stale (9d8616c3)
    3  ~/.zshrc                 OPENROUTER_API_KEY   stale (2e1fb636)  ⚠ shell profile

overwrite the 2 stale copy(ies) with what you just pasted? [Y/n/p=pick] ▸
```

One keystroke and the stale copies are gone. Every changed file is backed up as
`<file>.bak-pigeon` first, and **shell profiles are never bulk-written** — a
`.zshrc` is a bigger deal than a `.env`, so it needs `p` and an explicit yes.

That is the whole bug pigeon was built for, closed in one prompt: you pasted
once, and there is no stale fourth copy left to kill an agent next Tuesday.

### For agents

Your fleet has no hands, so nothing here needs a terminal:

```bash
coo check --json     # {alive, dead, unverified, keys:[{ref,verdict,detail,fingerprint}]}
coo nest --json      # the refs, as a JSON array
printf %s "$KEY" | coo stash openrouter/API_KEY --stdin
```

`coo check` exits `0` when nothing is dead and `1` when something is — so
`coo check || alert` is the whole monitoring integration. Values never appear in
any output, JSON included; you get fingerprints.

## What it is not

- **Not a vault.** Storage is solved (1Password, SOPS, age). pigeon sits on top and keeps what's stored *alive*. Point it at your existing store.
- **Not a server.** No account, no cloud, no telemetry. It runs offline against your machine and the providers' public APIs. Your values never leave the machine and are never printed — only fingerprints.
- **Not a security product.** It's key *ops* for people who run agents. The real security control is a spend cap per key (set yours to €10 and a leak is a €10 problem). pigeon tracks which keys have one.

## Install

```bash
git clone https://github.com/Morkeeth/pigeon
ln -s "$PWD/pigeon/coo" ~/.local/bin/coo   # or anywhere on your PATH
coo
```

That last line — bare `coo` — is the whole thing: it scans your machine, tells you which keys are dead, drained, or the wrong role, and **walks you through pasting fresh ones**, verifying each with the provider before it stores it. No AI (you have no keys yet to run one), no dashboard, no account. One command, a guided paste, done.

Requires `zsh`, `curl`, `python3`, and macOS Keychain. Backend is the macOS Keychain for now; a portable [age](https://github.com/FiloSottile/age)-based backend for Linux and shared/team nests is the next slice.

## Providers checked

Two different claims, and the difference is the honest part:

**Recognised — 60 providers.** One line each in the `REGISTRY` table at the top of `coo`: display name, key prefixes, env-var convention, default ref, console URL. That table powers the picker, the paste-time wrong-provider catch, and the per-provider retrieval guide. Adding a provider is **one line**, and it needs no code.

**Probed live — 5 key shapes.** OpenRouter (returns remaining credit), Anthropic, OpenAI, GitHub, and any JWT (decoded locally, shows the role). Anything else is stored and reported as `UNVERIFIED` — pigeon says it can't check rather than implying it did.

The prefixes in `REGISTRY` were written from memory, not scraped from vendor docs. A wrong one is a one-line PR, and that's the point: key formats churn constantly, so the rules should be community-owned rather than mine.

## Status

v0.2, still one file (~1,120 lines, ~60 of which are the provider table). Built and dogfooded on a real 46-repo, multi-agent, VPS-and-Vercel fleet. `gather`, `check`, `fan`, `rotate`, the picker and the post-paste landing are done and driven end-to-end against real files. The age backend (Linux/VPS + shared nests) is next — see ROADMAP.md.

MIT.
