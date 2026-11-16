import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BENIGN = {"git pull", "tail -f app.log", "cd /var/log", "ls -la",
          "systemctl status nginx"}


def run(tmp_path):
    out = tmp_path / "timeline.json"
    r = subprocess.run(
        [sys.executable, "-I", os.path.join(ROOT, "triage.py"),
         os.path.join(ROOT, "evidence"), str(out)],
        capture_output=True, text=True)
    return r, out


def report(tmp_path):
    r, out = run(tmp_path)
    assert r.returncode == 0, r.stderr
    return json.loads(out.read_text(encoding="utf-8"))


def test_evidence_present():
    for name in ("bash_history.txt", "auth_excerpt.log", "files.txt"):
        assert os.path.exists(os.path.join(ROOT, "evidence", name))


def test_labels_have_entry_and_persistence():
    with open(os.path.join(ROOT, "labels.json"), encoding="utf-8") as fh:
        labels = json.load(fh)
    assert labels["entry_vector"]
    assert labels["persistence"]


def test_triage_runs(tmp_path):
    rep = report(tmp_path)
    assert "hits" in rep


def test_hits_have_file_and_line(tmp_path):
    rep = report(tmp_path)
    for h in rep["hits"]:
        assert h.get("file") and h.get("line")


def test_noise_commands_never_reported(tmp_path):
    rep = report(tmp_path)
    texts = [h["text"] for h in rep["hits"]]
    for benign in BENIGN:
        assert benign not in texts, f"benign command misreported: {benign}"
    # and the suppression block accounts for all 25 benign history rows
    assert rep["noise_suppressed"]["count"] == 25
    assert set(rep["noise_suppressed"]["commands"]) == BENIGN


def test_verdict_is_unauthorized_and_cited(tmp_path):
    rep = report(tmp_path)
    v = rep["verdict"]
    assert v["classification"] == "unauthorized_tampering"
    assert v["account"] == "ops"
    assert v["entry_vector"] == "sudo misconfiguration"
    assert v["persistence"] == "sudoers edit"
    # every rationale point that makes a claim carries a file/line citation
    for point in v["rationale"]:
        if point["evidence"]:
            for cite in point["evidence"]:
                assert cite["file"] and cite["line"]


def test_sudoers_before_after_diff(tmp_path):
    rep = report(tmp_path)
    diff = rep["sudoers_diff"]
    joined_after = " ".join(diff["after_observed"])
    assert "NOPASSWD" in joined_after and "ops" in joined_after
    assert any(line.startswith("+") for line in diff["unified_diff"])
    # baseline must be honestly labelled as inferred (no backup exists)
    assert "inferred" in diff["baseline_basis"].lower()
    assert diff["evidence"][0]["file"] == "sudoers.frag"
    assert diff["evidence"][0]["line"] == 3


def test_timeline_ordered_and_cited(tmp_path):
    rep = report(tmp_path)
    ts = [e["ts"] for e in rep["timeline"] if e["ts"]]
    assert ts == sorted(ts)
    for e in rep["timeline"]:
        assert e["evidence"] and e["evidence"][0]["file"]
        assert e["evidence"][0]["line"]


def test_timestamp_dependence_documented(tmp_path):
    rep = report(tmp_path)
    dep = rep["timestamp_dependence"]
    assert dep["conclusions_relying_on_timestamps"]
    assert dep["conclusions_independent_of_timestamps"]
    assert "tamper" in dep["tamper_warning"].lower()


def test_clock_skew_flagged(tmp_path):
    rep = report(tmp_path)
    assert rep["clock_findings"], "history/auth clock discrepancy must be reported"
    finding = rep["clock_findings"][0]
    assert abs(finding["delta_minutes"]) > 40
    assert finding["evidence"]


def test_all_citations_point_to_real_lines(tmp_path):
    rep = report(tmp_path)
    ev_dir = os.path.join(ROOT, "evidence")
    lengths = {}
    for name in os.listdir(ev_dir):
        with open(os.path.join(ev_dir, name), encoding="utf-8") as fh:
            lengths[name] = sum(1 for _ in fh)

    def walk(obj):
        if isinstance(obj, dict):
            if "file" in obj and "line" in obj and obj["file"] in lengths:
                lines = obj["line"]
                lines = lines if isinstance(lines, list) else [lines]
                for ln in lines:
                    assert 1 <= ln <= lengths[obj["file"]], \
                        f"{obj['file']}:{ln} out of range"
            for v in obj.values():
                walk(v)
        elif isinstance(obj, list):
            for v in obj:
                walk(v)

    walk(rep)
