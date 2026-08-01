# Prefix provenance — all 60 providers

Every prefix in the `REGISTRY` table in `coo`, checked against the vendor's own
documentation. A row is **VERIFIED** only when a vendor-published page states or
shows the prefix, and the URL is in this table. Everything else is **UNVERIFIED** —
which here means *nobody has checked*, not *wrong*.

`UNVERIFIED` is the honest majority outcome. A prefix in `coo` that is unverified
here was written from memory in v0.1 and has never been confirmed. It may well be
correct. It has simply not been proven, and pigeon should not claim otherwise.

Checked 2026-08-01 against live vendor docs. Key formats churn; a citation is a
snapshot, not a guarantee. Re-check before trusting a row older than a few months.

## Counts

| | prefixes | provider rows |
|---|---|---|
| **VERIFIED** — vendor doc URL below | **33 / 70** | 15 / 60 fully cited |
| **UNVERIFIED** — no vendor doc found | **37 / 70** | 27 / 60 with ≥1 uncited prefix |
| rows claiming no prefix at all | — | 18 / 60 |

Row totals: 15 fully verified · 3 partially verified · 24 wholly unverified · 18 claim no prefix.

Evidence grades used below:

- **stated** — prose that names the prefix as the format ("Bot token strings begin with `xoxb-`")
- **table** — a vendor reference table mapping prefix → credential type
- **example** — a vendor code sample or masked value showing the prefix

`stated` and `table` are strong. `example` is weaker: it proves the prefix exists
in at least one key, not that it covers every key of that type.

---

## The table

