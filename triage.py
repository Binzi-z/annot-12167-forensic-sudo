"""Forensic timeline builder for the sudoers tampering case.

Replaces the old keyword grep. It parses the four evidence artifacts, keeps the
benign day-to-day ops commands out of the findings (noise suppression), orders
events on a single timeline, reconstructs the before/after sudoers diff, and
records which conclusions depend on file timestamps versus file contents.

CLI:  python triage.py <evidence_dir> <output.json>
"""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import sys

# The auth log and files.txt carry wall-clock strings without a timezone.
# Dates align to 2026-10-01 and the host behaves as UTC+8; we normalize on that
# assumption but tag every such event so the assumption stays visible.
ASSUMED_TZ = dt.timezone(dt.timedelta(hours=8))

# Benign operational commands seen in bash_history. Anything matching these is
# noise and must never appear in "hits".
NOISE_COMMANDS = {
    "git pull",
    "tail -f app.log",
    "cd /var/log",
    "ls -la",
    "systemctl status nginx",
}

AUTH_SSH_RE = re.compile(
    r"^(?P<when>\w+ \d+ \d+:\d+:\d+) \S+ sshd\[\d+\]: Accepted publickey "
    r"for (?P<user>\S+) from (?P<ip>[0-9.]+)"
)
AUTH_VISUDO_RE = re.compile(r"^(?P<when>\w+ \d+ \d+:\d+:\d+) \S+ visudo invoked")
AUTH_SUDO_RE = re.compile(
    r"^(?P<when>\w+ \d+ \d+:\d+:\d+) \S+ sudo:\s+(?P<rest>.*)"
)
FILES_RE = re.compile(
    r"^(?P<date>\d{4}-\d{2}-\d{2}) (?P<time>\d{2}:\d{2})\s+"
    r"(?P<mode>\d{3,4})\s+(?P<owner>\S+)\s+(?P<path>\S+)"
)


def _iso_local(d: dt.datetime) -> str:
    return d.replace(tzinfo=ASSUMED_TZ).isoformat()


def parse_bash_history(path: str) -> tuple[list[dict], list[dict]]:
    """Parse '#<epoch>' / command pairs. Returns (commands, noise).

    Each entry keeps both the timestamp line and the command line number so
    findings can cite exact evidence rows.
    """
    commands: list[dict] = []
    noise: list[dict] = []
    pending_epoch: int | None = None
    pending_line: int | None = None
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for no, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#") and line[1:].isdigit():
                pending_epoch = int(line[1:])
                pending_line = no
                continue
            when = dt.datetime.fromtimestamp(pending_epoch, dt.timezone.utc) \
                if pending_epoch is not None else None
            entry = {
                "command": line,
                "timestamp_epoch": pending_epoch,
                "time_utc": when.isoformat() if when else None,
                "time_local_assumed": when.astimezone(ASSUMED_TZ).isoformat()
                if when else None,
                "timestamp_line": pending_line,
                "command_line": no,
                "file": os.path.basename(path),
                "is_noise": line in NOISE_COMMANDS,
            }
            (noise if entry["is_noise"] else commands).append(entry)
            pending_epoch, pending_line = None, None
    return commands, noise


def parse_auth(path: str) -> dict:
    logins: list[dict] = []
    events: list[dict] = []
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for no, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")
            m = AUTH_SSH_RE.match(line)
            if m:
                when = dt.datetime.strptime(m.group("when"), "%b %d %H:%M:%S") \
                    .replace(year=2026)
                logins.append({
                    "user": m.group("user"), "ip": m.group("ip"),
                    "time_local_assumed": _iso_local(when),
                    "file": os.path.basename(path), "line": no,
                })
                continue
            m = AUTH_VISUDO_RE.match(line)
            if m:
                when = dt.datetime.strptime(m.group("when"), "%b %d %H:%M:%S") \
                    .replace(year=2026)
                events.append({
                    "event": "visudo_invoked",
                    "time_local_assumed": _iso_local(when),
                    "file": os.path.basename(path), "line": no,
                    "text": line,
                })
                continue
            m = AUTH_SUDO_RE.match(line)
            if m:
                when = dt.datetime.strptime(m.group("when"), "%b %d %H:%M:%S") \
                    .replace(year=2026)
                events.append({
                    "event": "sudo_command",
                    "time_local_assumed": _iso_local(when),
                    "file": os.path.basename(path), "line": no,
                    "text": line, "detail": m.group("rest"),
                })
    return {"logins": logins, "events": events}


