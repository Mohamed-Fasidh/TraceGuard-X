from dataclasses import dataclass

@dataclass(frozen=True)
class Requirement:
    requirement_id: str
    text: str
    verification_priority: int

def build_requirement_graph(trace):
    """
    Converts natural-language requirements into an inspectable requirement
    graph. The graph is deterministic for the included benchmark and is
    designed so an LLM can later enrich it without changing the schema.
    """
    reqs = []
    for i, text in enumerate(trace.requirements, 1):
        priority = 100
        lower = text.lower()
        if any(k in lower for k in ("edge", "empty", "missing", "malformed")):
            priority = 120
        reqs.append(Requirement(f"R{i}", text, priority))
    return sorted(reqs, key=lambda x: -x.verification_priority)
