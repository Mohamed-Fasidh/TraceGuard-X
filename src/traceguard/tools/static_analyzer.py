import ast
from src.traceguard.schemas import StaticEvidence

def analyze(code: str) -> StaticEvidence:
    try:
        ast.parse(code)
        compile(code, "candidate.py", "exec")
        return StaticEvidence(syntax_ok=True)
    except Exception as exc:
        return StaticEvidence(
            syntax_ok=False,
            compile_error=f"{type(exc).__name__}: {exc}"
        )
