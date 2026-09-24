#!/usr/bin/env python3
"""Clipboard consent tests for `coo add <ref>`.

Run:  python3 tests/clipboard-consent.py      (macOS, needs /usr/bin/security)

What it proves, each in a fresh HOME with its own temp keychain:
  - Enter, "n" or "yolo" at a prompt stores nothing.
  - "n" at the first prompt means the clipboard is never read.
  - Ctrl+C at either prompt, or during the live probe, exits 130 and stores nothing.
  - EOF (Ctrl+D) at a prompt exits non-zero and stores nothing.
  - "y" then "y" stores the value, in the sandbox keychain only.
  - The full value never appears on screen.

Safety. This never touches your real keychain or clipboard:
  - `security` is a shim that appends the sandbox keychain path to every
    add/find/delete call and refuses every other subcommand.
  - `pbpaste` is a shim that prints a fake key and logs that it was called.
  - `curl` is a shim: it reports "cannot connect", or sleeps when a test needs
    a probe in flight. No network call is made.
  - At the end, the real login keychain is queried (read only, no value) for
    each test ref and must not hold it, and the real keychain search list must
    be unchanged.
"""
import os, pty, re, select, shutil, signal, subprocess, sys, tempfile, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COO = os.path.join(ROOT, "coo")
SEC = "/usr/bin/security"
SERVICE = "pigeon-nest"
REAL_HOME = os.path.expanduser("~")

SG_KEY = "SG.FAKEFAKEFAKEFAKE.FAKEFAKEFAKEFAKEFAKE9z7Q"
ANT_KEY = "sk-ant-api03-FAKEFAKEFAKEFAKEFAKEFAKEFAKEFAKE00w3Xy"
SG_REF = "sendgrid/PIGEON_TEST_KEY"
ANT_REF = "anthropic/PIGEON_TEST_KEY"

SHIM_SECURITY = """#!/bin/sh
case "$1" in
  add-generic-password|find-generic-password|delete-generic-password)
    exec /usr/bin/security "$@" "$SANDBOX_KC" ;;
  *) echo "security shim: refused $1" >&2; exit 99 ;;
esac
"""
SHIM_PBPASTE = """#!/bin/sh
echo called >> "$PB_LOG"
printf '%s' "$FAKE_CLIP"
"""
SHIM_CURL = """#!/bin/sh
if [ -n "$CURL_SLEEP" ]; then : > "$CURL_MARK"; sleep 30; fi
printf '000'
exit 7
"""
SHIM_OPEN = "#!/bin/sh\nexit 0\n"


def real_search_list():
    env = dict(os.environ, HOME=REAL_HOME)
    return subprocess.run([SEC, "list-keychains"], env=env, capture_output=True, text=True).stdout


def real_has(ref):
    env = dict(os.environ, HOME=REAL_HOME)
    r = subprocess.run([SEC, "find-generic-password", "-s", SERVICE, "-a", ref],
                       env=env, capture_output=True, text=True)
    return r.returncode == 0


