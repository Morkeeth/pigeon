# Roadmap

The bet: **key ops for agent fleets, not human teams.** Storage is solved and priced per human seat. A fleet has zero humans and its keys silently drift and die. magpie keeps them alive.

Ordered by leverage. Each slice is independently shippable and dogfooded before the next.

## ✅ v0.1 — gather + check + guided setup (done, Jul 2026)
- `gather` — scan the machine, flag divergence on account-scoped keys only
- `check` — ask each provider: alive / dead / drained / wrong-role
- bare command — a guided paste flow that fixes the broken ones, verifying live
- macOS Keychain backend, gitleaks self-scan clean
- Dogfooded on a real 46-repo, multi-agent, VPS + Vercel fleet

## v0.2 — `fan` (the copy-paste killer)
One paste → every place a key lives. Declare sites once (`fan site openrouter/API_KEY ~/CODE/x/.env OPENROUTER_API_KEY`), then `fan openrouter/API_KEY` writes the canonical value to all of them and backs up what it replaced. Kills the four-places-and-one-goes-stale bug at the root. Prototyped already.

## v0.3 — age backend (portability = other people can use it)
Keychain is Mac-only. An [age](https://github.com/FiloSottile/age)-based backend stores the nest as an encrypted file that works on Linux, a VPS, and — encrypted into a repo — a **shared team nest** with no server. This is the slice that turns "Oscar's tool" into "anyone's tool."

## v0.4 — `rotate` (paste once, everywhere, then revoke)
Open the provider console, paste the new key once, verify it live, fan it to every site, and remind you to revoke the old one. The whole cumbersome rotation, one command.

## v0.5 — `watch` (never be surprised by a dead key)
A scheduled `check` that notifies you the moment a key goes DEAD or LOW — before an agent fails silently. This is the promise the incumbents can't make, because they check the file, not the provider.

## v0.6 — MCP server + more providers (agent-native)
An MCP endpoint so an agent can ask "is my key alive / how much budget is left" mid-run. Plus community PRs for new key shapes — the whole point is that formats change constantly, so the rules should be owned by everyone. Per-key spend caps surfaced where the provider supports them (OpenRouter today; the €10-loss-max rule made visible).

## Distribution
- `brew install` tap + a `curl -fsSL <domain> | sh` one-liner (the "one copy-paste command" install)
- The `check` screenshot — a real dead + drained + wrong-role key — is the launch tweet
- Show HN / r/commandline / the agent-builder communities

## Non-goals (on purpose)
- Not a vault. Sits on storage, never rebuilds it.
- Not a server, not an account, not per-seat.
- Not a security product. The real control is a spend cap per key; magpie makes it visible.
- No AI in the setup path — you have no keys yet to run one, and deterministic is faster anyway.
