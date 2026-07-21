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
coo gather          find every key scattered across your machine, flag divergence
coo check           ask each provider: alive? dead? drained? wrong role?
coo nest            list what you've gathered (names only, never values)
coo stash <ref>     paste one key into the nest (hidden)
coo fan <ref>       push the canonical value everywhere it should live
```

`coo gather` is the one you run first. It reads your `~/CODE/*/.env`, your shell profile, your agent auth stores, and shows you the mess you didn't know you had — grouped by service, with **divergence flagged**: the same account key wearing three different values across three repos means two of them are stale.

`coo check` is the one that makes people share a screenshot. It asks each provider directly — not the file, the provider — so a key that exists, parses, and is *wrong* gets caught. That's the failure storage tools can't see.

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

OpenRouter (with remaining credit), Anthropic, OpenAI, GitHub, and any Supabase / JWT key (decodes and shows the role — the `anon`-where-you-wanted-`service_role` trap). Adding a provider is a few lines in `probe()`. PRs welcome — the whole point is that key formats change constantly, so the rules should be community-owned.

## Status

v0.1, single file, ~250 lines you can read in one sitting. Built and dogfooded on a real 46-repo, multi-agent, VPS-and-Vercel fleet. `gather` and `check` are done. `fan` (one-paste fan-out) and the age backend are next.

MIT.
