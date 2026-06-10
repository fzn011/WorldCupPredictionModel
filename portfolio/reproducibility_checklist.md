# Reproducibility Checklist

- [ ] Clone repo and create venv
- [ ] `pip install -r requirements.txt`
- [ ] `python main.py` (or use committed model artifacts if available)
- [ ] Verify official data applied: `python scripts/evaluate_official_final_readiness.py`
- [ ] Confirm `official_final_enabled=true` if awards required
- [ ] `python scripts/run_monte_carlo.py --simulations 10 --seed 42`
- [ ] `python scripts/enrich_player_priors.py --update-award-candidates`
- [ ] `python scripts/generate_world_cup_awards.py --use-enriched`
- [ ] `python scripts/prepare_final_project_pack.py`
- [ ] `python -m pytest -q`
- [ ] `python -m streamlit run app/streamlit_app.py`
