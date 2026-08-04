# Cold-start reconnaissance — 2026-08-05

v1.0 slice 1. The roadmap says this slice is the unknown and that slices 4–5 are guesswork
until it runs. It ran. Method: fresh `git clone` into a throwaway `HOME` — no Keychain
entries, no `~/.local/bin`, no `sites.json`, no PATH beyond `/usr/bin:/bin` — driving the
binary the way a stranger would, README in hand.

Six stumbles. Four are fixed on this branch; two are recorded and left open on purpose.

---

## 1. `coo keys` on an empty nest was a dead end — FIXED

`keys` is the safest-sounding verb in the help text, so it is the one a stranger tries
first. It said, in full:

```
the nest is empty.
```

No next step. Every *other* empty state already taught one (`coo test` → *"run `coo` and
pick 1"*). The first command a new user runs was the only one that told them nothing.

```
the nest is empty — nothing gathered yet.
  land your first key:  `coo`          pick a provider, paste, done
  already have some?    `coo scan`     find what's on this machine
```

## 2. The README's own install line hard-failed — FIXED

Followed verbatim in a virgin `HOME`:

```
$ ln -s "$PWD/pigeon/coo" ~/.local/bin/coo
ln: /…/home/.local/bin/coo: No such file or directory
```

A fresh mac has no `~/.local/bin`. The very first command in the README exits 1. Fixed with
`mkdir -p ~/.local/bin` on the line above.

## 3. `~/.local/bin` is not on the default macOS PATH — FIXED (documented)

This machine's `/etc/paths` **does** contain `~/.local/bin`, which is exactly the insider
state that makes this invisible from the inside: stock macOS ships
`/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin` and nothing else. So even after the symlink
lands, `coo` is plausibly not found.

*Not verified on a stock machine — verified only that it is absent from Apple's default and
present here.* Fixed by making the install block end in `coo --version` as a self-test, with
a collapsed `command not found` section offering both the PATH line and "just run `./coo`".

## 4. No `--version` — FIXED

```
$ coo --version
✗ unknown command: --version
```

A tool distributed through a tap has to answer *which one do you have* or a bug report is
unactionable. Added `VERSION="0.3.0"`, wired to `--version` / `-V` / `version`.

## 5. README line 1 did not say macOS-only — FIXED

The v1.0 platform ruling is *"macOS-only, and said in line 1 of the README — not in a
footnote."* It was in a footnote, under Install, in a sentence that also listed `zsh` and
`curl`. Now it is line 1, and it names the age backend as the first PR to want.

---

## Not stumbles — checked and found already right

Recording these because two were on my suspect list and both were wrong:

- **The agent surface is intact.** `keys --json` → `[]`, `test --json` → a well-formed
  zero object, `pending --json` → `[]`. All three work on an empty nest.
- **Unknown commands exit 1**, not 0. An agent can branch on it.
- **`coo test` / `scan` / `pending` empty states all teach.** Only `keys` did not.

## Still open

- **Slice 4 (the first 60 seconds) is untested and stays untested here.** It needs a TTY
  and a human eye; a non-interactive harness cannot judge whether the picker *feels* good.
  This is the slice the roadmap marks taste-bound, and the cold start does not substitute
  for it.
- **A real `brew` tap** (slice 3) — the install path above is still clone-and-symlink.
