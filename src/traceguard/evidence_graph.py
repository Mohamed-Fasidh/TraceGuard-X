from dataclasses import dataclass, asdict

@dataclass
class EvidenceNode:
    node_id: str
    node_type: str
    label: str
    source: str

@dataclass
class EvidenceEdge:
    from_id: str
    to_id: str
    relation: str

def build_evidence_graph(trace, plan, static, execution, findings):
    nodes = [
        EvidenceNode("T1", "trace", "Agent trajectory", "trajectory"),
        EvidenceNode("C1", "claim", trace.claimed_verdict, "agent"),
    ]
    edges = [EvidenceEdge("T1", "C1", "contains_claim")]

    for i, item in enumerate(plan, 1):
        nid = f"V{i}"
        nodes.append(EvidenceNode(nid, "verification", item, "planner"))
        edges.append(EvidenceEdge("C1", nid, "challenged_by"))

    nodes.append(EvidenceNode("S1", "static", str(static.model_dump()), "static_analyzer"))
    edges.append(EvidenceEdge("V1", "S1", "produces_evidence"))

    nodes.append(EvidenceNode(
        "E1", "execution",
        f"exit={execution.exit_code}; tests={execution.tests_passed}/{execution.tests_total}",
        "docker_sandbox"
    ))
    edges.append(EvidenceEdge("V1", "E1", "produces_evidence"))

    for i, finding in enumerate(findings, 1):
        fid = f"F{i}"
        nodes.append(EvidenceNode(fid, "finding", finding["message"], "reconciler"))
        edges.append(EvidenceEdge("E1", fid, "supports"))

    return {
        "nodes": [asdict(x) for x in nodes],
        "edges": [asdict(x) for x in edges],
    }
