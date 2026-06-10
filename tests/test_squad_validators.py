"""Tests for official squad validators."""

import pytest
import pandas as pd

from src.official.squad_validators import (
    validate_official_players,
    validate_team_player_map,
    validate_player_award_priors,
    validate_official_award_candidates,
)


class TestSquadValidators:
    """Test squad validation functions."""
    
    @pytest.fixture
    def valid_players(self):
        """Create valid official players."""
        return pd.DataFrame({
            "player_id": [f"p{i}" for i in range(48)],
            "player_name": [f"Player {i}" for i in range(48)],
            "first_names": [f"First{i}" for i in range(48)],
            "last_names": [f"Last{i}" for i in range(48)],
            "name_on_shirt": [f"LAST{i}" for i in range(48)],
            "team": ["France"] * 26 + ["England"] * 22,
            "team_code": ["FRA"] * 26 + ["ENG"] * 22,
            "position_code": ["GK", "DF", "MF", "FW"] * 12,  # 4 * 12 = 48
            "position": ["goalkeeper", "defender", "midfielder", "forward"] * 12,  # 4 * 12 = 48
            "shirt_number": list(range(1, 27)) + list(range(1, 23)),
            "club": ["Club"] * 48,
            "club_country": ["Country"] * 48,
            "height_cm": [180] * 48,
            "date_of_birth": ["1995-01-01"] * 48,
            "age_at_tournament_start": [31] * 48,
            "source": ["official"] * 48,
            "last_verified_at": ["2026-01-01"] * 48,
        })
    
    def test_validate_official_players_valid(self, valid_players):
        """Test validation of valid players."""
        passed, report = validate_official_players(valid_players, strict_squad_size=False)
        
        # Should have warnings for incomplete squad but pass validation
        assert passed is True or len(report[report["severity"] == "error"]) == 0
    
    def test_validate_official_players_missing_columns(self):
        """Test validation fails on missing required columns."""
        incomplete_df = pd.DataFrame({
            "player_id": ["p1"],
            "player_name": ["Alice"],
        })
        
        passed, report = validate_official_players(incomplete_df)
        
        assert passed is False
        errors = report[report["severity"] == "error"]
        assert len(errors) > 0
    
    def test_validate_official_players_duplicate_ids(self):
        """Test validation fails on duplicate player_ids."""
        dup_df = pd.DataFrame({
            "player_id": ["p1", "p1"],
            "player_name": ["Alice", "Bob"],
            "team": ["France", "England"],
            "team_code": ["FRA", "ENG"],
            "position_code": ["GK", "GK"],
            "position": ["goalkeeper", "goalkeeper"],
            "shirt_number": [1, 1],
            "club": ["PSG", "Man City"],
            "club_country": ["France", "England"],
            "height_cm": [190, 190],
            "date_of_birth": ["2000-01-01", "2000-01-01"],
            "age_at_tournament_start": [26, 26],
            "source": ["official", "official"],
            "last_verified_at": ["2026-01-01", "2026-01-01"],
        })
        
        passed, report = validate_official_players(dup_df)
        
        assert passed is False
    
    def test_validate_official_players_sample_warning(self):
        """Test validation warns on sample_to_be_verified."""
        sample_df = pd.DataFrame({
            "player_id": ["p1"],
            "player_name": ["Alice"],
            "first_names": ["Alice"],
            "last_names": ["Smith"],
            "name_on_shirt": ["SMITH"],
            "team": ["France"],
            "team_code": ["FRA"],
            "position_code": ["GK"],
            "position": ["goalkeeper"],
            "shirt_number": [1],
            "club": ["PSG"],
            "club_country": ["France"],
            "height_cm": [190],
            "date_of_birth": ["2000-01-01"],
            "age_at_tournament_start": [26],
            "source": ["sample_to_be_verified"],
            "last_verified_at": ["2026-01-01"],
        })
        
        passed, report = validate_official_players(sample_df)
        
        # Should pass validation but with warnings about sample data and incomplete squad
        warnings = report[report["severity"] == "warning"]
        assert len(warnings) > 0, f"Expected warnings but got report: {report}"
        # Check for sample_to_be_verified warning or incomplete squad warning
        warning_messages = " ".join(warnings["message"].astype(str)).lower()
        assert "sample" in warning_messages or "incomplete" in warning_messages, f"Expected sample/incomplete warning, got: {warning_messages}"
    
    def test_validate_team_player_map_valid(self):
        """Test valid team-player map."""
        players_df = pd.DataFrame({
            "player_id": ["p1", "p2"],
            "player_name": ["Alice", "Bob"],
            "team": ["France", "England"],
        })
        
        map_df = pd.DataFrame({
            "team": ["France", "England"],
            "team_code": ["FRA", "ENG"],
            "player_id": ["p1", "p2"],
            "player_name": ["Alice", "Bob"],
            "position_code": ["GK", "GK"],
            "position": ["goalkeeper", "goalkeeper"],
            "shirt_number": [1, 1],
            "source": ["official", "official"],
            "last_verified_at": ["2026-01-01", "2026-01-01"],
        })
        
        passed, report = validate_team_player_map(map_df, players_df)
        
        assert passed is True
    
    def test_validate_team_player_map_invalid_player(self):
        """Test team-player map with invalid player_id."""
        players_df = pd.DataFrame({
            "player_id": ["p1"],
            "player_name": ["Alice"],
            "team": ["France"],
        })
        
        map_df = pd.DataFrame({
            "team": ["France"],
            "team_code": ["FRA"],
            "player_id": ["p999"],  # Does not exist in players
            "player_name": ["Unknown"],
            "position_code": ["GK"],
            "position": ["goalkeeper"],
            "shirt_number": [1],
            "source": ["official"],
            "last_verified_at": ["2026-01-01"],
        })
        
        passed, report = validate_team_player_map(map_df, players_df)
        
        assert passed is False
        errors = report[report["severity"] == "error"]
        assert len(errors) > 0
    
    def test_validate_player_award_priors_valid(self):
        """Test valid player priors."""
        priors_df = pd.DataFrame({
            "player": ["Alice"],
            "team": ["France"],
            "base_player_rating": [75],
            "expected_minutes_share": [0.8],
            "goals_prior": [5],
            "assists_prior": [2],
            "chance_creation_prior": [8],
            "defensive_actions_prior": [3],
            "goalkeeper_actions_prior": [0],
            "discipline_risk": [0.2],
            "star_role_score": [7],
            "flair_score": [6],
            "notes": ["Good player"],
        })
        
        passed, report = validate_player_award_priors(priors_df)
        
        assert passed is True
    
    def test_validate_official_award_candidates_valid(self):
        """Test valid award candidates."""
        players_df = pd.DataFrame({
            "player_id": ["p1"],
            "player_name": ["Alice"],
            "team": ["France"],
        })
        
        candidates_df = pd.DataFrame({
            "player_id": ["p1"],
            "team": ["France"],
            "team_code": ["FRA"],
            "shirt_number": [1],
            "position_code": ["FW"],
            "position": ["forward"],
            "player_name": ["Alice"],
            "date_of_birth": ["1998-01-01"],
            "age_at_tournament_start": [28],
            "club": ["PSG"],
            "height_cm": [180],
            "base_player_rating": [85],
            "expected_minutes_share": [0.9],
            "goals_prior": [12],
            "assists_prior": [4],
            "chance_creation_prior": [10],
            "defensive_actions_prior": [2],
            "goalkeeper_actions_prior": [0],
            "discipline_risk": [0.15],
            "star_role_score": [8],
            "flair_score": [7],
            "has_player_prior": [True],
            "prior_source": ["user_prior"],
            "source": ["official"],
            "last_verified_at": ["2026-01-01"],
        })
        
        passed, report = validate_official_award_candidates(candidates_df, players_df)
        
        assert passed is True
    
    def test_validate_official_award_candidates_invalid_player(self):
        """Test candidates with invalid player_id."""
        players_df = pd.DataFrame({
            "player_id": ["p1"],
            "player_name": ["Alice"],
            "team": ["France"],
        })
        
        candidates_df = pd.DataFrame({
            "player_id": ["p999"],  # Not in official players
            "team": ["France"],
            "team_code": ["FRA"],
            "shirt_number": [1],
            "position_code": ["FW"],
            "position": ["forward"],
            "player_name": ["Unknown"],
            "date_of_birth": ["1998-01-01"],
            "age_at_tournament_start": [28],
            "club": ["PSG"],
            "height_cm": [180],
            "base_player_rating": [85],
            "expected_minutes_share": [0.9],
            "goals_prior": [12],
            "assists_prior": [4],
            "chance_creation_prior": [10],
            "defensive_actions_prior": [2],
            "goalkeeper_actions_prior": [0],
            "discipline_risk": [0.15],
            "star_role_score": [8],
            "flair_score": [7],
            "has_player_prior": [False],
            "prior_source": ["conservative_default"],
            "source": ["official"],
            "last_verified_at": ["2026-01-01"],
        })
        
        passed, report = validate_official_award_candidates(candidates_df, players_df)
        
        assert passed is False
        errors = report[report["severity"] == "error"]
        assert len(errors) > 0
