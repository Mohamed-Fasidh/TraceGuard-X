# TraceGuard X — Reproduction Guide

## 1. Clean Environment

TraceGuard X requires:

- Python 3.10+
- Docker Desktop / Docker Engine
- Git

The advanced evaluator executes candidate code inside a Docker sandbox.

Create a virtual environment:

```bash
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
```

### Linux / macOS

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Verify Docker

Check the Docker installation:

```bash
docker version
```

Then verify that the TraceGuard sandbox can actually start:

```powershell
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --memory 128m --cpus 0.50 --pids-limit 32 python:3.11-slim python -c "print('TRACEGUARD_DOCKER_OK')"
```

Expected output:

```text
TRACEGUARD_DOCKER_OK
```

Verify the project workspace can also be mounted:

```powershell
docker run --rm --network none --read-only --cap-drop ALL --security-opt no-new-privileges --memory 128m --cpus 0.50 --pids-limit 32 -v "${PWD}:/work:ro" -w /work python:3.11-slim python -c "print('TRACEGUARD_MOUNT_OK')"
```

Expected output:

```text
TRACEGUARD_MOUNT_OK
```

The first Docker run may download:

```text
python:3.11-slim
```

This is expected.

---

## 3. Run Repository Tests

Run:

```bash
python -m pytest -q
```

The current repository test suite contains:

```text
6 tests
```

A successful run should report:

```text
6 passed
```

Execution time may vary depending on the machine.

---

## 4. Run the Baseline

The baseline evaluator can be executed with:

```bash
python -m baseline.baseline \
  --data data/traces \
  --output artifacts/baseline_results.json
```

This produces:

```text
artifacts/baseline_results.json
```

The baseline intentionally represents the simpler evaluation approach and does not perform the complete independent verification workflow used by TraceGuard X.

---

## 5. Run the Advanced Evaluator

First ensure Docker is running.

Then execute:

```bash
python -m src.traceguard.pipeline \
  --data data/traces \
  --output artifacts/advanced_results.json
```

The advanced pipeline performs:

1. Trace analysis
2. Claim extraction
3. Requirement-graph construction
4. Verification planning
5. Bounded adversarial case generation
6. Static analysis
7. Independent Docker sandbox execution
8. Evidence reconciliation
9. Deterministic scoring
10. Human-review recommendation
11. Evidence-graph construction

The generated result is:

```text
artifacts/advanced_results.json
```

The V3 benchmark contains:

```text
40 traces
```

---

## 6. Compare Baseline and Advanced

Run:

```bash
python -m evaluation.compare \
  --baseline artifacts/baseline_results.json \
  --advanced artifacts/advanced_results.json \
  --ground data/ground_truth.json
```

This generates:

```text
artifacts/comparison.json
```

The comparison contains:

- Verdict accuracy
- Absolute improvement
- Relative improvement
- Critical-failure precision
- Critical-failure recall
- Critical-failure F1
- Claim/evidence contradiction precision
- Claim/evidence contradiction recall
- Claim/evidence contradiction F1
- Verification-gap counts
- Sandbox-failure counts
- Confusion matrix
- Per-case error analysis

---

## 7. V3 Benchmark Result

The current V3 benchmark produces:

| Metric | Baseline | Advanced |
|---|---:|---:|
| Verdict accuracy | 20.00% | **100.00%** |
| Benchmark cases | 40 | **40** |
| Incorrect advanced verdicts | — | **0** |

Absolute improvement:

```text
+80 percentage points
```

Relative improvement:

```text
+400%
```

The advanced evaluator correctly classified:

```text
40 / 40 cases
```

These values must come from the generated evaluation artifacts.

They should not be manually edited.

---

## 8. Dashboard

Launch the dashboard:

```bash
streamlit run app.py
```

The dashboard provides an interactive view of evaluation results and evidence.

---

## 9. Reproducibility Design

The benchmark is:

- Synthetic
- Fixed
- Version-controlled
- Shared by baseline and advanced evaluation

Both evaluators consume the same trace files.

The comparison script validates that the evaluated trace IDs match the ground-truth benchmark.

The advanced execution path uses deterministic static checks and the Docker-based candidate harness.

---

## 10. API Cost

The included benchmark is designed to run using the repository's local verification components.

If the configured implementation does not require an external model provider for the benchmark run, the API cost is:

```text
$0
```

Do not report `$0` if an external model/API is actually enabled during the run.

---

## 11. Failure Behavior

If Docker is unavailable or sandbox execution cannot produce candidate evidence, the system must not silently treat the candidate as successfully verified.

