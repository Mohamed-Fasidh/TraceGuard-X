# Windows + Docker Runbook

Open PowerShell in the repository root.

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/preflight.py
```

Check Docker:

```powershell
docker version
docker info
```

Run the baseline:

```powershell
python -m baseline.baseline --data data/traces --output artifacts/baseline_results.json
```

Run TraceGuard X:

```powershell
python -m src.traceguard.pipeline --data data/traces --output artifacts/advanced_results.json
```

Compare:

```powershell
python -m evaluation.compare --baseline artifacts/baseline_results.json --advanced artifacts/advanced_results.json
```

Generate mutation evidence:

```powershell
python -m evaluation.mutation_report
```

Launch the dashboard:

```powershell
python -m streamlit run app.py
```

If `docker version` succeeds but the advanced command fails, copy the **full error output** into the chat. Do not change the benchmark result files manually.
