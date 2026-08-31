from src.traceguard.agent_runtime import AgentRuntime
from src.traceguard.tools.property_checker import identity_property_spec
from src.traceguard.agents.adversarial_verifier import generate_cases
from src.traceguard.schemas import Trace

def test_agent_runtime_records_handoff():
    rt = AgentRuntime("T")
    out = rt.run_agent(
        "planner", "plan", "test", {"x": 1}, lambda x: {"planned": True},
        feedback="next"
    )
    assert out["planned"] is True
    assert rt.to_dict()["events"][0]["feedback"] == "next"

def test_property_checker_is_spec_only():
    spec = identity_property_spec()
    assert spec["name"] == "identity"
    assert len(spec["inputs"]) >= 5

def test_adversarial_budget():
    trace = Trace(
        trace_id="x", task="identity", requirements=[],
        code="def solve(x): return x", trajectory=""
    )
    cases = generate_cases(trace, budget=4)
    assert len(cases) == 4