class Sandbox:
    def __init__(self, clip):
        self.dir = tempfile.mkdtemp(prefix="pigeon-consent-")
        self.home = os.path.join(self.dir, "home")
        self.bin = os.path.join(self.dir, "bin")
        os.makedirs(os.path.join(self.home, "Library", "Keychains"))
        os.makedirs(os.path.join(self.home, "Library", "Preferences"))
        os.makedirs(self.bin)
        self.kc = os.path.join(self.dir, "sandbox.keychain-db")
        for name, body in (("security", SHIM_SECURITY), ("pbpaste", SHIM_PBPASTE),
                           ("curl", SHIM_CURL), ("open", SHIM_OPEN)):
            p = os.path.join(self.bin, name)
            with open(p, "w") as f:
                f.write(body)
            os.chmod(p, 0o755)
        self.pb_log = os.path.join(self.dir, "pbpaste.log")
        self.curl_mark = os.path.join(self.dir, "curl.started")
        kenv = dict(os.environ, HOME=self.home)
        subprocess.run([SEC, "create-keychain", "-p", "sandbox", self.kc], env=kenv, check=True,
                       capture_output=True)
        subprocess.run([SEC, "unlock-keychain", "-p", "sandbox", self.kc], env=kenv, check=True,
                       capture_output=True)
        subprocess.run([SEC, "set-keychain-settings", self.kc], env=kenv, check=True,
                       capture_output=True)
        self.env = {
            "HOME": self.home,
            "PATH": self.bin + ":/usr/bin:/bin:/usr/sbin:/sbin",
            "TERM": "xterm",
            "LANG": "en_US.UTF-8",
            "SANDBOX_KC": self.kc,
            "PB_LOG": self.pb_log,
            "FAKE_CLIP": clip,
            "CURL_MARK": self.curl_mark,
        }

    def stored(self, ref):
        r = subprocess.run([SEC, "find-generic-password", "-s", SERVICE, "-a", ref, "-w", self.kc],
                           capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else None

    def index(self):
        p = os.path.join(self.home, ".local", "share", "pigeon", "index")
        return open(p).read().strip() if os.path.exists(p) else ""

    def pb_called(self):
        return os.path.exists(self.pb_log)

    def close(self):
        subprocess.run([SEC, "delete-keychain", self.kc], capture_output=True)
        shutil.rmtree(self.dir, ignore_errors=True)


def drive(sb, ref, steps, extra_env=None, timeout=20):
    """steps: list of (regex to wait for, bytes to send). Returns (exit_code, output)."""
    env = dict(sb.env, **(extra_env or {}))
    pid, fd = pty.fork()
    if pid == 0:
        os.execve("/bin/zsh", ["/bin/zsh", COO, "add", ref], env)
    out = b""
    pos = 0
    deadline = time.time() + timeout
    reaped = [None]

    def pump(until_re=None):
        nonlocal out
        while time.time() < deadline:
            if until_re is not None and re.search(until_re, out[pos:].decode("utf-8", "replace")):
                return True
            r, _, _ = select.select([fd], [], [], 0.2)
            if r:
                try:
                    chunk = os.read(fd, 4096)
                except OSError:
                    return until_re is None
                if not chunk:
                    return until_re is None
                out += chunk
            elif reaped[0] is None:
                wp, st = os.waitpid(pid, os.WNOHANG)
                if wp:
                    reaped[0] = st
                    if until_re is None:
                        return True
        return False

    for pat, send in steps:
        if not pump(pat):
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
            raise AssertionError(f"timed out waiting for {pat!r}\n--- output ---\n{out.decode('utf-8','replace')}")
        pos = len(out)
        if send is not None:
            time.sleep(0.15)
            os.write(fd, send)
    if not pump(None) and reaped[0] is None:
        # still running at the deadline: it is waiting for input it should not need
        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)
        os.close(fd)
        raise AssertionError("coo was still running at the deadline\n" + out.decode("utf-8", "replace"))
    status = reaped[0] if reaped[0] is not None else os.waitpid(pid, 0)[1]
    os.close(fd)
    code = os.waitstatus_to_exitcode(status)
    return code, out.decode("utf-8", "replace")


Q1 = r"read your clipboard for .*\[y/N\] ▸ "
Q2 = r"store it as .*\[y/N\] ▸ "
GUIDE_OPEN = r"press o to open ▸ "
PASTE = r"paste it here \(hidden, Enter to cancel\) ▸ "
HOME_Q = r"which file should hold it\? .*▸ "

results = []


def case(name, clip, ref, steps, want_code, want_stored, want_pb, extra_env=None, key=None):
    sb = Sandbox(clip)
    try:
        try:
            code, out = drive(sb, ref, steps, extra_env)
        except AssertionError as e:
            code, out = None, str(e)
        got = sb.stored(ref)
        problems = [] if code is not None else ["flow did not reach the expected prompt"]
        if want_code == "nonzero":
            if code == 0:
                problems.append(f"exit {code}, want non-zero")
        elif code != want_code:
            problems.append(f"exit {code}, want {want_code}")
        if want_stored and got != clip:
            problems.append("value not stored in sandbox keychain")
        if not want_stored and got is not None:
            problems.append("value STORED but must not be")
        if not want_stored and sb.index():
            problems.append(f"index not empty: {sb.index()!r}")
        if want_pb is False and sb.pb_called():
            problems.append("clipboard was read before consent")
        if want_pb is True and not sb.pb_called():
            problems.append("clipboard was never read")
        if clip in out:
            problems.append("full value printed on screen")
        ok = not problems
        results.append((name, ok, problems, out if not ok else ""))
        print(("PASS " if ok else "FAIL ") + name + (f"  (exit {code})"))
        for p in problems:
            print("     - " + p)
    finally:
        sb.close()