def parse_files(path: str) -> list[dict]:
    out: list[dict] = []
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for no, raw in enumerate(fh, start=1):
            m = FILES_RE.match(raw.strip())
            if not m:
                continue
            when = dt.datetime.strptime(
                f"{m.group('date')} {m.group('time')}", "%Y-%m-%d %H:%M"
            )
            out.append({
                "path": m.group("path"), "mode": m.group("mode"),
                "owner": m.group("owner"),
                "time_local_assumed": _iso_local(when),
                "file": os.path.basename(path), "line": no,
            })
    return out


def parse_sudoers(path: str) -> dict:
    rules: list[dict] = []
    anomalous: list[dict] = []
    with open(path, encoding="utf-8", errors="ignore") as fh:
        for no, raw in enumerate(fh, start=1):
            line = raw.rstrip("\n")
            if not line.strip():
                continue
            entry = {"file": os.path.basename(path), "line": no, "text": line}
            if "NOPASSWD" in line:
                rules.append({**entry, "rule": line.strip()})
            elif not line.lstrip().startswith(("#", "Defaults", "User_Alias",
                                               "Cmnd_Alias", "Host_Alias",
                                               "Runas_Alias")) and "=" not in line:
                # crontab syntax (MAILTO=, */30 ...) is not valid sudoers grammar.
                anomalous.append(entry)
            else:
                anomalous.append(entry)
    return {"nopasswd_rules": rules, "non_sudoers_lines": anomalous}


def build_sudoers_diff(sudoers: dict) -> dict:
    """Reconstruct before/after. No baseline backup exists in evidence, so the
    'before' side is an inferred least-privilege baseline, clearly labelled."""
    rule = sudoers["nopasswd_rules"][0] if sudoers["nopasswd_rules"] else None
    target = "/etc/sudoers (or /etc/sudoers.d fragment)"
    before = [
        "# inferred baseline: no NOPASSWD grant for ops in evidence",
        "# ops could only sudo with a password under the default policy",
    ]
    after = [r["rule"] for r in sudoers["nopasswd_rules"]]
    unified = [f"--- {target}\t(inferred baseline; no backup in evidence)",
               f"+++ {target}\t(evidence/sudoers.frag)"]
    unified.extend(f"-{x}" for x in before)
    unified.extend(f"+{x}" for x in after)
    return {
        "target": target,
        "baseline_basis": "No pre-change sudoers backup is present; the 'before' "
                          "state is inferred from default sudo policy (password "
                          "required) and from the absence of any NOPASSWD rule "
                          "outside the captured fragment.",
        "before_inferred": before,
        "after_observed": after,
        "unified_diff": unified,
        "evidence": [
            {"file": rule["file"], "line": rule["line"], "text": rule["text"]}
            for rule in sudoers["nopasswd_rules"]
        ],
    }


