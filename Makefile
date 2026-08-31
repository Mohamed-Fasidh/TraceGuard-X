test:
	pytest -q

baseline:
	python -m baseline.baseline --data data/traces --output artifacts/baseline_results.json

advanced:
	python -m src.traceguard.pipeline --data data/traces --output artifacts/advanced_results.json

validate:
	python evaluation/benchmark_validate.py

compare:
	python evaluation/compare.py --baseline artifacts/baseline_results.json --advanced artifacts/advanced_results.json

scorecard:
	python evaluation/scorecard.py