| # | provider | prefix | status | evidence | source |
|---|---|---|---|---|---|
| 1 | openai | `sk-proj-` | UNVERIFIED | — | platform.openai.com returns 403 to unauthenticated fetches; no public vendor page found stating the format |
| 2 | openai | `sk-svcacct-` | UNVERIFIED | — | as above |
| 3 | anthropic | `sk-ant-` | **VERIFIED** | stated | https://platform.claude.com/docs/en/manage-claude/authentication — "Static `sk-ant-api...` secret in the `x-api-key` header" |
| 4 | openrouter | `sk-or-v1-` | UNVERIFIED | — | openrouter.ai/docs/api-keys and /docs/api-reference/authentication use `<OPENROUTER_API_KEY>` placeholders only |
| 5 | supabase | `sb_secret_` | **VERIFIED** | table | https://supabase.com/docs/guides/api/api-keys — "Secret keys \| `sb_secret_...`" |
| 6 | supabase | `sb_publishable_` | **VERIFIED** | table | https://supabase.com/docs/guides/api/api-keys — "Publishable key \| `sb_publishable_...`" |
| 7 | github | `ghp_` | **VERIFIED** | table | https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github — "Personal access token (classic)" → `ghp_` |
| 8 | github | `gho_` | **VERIFIED** | stated | https://github.blog/engineering/platform-security/behind-githubs-new-authentication-token-formats/ — "`gho` for OAuth access tokens" |
| 9 | github | `ghu_` | **VERIFIED** | stated | as above — "`ghu` for GitHub user-to-server tokens" |
| 10 | github | `ghs_` | **VERIFIED** | stated | as above — "`ghs` for GitHub server-to-server tokens" |
| 11 | github | `ghr_` | **VERIFIED** | stated | as above — "`ghr` for refresh tokens" |
| 12 | github | `github_pat_` | **VERIFIED** | table | https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github — "Fine-grained personal access token" → `github_pat_` |
| 13 | google | `AIza` | **VERIFIED** | example | https://docs.cloud.google.com/docs/authentication/api-keys — example key `AIzaSyDaGmWKa4JsXZ-HjGw7ISLn_3namBGewQe` |
| 14 | groq | `gsk_` | UNVERIFIED | — | console.groq.com/docs/quickstart and /docs/api-reference use `$GROQ_API_KEY` placeholders only |
| 15 | xai | `xai-` | UNVERIFIED | — | docs.x.ai/docs/overview and /docs/api-reference use `$XAI_API_KEY` placeholders only |
| 16 | perplexity | `pplx-` | UNVERIFIED | — | docs.perplexity.ai/getting-started/quickstart states no key format |
| 17 | huggingface | `hf_` | **VERIFIED** | example | https://huggingface.co/docs/hub/en/security-tokens — code sample `access_token = "hf_..."` |
| 18 | replicate | `r8_` | **VERIFIED** | example | https://replicate.com/docs/reference/http — "Authorization: Bearer r8_Hw***…" |
| 19 | elevenlabs | `sk_` | UNVERIFIED | — | elevenlabs.io/docs/api-reference/authentication uses `YOUR_API_KEY` placeholders only |
| 20 | fireworks | `fw_` | UNVERIFIED | — | docs.fireworks.ai/getting-started/quickstart states no key format |
| 21 | modal | `ak-` | UNVERIFIED | — | modal.com/docs/reference/cli/token documents the commands, not the token format |
| 22 | modal | `as-` | UNVERIFIED | — | as above |
| 23 | langsmith | `lsv2_pt_` | UNVERIFIED | — | docs.langchain.com/langsmith/create-account-api-key names PAT vs Service key but no prefixes |
| 24 | langsmith | `lsv2_sk_` | UNVERIFIED | — | as above |
| 25 | stripe | `sk_live_` | **VERIFIED** | stated | https://docs.stripe.com/keys — live-mode keys "begin with `pk_live_`, `rk_live_` and `sk_live_`" |
| 26 | stripe | `sk_test_` | **VERIFIED** | stated | https://docs.stripe.com/keys — test-mode keys "begin with `pk_test_`, `rk_test_` and `sk_test_`" |
| 27 | stripe | `rk_live_` | **VERIFIED** | stated | https://docs.stripe.com/keys |
| 28 | stripe | `rk_test_` | **VERIFIED** | stated | https://docs.stripe.com/keys |
| 29 | slack | `xoxb-` | **VERIFIED** | stated | https://docs.slack.dev/authentication/tokens — "Bot token strings begin with `xoxb-`" |
| 30 | slack | `xoxp-` | **VERIFIED** | stated | https://docs.slack.dev/authentication/tokens — "User token strings begin with `xoxp-`" |
| 31 | slack | `xapp-` | **VERIFIED** | stated | https://docs.slack.dev/authentication/tokens — "App-level token strings begin with `xapp-`" |
| 32 | slack | `xoxa-` | UNVERIFIED | — | **not present** in Slack's current token-types doc; may be a retired format |
| 33 | slack | `xoxs-` | UNVERIFIED | — | **not present** in Slack's current token-types doc; may be a retired format |
| 34 | notion | `ntn_` | UNVERIFIED | — | developers.notion.com/reference/authentication and /docs/authorization show no token format |
| 35 | notion | `secret_` | UNVERIFIED | — | as above |
| 36 | linear | `lin_api_` | UNVERIFIED | — | linear.app/developers/graphql states no key format |
| 37 | figma | `figd_` | UNVERIFIED | — | developers.figma.com/docs/rest-api/personal-access-tokens/ states no token format |
| 38 | airtable | `pat` | UNVERIFIED | — | support.airtable.com/docs/creating-personal-access-tokens states no token format |
| 39 | shopify | `shpat_` | UNVERIFIED | — | shopify.dev access-token-types page 404s; access-scopes and authentication-authorization pages show no prefixes |
| 40 | shopify | `shpss_` | UNVERIFIED | — | as above |
| 41 | shopify | `shpca_` | UNVERIFIED | — | as above |
| 42 | shopify | `shppa_` | UNVERIFIED | — | as above |
| 43 | resend | `re_` | **VERIFIED** | stated | https://resend.com/docs/api-reference/introduction — "Bearer re_xxxxxxxxx where `re_xxxxxxxxx` is your API Key" |
| 44 | sendgrid | `SG.` | UNVERIFIED | — | twilio.com/docs/sendgrid API-keys and authentication pages use `<Your-API-Key-Here>` only |
| 45 | twilio | `SK` | **VERIFIED*** | table | https://www.twilio.com/docs/glossary/what-is-a-sid — "Prefix: SK / Component: API Key". **\*Wrong field** — see Findings #2 |
| 46 | gitlab | `glpat-` | **VERIFIED** | table | https://docs.gitlab.com/security/tokens/ — "Personal access token: `glpat-`" |
| 47 | gitlab | `gldt-` | **VERIFIED** | table | https://docs.gitlab.com/security/tokens/ — "Deploy token: `gldt-`" |
| 48 | npm | `npm_` | UNVERIFIED | — | docs.npmjs.com/about-access-tokens describes tokens as "a hexadecimal string" — **contradicts** `npm_`; see Findings #3 |
| 49 | pypi | `pypi-` | **VERIFIED** | stated | https://pypi.org/help/ — "Set your password to the token value, including the `pypi-` prefix" |
| 50 | docker | `dckr_pat_` | UNVERIFIED | — | docs.docker.com access-tokens pages state no token format |
| 51 | aws | `AKIA` | **VERIFIED** | table | https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html — "AKIA \| Access key" |
| 52 | aws | `ASIA` | **VERIFIED** | table | https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_identifiers.html — "ASIA \| Temporary (AWS STS) access key IDs" |
| 53 | netlify | `nfp_` | UNVERIFIED | — | docs.netlify.com/api/get-started/ states no token format |
| 54 | fly | `fm2_` | **VERIFIED** | example | https://fly.io/docs/security/tokens/ — "`-t <existing token starting with fm2_>`" |
| 55 | fly | `FlyV1` | UNVERIFIED | — | **not present** on fly.io/docs/security/tokens/ |
| 56 | neon | `napi_` | UNVERIFIED | — | neon.com/docs/manage/api-keys shows `neon_api_key_…`, `neon_org_key_…`, `neon_project_key_…` — **contradicts** `napi_`; see Findings #4 |
| 57 | planetscale | `pscale_tkn_` | UNVERIFIED | — | planetscale.com/docs/concepts/service-tokens states no token format |
| 58 | planetscale | `pscale_pw_` | UNVERIFIED | — | as above |
| 59 | pinecone | `pcsk_` | UNVERIFIED | — | docs.pinecone.io/guides/projects/manage-api-keys shows no key format |
| 60 | tavily | `tvly-` | **VERIFIED** | example | https://docs.tavily.com/documentation/quickstart — `api_key="tvly-YOUR_API_KEY"` |
| 61 | firecrawl | `fc-` | **VERIFIED** | example | https://docs.firecrawl.dev/introduction — `api_key="fc-YOUR-API-KEY"` |
| 62 | brave | `BSA` | UNVERIFIED | — | api-dashboard.search.brave.com web-search get-started uses `<YOUR_API_KEY>` only |
| 63 | sentry | `sntrys_` | UNVERIFIED | — | checked docs.sentry.io /api/auth/, /account/auth-tokens/, /cli/configuration/, internal-integration — none state a prefix |
| 64 | sentry | `sntryu_` | UNVERIFIED | — | as above |
| 65 | posthog | `phx_` | **VERIFIED** | example | https://posthog.com/docs/api/personal-api-keys — masked display hint `phx_***1234` |
| 66 | posthog | `phc_` | UNVERIFIED | — | not shown on posthog.com/docs/api or /docs/api/personal-api-keys |
| 67 | honeycomb | `hcaik_` | UNVERIFIED | — | docs.honeycomb.io manage-api-keys shows no key format |
| 68 | doppler | `dp.pt.` | **VERIFIED** | table | https://docs.doppler.com/reference/auth-token-formats — "dp.pt. — Personal Token" |
| 69 | doppler | `dp.st.` | **VERIFIED** | table | https://docs.doppler.com/reference/auth-token-formats — "dp.st. — Service Token" |
| 70 | doppler | `dp.sa.` | **VERIFIED** | table | https://docs.doppler.com/reference/auth-token-formats — "dp.sa. — Service Account Token" |