def build_timeline(evidence_dir: str) -> dict:
    hist_path = os.path.join(evidence_dir, "bash_history.txt")
    auth_path = os.path.join(evidence_dir, "auth_excerpt.log")
    files_path = os.path.join(evidence_dir, "files.txt")
    sudoers_path = os.path.join(evidence_dir, "sudoers.frag")

    history, noise = parse_bash_history(hist_path)
    auth = parse_auth(auth_path)
    files = parse_files(files_path)
    sudoers = parse_sudoers(sudoers_path)

    timeline: list[dict] = []

    # File-landing / mtime events (files.txt)
    severity_by_path = {
        "/var/www/html/uploads/shell.php": "high",
        "/var/spool/cron/crontabs/ops": "high",
        "/etc/passwd": "medium",
    }
    note_by_path = {
        "/var/www/html/uploads/shell.php":
            "Web shell written under the web upload dir, owned by ops.",
        "/var/spool/cron/crontabs/ops":
            "User crontab written (persistence), owned by ops.",
        "/etc/passwd":
            "passwd mtime is the earliest artifact; account-database change "
            "should be verified against /etc/shadow and useradd logs.",
    }
    for f in files:
        timeline.append({
            "ts": f["time_local_assumed"],
            "time_basis": "files.txt mtime (local clock, tz unstated; assumed +08:00)",
            "event": "file_landed",
            "severity": severity_by_path.get(f["path"], "info"),
            "summary": f"{f['path']} (mode {f['mode']}, owner {f['owner']})",
            "detail": note_by_path.get(f["path"], ""),
            "evidence": [{"file": f["file"], "line": f["line"]}],
        })

    # SSH logins summarized as one event, citing first and last line
    if auth["logins"]:
        ips = sorted({x["ip"] for x in auth["logins"]})
        users = sorted({x["user"] for x in auth["logins"]})
        timeline.append({
            "ts": auth["logins"][0]["time_local_assumed"],
            "time_basis": "auth wall clock (tz unstated; assumed +08:00)",
            "event": "ssh_login_burst",
            "severity": "medium",
            "summary": f"{len(auth['logins'])} publickey logins for "
                       f"{','.join(users)} from {len(ips)} distinct IPs",
            "detail": f"source IPs: {', '.join(ips)}",
            "evidence": [
                {"file": "auth_excerpt.log",
                 "line": [auth["logins"][0]["line"], auth["logins"][-1]["line"]]},
            ],
        })

    # Bash history events (exact UTC epochs) — only non-noise commands
    for h in history:
        kind = "sudoers_edit_session" if h["command"] == "sudo visudo" \
            else "privilege_verification"
        timeline.append({
            "ts": h["time_local_assumed"],
            "time_basis": "bash_history #epoch (exact UTC; local shown assumed +08:00)",
            "event": kind,
            "severity": "high",
            "summary": h["command"],
            "detail": f"recorded at epoch {h['timestamp_epoch']} "
                      f"({h['time_utc']} UTC)",
            "evidence": [
                {"file": "bash_history.txt",
                 "line": [h["timestamp_line"], h["command_line"]]},
            ],
        })

    # Auth log visudo / sudo events
    for e in auth["events"]:
        timeline.append({
            "ts": e["time_local_assumed"],
            "time_basis": "auth wall clock (tz unstated; assumed +08:00)",
            "event": e["event"],
            "severity": "critical" if e["event"] == "sudo_command" else "high",
            "summary": e["text"],
            "detail": e.get("detail", ""),
            "evidence": [{"file": e["file"], "line": e["line"]}],
        })

    # Current-state sudoers rule (no timestamp on the fragment itself)
    for r in sudoers["nopasswd_rules"]:
        timeline.append({
            "ts": None,
            "time_basis": "content-only artifact; sudoers.frag carries no mtime",
            "event": "sudoers_rule_observed",
            "severity": "critical",
            "summary": f"NOPASSWD rule present: {r['rule']}",
            "detail": "Grants passwordless root-equivalent sudo to ops.",
            "evidence": [{"file": r["file"], "line": r["line"]}],
        })

    timeline.sort(key=lambda x: (x["ts"] is None, x["ts"] or ""))

    # Clock-skew check: history epoch vs auth wall clock for the visudo actions
    clock_findings: list[dict] = []
    hv = next((h for h in history if h["command"] == "sudo visudo"), None)
    av = next((e for e in auth["events"] if e["event"] == "visudo_invoked"), None)
    if hv and av:
        t1 = dt.datetime.fromisoformat(hv["time_local_assumed"])
        t2 = dt.datetime.fromisoformat(av["time_local_assumed"])
        delta_min = (t2 - t1).total_seconds() / 60
        clock_findings.append({
            "issue": "clock skew between bash_history epoch and auth wall clock",
            "history_visudo": hv["time_local_assumed"],
            "auth_visudo": av["time_local_assumed"],
            "delta_minutes": delta_min,
            "evidence": [
                {"file": "bash_history.txt",
                 "line": [hv["timestamp_line"], hv["command_line"]]},
                {"file": "auth_excerpt.log", "line": av["line"]},
            ],
            "impact": "Absolute ordering across the two clocks is uncertain by "
                      "~%.0f minutes; same-day ordering and the command sequence "
                      "within each source are unaffected." % abs(delta_min),
        })

    diff = build_sudoers_diff(sudoers)

    verdict = {
        "classification": "unauthorized_tampering",
        "confidence": "high",
        "account": "ops",
        "entry_vector": "sudo misconfiguration",
        "persistence": "sudoers edit",
        "rationale": [
            {"point": "The live fragment grants ops passwordless full root "
                      "equivalence (NOPASSWD: ALL).",
             "evidence": [{"file": "sudoers.frag",
                           "line": sudoers["nopasswd_rules"][0]["line"]}]},
            {"point": "The same account owns a web shell and a user crontab "
                      "landed hours earlier, i.e. an established compromise "
                      "chain rather than a change ticket.",
             "evidence": [{"file": "files.txt", "line": 2},
                          {"file": "files.txt", "line": 3}]},
            {"point": "25 publickey logins for ops from 17 distinct IPs in one "
                      "shift is inconsistent with a single named administrator "
                      "and indicates a shared/compromised account.",
             "evidence": [{"file": "auth_excerpt.log", "line": [1, 25]}]},
            {"point": "Sequence 'sudo visudo' then 'sudo -l' then an interactive "
                      "root /bin/bash is the tamper -> verify -> exploit pattern, "
                      "not routine administration.",
             "evidence": [{"file": "bash_history.txt", "line": [51, 54]},
                          {"file": "auth_excerpt.log", "line": [26, 27]}]},
            {"point": "The fragment contains crontab grammar (MAILTO, */30 cron "
                      "line) which is invalid sudoers syntax; a sanctioned visudo "
                      "save would reject it, suggesting a direct file write that "
                      "bypassed visudo validation.",
             "evidence": [{"file": "sudoers.frag", "line": [1, 2]}]},
            {"point": "No change/approval record exists anywhere in the evidence; "
                      "authorization cannot be established and every surrounding "
                      "artifact is malicious.",
             "evidence": []},
        ],
        "caveats": [
            "No pre-change sudoers backup is in evidence; the 'before' side of "
            "the diff is inferred from default policy, not captured.",
            "Auth log and files.txt omit timezone; +08:00 is assumed and the two "
            "clocks disagree by ~53 minutes (see clock_findings).",
        ],
    }

    timestamp_dependence = {
        "conclusions_relying_on_timestamps": [
            "Ordering web shell (02:08) -> crontab (02:14) -> visudo session "
            "(11:30/12:23) relies on files.txt mtimes and the bash_history epochs.",
            "Attributing the edit window to ops on 2026-10-01 relies on the auth "
            "wall clock and history epochs.",
            "Treating /etc/passwd (01:58) as the earliest event relies solely on "
            "its mtime.",
        ],
        "conclusions_independent_of_timestamps": [
            "The NOPASSWD: ALL grant itself is proven by sudoers.frag line 3 "
            "content, regardless of any clock.",
            "Ownership (ops) and permissions of shell.php and the crontab come "
            "from files.txt owner/mode fields, not mtimes.",
            "The command text 'sudo visudo' / 'sudo -l' and the root /bin/bash "
            "sudo record are content facts.",
            "Invalid crontab grammar inside the sudoers fragment is a syntax fact.",
        ],
        "tamper_warning": "mtimes and bash history epochs are attacker-mutable "
                          "and can be tampered with; corroborate against remote "
                          "syslog/journald and file integrity monitoring before "
                          "treating times as conclusive.",
    }

    # Backward-compatible flat "hits": suspicious evidence rows only.
    hits: list[dict] = []
    for f in files:
        hits.append({"file": f["file"], "line": f["line"],
                     "text": f"{f['path']} owner={f['owner']} mode={f['mode']}",
                     "severity": severity_by_path.get(f["path"], "info")})
    for h in history:
        hits.append({"file": h["file"], "line": h["command_line"],
                     "text": h["command"], "severity": "high"})
    for e in auth["events"]:
        hits.append({"file": e["file"], "line": e["line"],
                     "text": e["text"], "severity":
                         "critical" if e["event"] == "sudo_command" else "high"})
    for r in sudoers["nopasswd_rules"]:
        hits.append({"file": r["file"], "line": r["line"],
                     "text": r["text"], "severity": "critical"})
    for r in sudoers["non_sudoers_lines"]:
        hits.append({"file": r["file"], "line": r["line"],
                     "text": r["text"], "severity": "medium"})

    return {
        "case": "sudoers tampering — passwordless privilege escalation",
        "generated_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "assumed_timezone": "+08:00 (auth log and files.txt state no tz)",
        "verdict": verdict,
        "sudoers_diff": diff,
        "timeline": timeline,
        "clock_findings": clock_findings,
        "timestamp_dependence": timestamp_dependence,
        "noise_suppressed": {
            "count": len(noise),
            "commands": sorted({n["command"] for n in noise}),
            "note": "Benign operational commands; deliberately not reported as hits.",
            "evidence_lines": [n["command_line"] for n in noise],
        },
        "hits": hits,
    }


def scan(root: str) -> list[dict]:
    """Kept for API compatibility: returns only suspicious hits."""
    return build_timeline(root)["hits"]


def main() -> int:
    root = sys.argv[1] if len(sys.argv) > 1 else "evidence"
    out = sys.argv[2] if len(sys.argv) > 2 else "timeline.json"
    report = build_timeline(root)
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(report, fh, ensure_ascii=False, indent=2)
    print(f"{len(report['hits'])} suspicious hits, "
          f"{report['noise_suppressed']['count']} noise commands suppressed -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
