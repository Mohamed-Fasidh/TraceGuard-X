from typing import Literal
from pydantic import BaseModel, Field

Verdict = Literal["PASS", "FAIL", "PARTIAL", "REVIEW"]

class Trace(BaseModel):
    trace_id: str
    task: str
    requirements: list[str] = Field(default_factory=list)
    code: str
    trajectory: str
    claimed_verdict: str = "UNKNOWN"
    claimed_tests: str = ""
    claimed_exit_code: int | None = None
    claimed_output: str = ""
    case_type: str = "unknown"
    test_cases: list[dict] = Field(default_factory=list)

class StaticEvidence(BaseModel):
    syntax_ok: bool
    compile_error: str | None = None

class ExecutionEvidence(BaseModel):
    executed: bool
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False
    duration_ms: float = 0.0
    tests_passed: int | None = None
    tests_total: int | None = None
    observed_outputs: list = Field(default_factory=list)
    property_passed: bool = False
    cases: list = Field(default_factory=list)

class Finding(BaseModel):
    category: str
    severity: str
    message: str
    evidence: dict = Field(default_factory=dict)