## Rows that claim no prefix (18)

These providers have an empty `prefixes` column in `coo` — the claim is "this
vendor's keys have no distinctive shape." That is itself an unverified claim, and
one of them is now known to be false.

| provider | status |
|---|---|
| cloudflare | **WRONG — vendor now documents 3 prefixes.** See Findings #1 |
| vercel · mistral · deepseek · together · cohere · clerk · discord · telegram · railway · upstash · exa · serper · datadog · wandb · assemblyai · deepgram · okx | UNVERIFIED — no vendor page found either stating a prefix or stating that none exists |

---

## Findings

Four things this pass turned up that are bugs, not gaps.

**1. Cloudflare has documented prefixes and pigeon has none.**
https://developers.cloudflare.com/fundamentals/api/get-started/token-formats/ documents
three: `cfk_` (global key), `cfut_` (user token), `cfat_` (account token). The
create-token page adds: "New API tokens use the `cfut_` prefixed scannable format."
pigeon's cloudflare row has an empty prefix column, so it cannot name a Cloudflare
token on sight. This is a missed detection, not a false block — lower severity, but
free to fix.

**2. Twilio's `SK` is on the wrong field.**
`SK` is verified — but as the prefix of the Twilio **API Key SID**, per
https://www.twilio.com/docs/glossary/what-is-a-sid ("Prefix: SK / Component: API Key").
pigeon's registry maps it to `TWILIO_AUTH_TOKEN`. The Auth Token has no documented
prefix. So pigeon will reject a correct Twilio auth token paste as "wrong provider" —
this is a live false-positive in the guard, the exact failure the README warns about.

