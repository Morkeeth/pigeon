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

- **Verify the 60 prefixes against vendor docs.** They were written from memory. A wrong one causes a false "wrong provider" block — in the guard everything else now leans on.
- **Probe more shapes.** `sb_secret_` has none, so a wrong Supabase key stores and deploys silently. Same for Vercel, Stripe, Groq, xAI, Google.
- **`--dry-run`** — print every file it *would* touch before it touches one.

## v0.4 — someone who isn't me
- The cold-start test: a stranger clones it and reaches a landed key with no help
- Make the repo public — it is private today, so the README's `git clone` is a lie for everyone else
- `brew install` tap, then a `curl -fsSL … | sh` one-liner

## v0.5 — age backend (portability)
Keychain is Mac-only. An [age](https://github.com/FiloSottile/age)-based backend stores the nest as an encrypted file that works on Linux, a VPS, and — encrypted into a repo — a **shared team nest** with no server. The slice that turns "Oscar's tool" into "anyone's tool".

## v0.6 — `watch`
A scheduled `test` that notifies the moment a key goes DEAD or LOW — before an agent fails silently. The promise the incumbents can't make, because they check the file, not the provider.

## v0.7 — MCP server
An endpoint so an agent can ask "is my key alive / how much budget is left" mid-run instead of shelling out.

## Non-goals (on purpose)
- Not a vault. Sits on storage, never rebuilds it.
- Not a server, not an account, not per-seat.
- Not a security product. The real control is a spend cap per key.
- **Never revokes a key for you.** A wrong guess there takes production down.
- No AI in the setup path — you have no keys yet to run one, and deterministic is faster anyway.
