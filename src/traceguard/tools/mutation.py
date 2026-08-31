import ast
import copy

class Mutation:
    def __init__(self, mutation_id, description, source):
        self.mutation_id = mutation_id
        self.description = description
        self.source = source

def generate_mutations(code):
    """
    Small deterministic mutation operator set. A real implementation can
    expand this with mutmut/cosmic-style operators.
    """
    mutations = []
    if "return x" in code:
        mutations.append(Mutation("M1", "replace identity return with None",
                                  code.replace("return x", "return None", 1)))
        mutations.append(Mutation("M2", "uppercase identity return",
                                  code.replace("return x", "return x.upper()", 1)))
        mutations.append(Mutation("M3", "constant wrong return",
                                  code.replace("return x", "return 'wrong'", 1)))
    return mutations[:8]

def mutation_kill_rate(original_code, verifier):
    """
    A mutation is killed if the verifier detects the mutated implementation as
    failing. This metric evaluates the evaluator, not the candidate.
    """
    muts = generate_mutations(original_code)
    if not muts:
        return {"total": 0, "killed": 0, "rate": 1.0, "mutations": []}

    rows = []
    killed = 0
    for m in muts:
        result = verifier(m.source)
        is_killed = result.get("verdict") == "FAIL"
        killed += int(is_killed)
        rows.append({
            "mutation_id": m.mutation_id,
            "description": m.description,
            "killed": is_killed,
        })
    return {
        "total": len(muts),
        "killed": killed,
        "rate": killed / len(muts),
        "mutations": rows,
    }