TraceGuard X distinguishes between:

```text
Candidate failure
```

and:

```text
Verification failure / evidence gap
```

For example:

```text
sandbox_timeout
verification_gap
```

indicate that independent verification was incomplete.

They are not automatically interpreted as proof that the candidate implementation itself failed.

---

## 12. Synthetic Benchmark Validation Without Docker

The repository also provides:

```bash
python -m evaluation.benchmark_validate
```

This utility validates the included synthetic benchmark data without Docker.

It is a dataset-validation utility.

It is **not** a replacement for the Docker sandbox used by the advanced evaluation.

The competition result should be generated using:

```bash
python -m src.traceguard.pipeline
```

rather than only using the local benchmark validator.

---

## 13. Qualification / Preflight Gate

Before presenting final benchmark results, run:

```bash
python scripts/preflight.py
```

The expected preflight artifact is:

```text
artifacts/preflight.json
```

The preflight check should verify the environment and benchmark prerequisites.

Importantly, the presence of the Docker binary alone is not sufficient evidence that the sandbox works.

The actual Docker execution path must also succeed.

---

## 14. Final Artifact Set

A complete evaluation should produce:

```text
artifacts/
├── baseline_results.json
├── advanced_results.json
├── comparison.json
├── preflight.json
└── mutation_report.json
```

Where supported by the repository, these artifacts provide the evidence used for the final evaluation and presentation.

If an artifact is not generated by the current repository configuration, it should not be presented as if it exists.

---

## 15. Benchmark Data

The benchmark traces are stored under:

```text
data/traces/
```

Ground-truth labels are stored under:

```text
data/ground_truth.json
```

The V3 benchmark contains 40 cases:

| Category | Cases |
|---|---:|
| Correct | 8 |
| Logic failures | 7 |
| Runtime failures | 6 |
| Missing requirements | 5 |
| False-success / output claims | 4 |
| Syntax failures | 3 |
| Dependency failures | 3 |
| Timeout failures | 4 |
| **Total** | **40** |

Each trace contains six explicit verification inputs.

---

## 16. Security Configuration

The advanced sandbox requests:

```text
--network none
--read-only
--cap-drop ALL
--security-opt no-new-privileges
--memory 128m
--cpus 0.50
--pids-limit 32
```

The candidate runs in an isolated Docker environment with a disposable workspace.

Docker is a practical containment boundary for this project and is not presented as a formal security proof.

---

## 17. Full Reproduction Sequence

From a clean environment:

```bash
python -m venv .venv
```

Activate the environment and install dependencies:

```bash
pip install -r requirements.txt
```

Run tests:

```bash
python -m pytest -q
```

Run baseline:

```bash
python -m baseline.baseline \
  --data data/traces \
  --output artifacts/baseline_results.json
```

Run advanced:

```bash
python -m src.traceguard.pipeline \
  --data data/traces \
  --output artifacts/advanced_results.json
```

Compare:

```bash
python -m evaluation.compare \
  --baseline artifacts/baseline_results.json \
  --advanced artifacts/advanced_results.json \
  --ground data/ground_truth.json
```

Inspect:

```text
artifacts/comparison.json
```

Optional dashboard:

```bash
streamlit run app.py
```

---

## 18. Reproducibility Rule

Do not manually edit:

```text
artifacts/baseline_results.json
artifacts/advanced_results.json
artifacts/comparison.json
```

Regenerate them using the commands in this guide.

The final benchmark metrics should always be derived from:

```text
data/traces/
data/ground_truth.json
baseline_results.json
advanced_results.json
evaluation/compare.py
```

---

## 19. Final Result Integrity

The final presentation should use only generated benchmark artifacts.

The evaluation flow is:

```text
                data/traces
                     |
          +----------+----------+
          |                     |
          v                     v
      Baseline             TraceGuard X
          |                     |
          v                     v
 baseline_results.json   advanced_results.json
          |                     |
          +----------+----------+
                     |
                     v
          evaluation/compare.py
                     |
                     v
             comparison.json
```

This prevents manually fabricated benchmark claims.

---

## 20. Final V3 Result

The current V3 experiment demonstrates:

```text
Baseline accuracy
20.00%

        |
        | +80 percentage points
        v

Advanced accuracy
100.00%
```

Across:

```text
40 benchmark cases
```

the advanced evaluator produced:

```text
40 / 40 correct verdicts
0 incorrect advanced verdicts
```

The final principle is:

> **Claims are hypotheses. Independent evidence is verification.**
