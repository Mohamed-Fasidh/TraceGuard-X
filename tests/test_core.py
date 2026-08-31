import json
from pathlib import Path
from src.traceguard.agents.trace_analyst import analyze
from src.traceguard.tools.static_analyzer import analyze as static
from src.traceguard.scoring.scorer import score
from src.traceguard.schemas import ExecutionEvidence, StaticEvidence

def test_trace_analysis():
    raw = json.loads(Path("data/traces/trace_003.json").read_text())
    t = analyze(raw)
    assert t.trace_id == "003"
    assert t.claimed_verdict == "PASS"

def test_static_analysis():
    assert static("def solve(x):\n return x").syntax_ok
    assert not static("def solve(x)\n return x").syntax_ok

def test_failed_score():
    result = score(None, StaticEvidence(syntax_ok=True),
                   ExecutionEvidence(executed=True, exit_code=1),
                   [{"category":"runtime_error","severity":"high","message":"boom"}])
    assert result["verdict"] == "FAIL"
    assert result["score"] < 60
