"""
Prints the project-to-rubric mapping used during submission review.
"""
RUBRIC = [
    ("Problem & User Value", 15, "Evidence-first verification of coding-agent claims."),
    ("Agent Solution & Engineering", 30, "Trace analysis, verification planning, static checks, sandbox and evidence reconciliation."),
    ("End-to-End Quality", 20, "Dashboard, structured reports, deterministic scoring and review gate."),
    ("Measured Improvement", 15, "Same fixed benchmark for baseline and advanced conditions."),
    ("Reproducibility", 15, "Synthetic data, scripts, pinned dependencies and Docker sandbox."),
    ("Hot Take / Insights", 5, "Independent evidence beats adding another model judge when evidence is the bottleneck."),
]
for name, points, mapping in RUBRIC:
    print(f"{points:>2}  {name}: {mapping}")
