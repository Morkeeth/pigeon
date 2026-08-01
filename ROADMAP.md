# Roadmap

The bet: **key ops for agent fleets, not human teams.** Storage is solved and priced per human seat. A fleet has zero humans and its keys silently drift and die. pigeon keeps them alive.

Ordered by leverage. Each slice is independently shippable and dogfooded before the next.

## ✅ v0.1 — gather + check + guided setup (done, Jul 2026)
- `scan` — read the machine, flag divergence on account-scoped keys only
- `test` — ask each provider: alive / dead / drained / wrong-role
- bare `coo` — a guided paste flow that fixes the broken ones, verifying live
- macOS Keychain backend, gitleaks self-scan clean
- Dogfooded on a real 46-repo, multi-agent, VPS + Vercel fleet

## ✅ v0.2 — the input is the product (done, Jul 31 2026)
The slice that made it usable. All of it driven against real keys and real production.

- **Picker** — 60 providers in a `REGISTRY` table, type-to-filter, recency-ranked, in-nest markers. Raw zsh; no fzf, no deps. Adding a provider is one line and no code.
- **Detection** — name a value from its prefix; refuse a wrong-provider paste before storing. Trim a shell prompt that came along with a copy; reject non-ASCII outright.
- **Clipboard** — if you already copied it, one keypress. `--clipboard` runs the whole flow unattended so an agent can trigger it.
- **Landing** — after a verified paste, find every copy on the machine *by value shape* and offer to fix the stale ones. Backups always.
- **Account vs project scope** — only one-key-per-account providers get bulk overwrite. Everything else is listed and left alone.
- **Vercel** — env push plus `--redeploy`, with presence verification and honest reporting of what could not be read back.
- **Agent surface** — `pending`, `--json`, `--stdin`, `--clipboard`, meaningful exit codes.
- **Terminal** — synchronized output, alternate screen, OSC 8 links, and a trap so a kill never leaves the terminal in raw mode.

## v0.3 — earn the trust back
v0.2 wrote one project's key over another's, twice, before the scope rule existed. Close the gaps that made that possible before adding anything new.

- ~~**Verify the 60 prefixes against vendor docs.**~~ Done 2026-08-01 → [PREFIXES.md](PREFIXES.md). 33 of 70 prefixes now carry a vendor-doc citation; 37 are marked UNVERIFIED because no vendor page states them. The pass surfaced four defects, all still unfixed:
  - **Twilio `SK` is on the wrong field** — it's the API Key SID prefix, not the Auth Token. Live false-positive in the guard. Fix first.
  - **Cloudflare has three documented prefixes** (`cfk_`, `cfut_`, `cfat_`) and pigeon carries none — a missed detection.
  - **npm `npm_`** and **Neon `napi_`** are contradicted by their own vendor docs. Need a real key or a better page to settle.
- ~~**Close the citation gap.**~~ **DEFERRED to the community (ruled 2026-08-01).** The remaining 37 block no one — they are published as UNVERIFIED and the table was built for exactly this (one line, no code). Vendors that document more than pigeon carries, for whoever picks it up: GitLab (14 vs 2), Doppler (7 vs 3), Stripe (`pk_*`, `sk_org_`), Slack (`xwfp-`).
- **Probe more shapes.** `sb_secret_` has none, so a wrong Supabase key stores and deploys silently. Same for Vercel, Stripe, Groq, xAI, Google. → **`sb_secret_` pulled forward into v1.0 slice 2**; the rest stay here.
- **`--dry-run`** — print every file it *would* touch before it touches one.

## v1.0 — go public, with DX people can feel

**Ruled 2026-08-01.** pigeon goes public. Not because a market was found — because the
author has this problem and found nothing that solves it. The bar for shipping is not
"it works", it is: *someone installs it and thinks "he really thought about this."*

**Platform ruling: macOS-only, and said in line 1 of the README — not in a footnote.**
Perfect for the people it serves beats mediocre for everyone. Portability moves to v1.1
and is the obvious first community PR.

Seven slices, ordered by what unblocks the most. Each ships and verifies alone.

**1. Cold-start reconnaissance** — become the stranger before designing for them.
Fresh clone into a throwaway `HOME`: no Keychain entries, no `~/.local/bin`, no `sites.json`.
Record every stumble verbatim.
- done when: a numbered list of real stumbles exists, each with the exact output the stranger saw
- size **S** · **risk: this is the unknown.** Slices 4–5 are guesswork until it runs — expect it to rewrite them

**2. Correctness debt** — never ship a known false-positive.
The four defects in [PREFIXES.md](PREFIXES.md), plus the missing `sb_secret_` probe (a silent
wrong Supabase key is what broke litmus twice).
- done when: a real Twilio auth token stores without a "wrong provider" block; a bad `sb_secret_` reports DEAD, not UNKNOWN
- size **M** · risk: npm + Neon need a real token shape to settle

**3. Install path** — the front door.
`brew install morkeeth/tap/pigeon`, plus a `curl -fsSL … | sh` fallback.
- done when: both land `coo` on PATH on a machine that has never seen the repo
- size **M** · risk: tap repo + formula is new ground

**4. The first 60 seconds** — `coo` on an empty nest → first key landed.
The whole "wow" lives here: motion, spacing, colour, the picker's feel, and what the very
first run shows when there is nothing to show.
- done when: a stranger reaches a landed key having read no README, timed under 60s
- size **L** · risk: taste-bound. Needs `/design-taste` and Oscar's eye — not an agent's assertion that it looks good

**5. Failure and empty states** — where "he really thought about it" actually lives.
Nothing gathered · probe can't reach · key rejected · wrong provider · Keychain locked.
- done when: all five hit on purpose and screenshotted, none reading like a stack trace
- size **M**

**6. Repo surface** — what people judge before they install.
README line 1 = macOS-only. `CONTRIBUTING.md` aiming the 37 uncited prefixes at the community
(that is what the one-line-no-code table was built for). Issue templates, LICENSE, a real demo cast.
- done when: someone who never installs it can tell in 10s what it does and whether it runs on their machine
- size **M**

**7. Flip public — and re-run slice 1 as the gate.**
- done when: repo is public and a second cold-start produces zero stumbles from the slice-1 list
- size **S**

**Deferred on purpose:** the 37 uncited prefixes — proven 2026-08-01 to block no one, and
community-shaped work by design. Linux/portable backend → v1.1.

## v1.1 — age backend (portability)
Keychain is Mac-only. An [age](https://github.com/FiloSottile/age)-based backend stores the nest as an encrypted file that works on Linux, a VPS, and — encrypted into a repo — a **shared team nest** with no server. The slice that turns "Oscar's tool" into "anyone's tool". **First community PR candidate.**

## v1.2 — `watch`
A scheduled `test` that notifies the moment a key goes DEAD or LOW — before an agent fails silently. The promise the incumbents can't make, because they check the file, not the provider.

## v1.3 — MCP server
An endpoint so an agent can ask "is my key alive / how much budget is left" mid-run instead of shelling out.

## Non-goals (on purpose)
- Not a vault. Sits on storage, never rebuilds it.
- Not a server, not an account, not per-seat.
- Not a security product. The real control is a spend cap per key.
- **Never revokes a key for you.** A wrong guess there takes production down.
- No AI in the setup path — you have no keys yet to run one, and deterministic is faster anyway.
