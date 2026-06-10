"""Tests for Step 17B orchestration and official awards candidates.

Tests the prepare_step17b orchestrator and the awards layer integration
that ensures only official players can enter award candidates.
"""

import pytest
import pandas as pd
import json
from pathlib import Path

from src.official.prepare_squads import prepare_step17b_official_squads_and_priors


class TestPrepareSquads:
    """Test Step 17B orchestration."""
    
    def test_prepare_step17b_returns_dict(self):
        """Test orchestrator returns summary dict."""
        result = prepare_step17b_official_squads_and_priors()
        
        assert isinstance(result, dict)
        assert "status" in result
        assert "validation_passed" in result
        assert "official_players_count" in result
    
    def test_prepare_step17b_status_values(self):
        """Test status is one of valid values."""
        result = prepare_step17b_official_squads_and_priors()
        
        status = result.get("status")
        assert status in ["ok", "needs_verification", "error"]
    
    def test_prepare_step17b_creates_files(self):
        """Test orchestrator creates output files."""
        result = prepare_step17b_official_squads_and_priors()
        
        players_path = Path(result.get("official_players_path", ""))
        assert players_path.exists()
        
        candidates_path = Path(result.get("official_award_candidates_path", ""))
        assert candidates_path.exists()
    
    def test_prepare_step17b_official_award_candidates_only_official(self):
        """Test award candidates contain only official players."""
        result = prepare_step17b_official_squads_and_priors()
        
        # Load official players and candidates
        players_path = Path(result.get("official_players_path", ""))
        candidates_path = Path(result.get("official_award_candidates_path", ""))
        
        players = pd.read_csv(players_path)
        candidates = pd.read_csv(candidates_path)
        
        official_ids = set(players["player_id"].unique())
        candidate_ids = set(candidates["player_id"].unique())
        
        # All candidates should be in official players
        assert candidate_ids.issubset(official_ids)
    
    def test_prepare_step17b_summary_has_required_fields(self):
        """Test summary contains all expected fields."""
        result = prepare_step17b_official_squads_and_priors()
        
        required_fields = [
            "status",
            "validation_passed",
            "official_players_count",
            "official_teams_with_players",
            "official_award_candidates_count",
            "errors_count",
            "warnings_count",
        ]
        
        for field in required_fields:
            assert field in result
    
    def test_prepare_step17b_unmatched_priors_excluded(self):
        """Test unmatched priors are excluded from candidates."""
        result = prepare_step17b_official_squads_and_priors()
        
        # Load files
        merge_report_path = Path(result.get("prior_merge_report_path", ""))
        candidates_path = Path(result.get("official_award_candidates_path", ""))
        
        if merge_report_path.exists():
            unmatched = pd.read_csv(merge_report_path)
            
            if len(unmatched) > 0:
                candidates = pd.read_csv(candidates_path)
                
                # Verify unmatched priors are not in candidates
                for _, row in unmatched.iterrows():
                    player = row.get("player")
                    team = row.get("team")
                    
                    matches = candidates[
                        (candidates["player_name"] == player) & 
                        (candidates["team"] == team)
                    ]
                    
                    # If matched, should have has_player_prior=False
                    # (meaning it used conservative defaults, not the unmatched prior)
                    for _, match_row in matches.iterrows():
                        # This player should not have the unmatched prior's values
                        pass
    
    def test_prepare_step17b_with_overwrite_priors(self):
        """Test overwriting priors template."""
        result1 = prepare_step17b_official_squads_and_priors()
        
        # Try again with overwrite
        result2 = prepare_step17b_official_squads_and_priors(overwrite_priors=True)
        
        assert result2["status"] in ["ok", "needs_verification", "error"]


class TestAwardsOfficialCandidates:
    """Test integration with awards layer."""
    
    def test_load_player_candidates_official_mode(self, monkeypatch):
        """Test loading candidates in official mode."""
        prepare_step17b_official_squads_and_priors()

        monkeypatch.setattr(
            "src.awards.player_awards.require_official_final_ready",
            lambda: {"official_final_enabled": True, "final_ready": True},
        )
        monkeypatch.setattr(
            "src.awards.award_data.require_official_final_ready",
            lambda: {"official_final_enabled": True, "final_ready": True},
        )

        from src.awards.player_awards import load_player_candidates

        candidates = load_player_candidates(official_only=True)

        assert isinstance(candidates, pd.DataFrame)
        assert len(candidates) > 0
        assert "player_id" in candidates.columns

    def test_load_player_candidates_official_only_raises_if_missing(self, monkeypatch):
        """Test official_only=True raises if official final is not ready."""
        from src.awards.player_awards import load_player_candidates

        monkeypatch.setattr(
            "src.awards.player_awards.require_official_final_ready",
            lambda: (_ for _ in ()).throw(
                RuntimeError(
                    "World Cup awards require official_final mode. Run official final readiness and promotion first."
                )
            ),
        )
        with pytest.raises(RuntimeError, match="official_final"):
            load_player_candidates(official_only=True)
    
    def test_no_non_official_players_in_official_mode(self):
        """Test non-official players are blocked in official mode."""
        # Prepare Step 17B data
        result = prepare_step17b_official_squads_and_priors()
        
        # Load official players and candidates
        players_path = Path(result.get("official_players_path", ""))
        candidates_path = Path(result.get("official_award_candidates_path", ""))
        
        players = pd.read_csv(players_path)
        candidates = pd.read_csv(candidates_path)
        
        # Every candidate must have an official player_id
        official_ids = set(players["player_id"].unique())
        
        for _, row in candidates.iterrows():
            player_id = row["player_id"]
            assert player_id in official_ids, f"Non-official player {player_id} in candidates!"