def main():
    if sys.platform != "darwin":
        print("SKIP: macOS keychain tests")
        return 0
    before = real_search_list()

    enter_cancel = [(GUIDE_OPEN, b"\n"), (PASTE, b"\n")]

    case("empty answer at 'read clipboard?' stores nothing, clipboard untouched",
         SG_KEY, SG_REF, [(Q1, b"\n")] + enter_cancel, 0, False, False)
    case("'n' at 'read clipboard?' stores nothing, clipboard untouched",
         SG_KEY, SG_REF, [(Q1, b"n\n")] + enter_cancel, 0, False, False)
    case("'yolo' at 'read clipboard?' is not yes",
         SG_KEY, SG_REF, [(Q1, b"yolo\n")] + enter_cancel, 0, False, False)
    case("empty answer at 'store it?' stores nothing",
         SG_KEY, SG_REF, [(Q1, b"y\n"), (Q2, b"\n")] + enter_cancel, 0, False, True)
    case("'n' at 'store it?' stores nothing",
         SG_KEY, SG_REF, [(Q1, b"yes\n"), (Q2, b"n\n")] + enter_cancel, 0, False, True)
    case("Ctrl+C at 'read clipboard?' exits 130, nothing stored",
         SG_KEY, SG_REF, [(Q1, b"\x03")], 130, False, False)
    case("Ctrl+C at 'store it?' exits 130, nothing stored",
         SG_KEY, SG_REF, [(Q1, b"y\n"), (Q2, b"\x03")], 130, False, True)
    case("EOF at 'read clipboard?' exits non-zero, nothing stored",
         SG_KEY, SG_REF, [(Q1, b"\x04")], "nonzero", False, False)
    case("EOF at 'store it?' exits non-zero, nothing stored",
         SG_KEY, SG_REF, [(Q1, b"y\n"), (Q2, b"\x04")], "nonzero", False, True)

    # Ctrl+C while the live probe is in flight. The curl shim sleeps and drops a
    # marker; the interrupt is sent once the marker exists.
    sb = Sandbox(ANT_KEY)
    try:
        try:
            code, out = drive_probe_int(sb, ANT_REF, [(Q1, b"y\n"), (Q2, b"y\n")], {"CURL_SLEEP": "1"})
        except AssertionError as e:
            code, out = None, str(e)
        got = sb.stored(ANT_REF)
        problems = []
        if code != 130:
            problems.append(f"exit {code}, want 130")
        if got is not None:
            problems.append("value STORED but must not be")
        if sb.index():
            problems.append("index not empty")
        if ANT_KEY in out:
            problems.append("full value printed on screen")
        ok = not problems
        results.append(("Ctrl+C during the live probe", ok, problems, out if not ok else ""))
        print(("PASS " if ok else "FAIL ") + f"Ctrl+C during the live probe exits 130, nothing stored  (exit {code})")
        for p in problems:
            print("     - " + p)
    finally:
        sb.close()

    case("'y' then 'y' stores in the SANDBOX keychain",
         SG_KEY, SG_REF, [(Q1, b"y\n"), (Q2, b"y\n"), (HOME_Q, b"\n")], 0, True, True)

    after = real_search_list()
    real_ok = True
    for ref in (SG_REF, ANT_REF):
        if real_has(ref):
            real_ok = False
            print(f"FAIL real login keychain holds {ref}")
    if before != after:
        real_ok = False
        print("FAIL the real keychain search list changed")
    if real_ok:
        print("PASS real keychain untouched (test refs absent, search list unchanged)")

    failed = [r for r in results if not r[1]]
    for name, _, _, out in failed:
        print(f"\n--- output of failed case: {name} ---\n{out}")
    print(f"\n{len(results) - len(failed)}/{len(results)} cases passed" + ("" if real_ok else ", REAL KEYCHAIN CHECK FAILED"))
    return 0 if (not failed and real_ok) else 1


def drive_probe_int(sb, ref, steps, extra_env):
    env = dict(sb.env, **extra_env)
    pid, fd = pty.fork()
    if pid == 0:
        os.execve("/bin/zsh", ["/bin/zsh", COO, "add", ref], env)
    out = b""
    pos = 0
    deadline = time.time() + 25

    def read_some():
        nonlocal out
        r, _, _ = select.select([fd], [], [], 0.2)
        if r:
            try:
                chunk = os.read(fd, 4096)
            except OSError:
                return False
            if not chunk:
                return False
            out += chunk
        return True

    for pat, send in steps:
        while time.time() < deadline and not re.search(pat, out[pos:].decode("utf-8", "replace")):
            if not read_some():
                break
        pos = len(out)
        time.sleep(0.15)
        os.write(fd, send)
    while time.time() < deadline and not os.path.exists(sb.curl_mark):
        read_some()
    if not os.path.exists(sb.curl_mark):
        os.kill(pid, signal.SIGKILL)
        os.waitpid(pid, 0)
        raise AssertionError("probe never started\n" + out.decode("utf-8", "replace"))
    time.sleep(0.3)
    os.write(fd, b"\x03")
    status = None
    while time.time() < deadline:
        if not read_some():
            break
        wp, st = os.waitpid(pid, os.WNOHANG)
        if wp:
            status = st
            break
    if status is None:
        # the pty can close a moment before the process is reapable
        t_end = time.time() + 5
        wp = 0
        while time.time() < t_end:
            wp, st = os.waitpid(pid, os.WNOHANG)
            if wp:
                break
            time.sleep(0.05)
        if wp:
            status = st
        else:
            os.kill(pid, signal.SIGKILL)
            os.waitpid(pid, 0)
            os.close(fd)
            raise AssertionError("coo kept running after Ctrl+C\n" + out.decode("utf-8", "replace"))
    os.close(fd)
    return os.waitstatus_to_exitcode(status), out.decode("utf-8", "replace")

if __name__ == "__main__":
    sys.exit(main())