**3. npm's own docs contradict `npm_`.**
docs.npmjs.com/about-access-tokens describes access tokens as "a hexadecimal string,"
with no prefix. `npm_` is real for granular tokens in the wild, but npm has not
documented it on that page. Unresolved — needs a better source before either keeping
or removing.

**4. Neon's docs contradict `napi_`.**
neon.com/docs/manage/api-keys shows `neon_api_key_…`, `neon_org_key_…` and
`neon_project_key_…`. These may be illustrative placeholders rather than literal
prefixes, so this is flagged, not ruled. Needs a real key or a better page to settle.

### Coverage the vendors document and pigeon does not

Not bugs — completeness gaps, listed so the next slice has a target:

- **Stripe** also documents `pk_live_`, `pk_test_` (publishable) and `sk_org_` (organization).
- **Slack** also documents `xwfp-` (workflow token). Meanwhile pigeon's `xoxa-` and `xoxs-` appear nowhere in Slack's current docs.
- **GitLab** documents 14 prefixes; pigeon carries 2. Missing: `gloas-`, `glrt-`, `glrtr-`, `glcbt-`, `glptt-`, `glft-`, `glimt-`, `glagent-`, `glwt-`, `glsoat-`, `glffct-`.
- **Doppler** documents 7; pigeon carries 3. Missing: `dp.ct.`, `dp.said.`, `dp.scim.`, `dp.audit.`.

## Method, and how to redo this

Each prefix was checked by fetching the vendor's own documentation and looking for
the literal prefix string. Third-party sources — blog posts, secret-scanning rule
sets, community forums, other people's regex libraries — were **not** accepted as
citations, on the grounds that they are exactly the kind of copied-from-memory
knowledge this pass exists to replace. GitHub's own engineering blog was accepted
because GitHub is the vendor.

Where a vendor doc could not be fetched (OpenAI returns 403 to unauthenticated
requests) the row is UNVERIFIED, not guessed.
