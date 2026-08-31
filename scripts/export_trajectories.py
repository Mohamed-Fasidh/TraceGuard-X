import json
from pathlib import Path

ROOT = Path(".")
results = json.loads(
    (ROOT / "artifacts" / "advanced_results.json").read_text(encoding="utf-8")
)

agents = {
    "trace_analyst": [],
    "requirement_agent": [],
    "verification_planner": [],
    "adversarial_verifier": [],
    "static_analyzer": [],
    "execution_agent": [],
    "auditor": [],
}

for result in results:
    runtime = result.get("agent_runtime", {})

    for event in runtime.get("events", []):
        agent = event.get("agent")

        if agent in agents:
            agents[agent].append({
                "trace_id": runtime.get("trace_id", result.get("trace_id")),
                **event
            })

out = ROOT / "trajectories"
out.mkdir(exist_ok=True)

for agent, events in agents.items():
    path = out / f"{agent}.jsonl"

    with path.open("w", encoding="utf-8") as f:
        for event in events:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")

    print(f"{agent}: {len(events)} events -> {path}")

