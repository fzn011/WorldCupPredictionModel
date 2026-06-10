"""Tests for official player registry operations."""

import pytest
import pandas as pd

from src.official.player_registry import (
    build_official_squads_summary,
    build_team_player_map,
    merge_player_priors_with_official_players,
)


class TestPlayerRegistry:
    """Test player registry operations."""
    
    @pytest.fixture
    def sample_players(self):
        """Create sample official players."""
        return pd.DataFrame({
            "player_id": ["p1", "p2", "p3", "p4", "p5", "p6"],
            "player_name": ["Alice", "Bob", "Charlie", "David", "Eve", "Frank"],
            "team": ["France", "France", "France", "England", "England", "England"],
            "team_code": ["FRA", "FRA", "FRA", "ENG", "ENG", "ENG"],
            "position_code": ["GK", "DF", "MF", "GK", "DF", "FW"],
            "position": ["goalkeeper", "defender", "midfielder", "goalkeeper", "defender", "forward"],
            "shirt_number": [1, 2, 3, 1, 2, 9],
            "club": ["PSG", "Monaco", "Lyon", "Man City", "Liverpool", "Arsenal"],
            "height_cm": [190, 185, 180, 195, 183, 178],
            "date_of_birth": ["2000-01-01", "1995-01-01", "1998-01-01", "1996-01-01", "1997-01-01", "1999-01-01"],
            "age_at_tournament_start": [26, 31, 28, 30, 29, 27],
            "source": ["official", "official", "official", "official", "official", "official"],
            "last_verified_at": ["2026-01-01"] * 6,
        })
    
    @pytest.fixture
    def sample_priors(self):
        """Create sample player priors."""
        return pd.DataFrame({
            "player": ["Alice", "Bob"],
            "team": ["France", "France"],
            "base_player_rating": [85, 80],
            "expected_minutes_share": [0.9, 0.8],
            "goals_prior": [0, 5],
            "assists_prior": [0, 2],
            "chance_creation_prior": [1, 8],
            "defensive_actions_prior": [3, 10],
            "goalkeeper_actions_prior": [45, 0],
            "discipline_risk": [0.1, 0.2],
            "star_role_score": [8, 7],
            "flair_score": [6, 5],
            "notes": ["Editable prior"] * 2,
        })
    
    def test_build_official_squads_summary(self, sample_players):
        """Test building squad summary."""
        summary = build_official_squads_summary(sample_players)
        
        assert len(summary) == 2
        assert "France" in summary["team"].values
        assert "England" in summary["team"].values
        
        france = summary[summary["team"] == "France"].iloc[0]
        assert france["player_count"] == 3
        assert france["goalkeepers"] == 1
        assert france["defenders"] == 1
        assert france["midfielders"] == 1
        assert france["forwards"] == 0
    
    def test_build_team_player_map(self, sample_players):
        """Test building team-player map."""
        team_map = build_team_player_map(sample_players)
        
        assert len(team_map) == 6
        assert all(col in team_map.columns for col in ["team", "player_id", "player_name", "position_code"])
        
        france_map = team_map[team_map["team"] == "France"]
        assert len(france_map) == 3
    
    def test_merge_player_priors_with_official_players(self, sample_players, sample_priors):
        """Test merging priors with official players."""
        candidates, unmatched = merge_player_priors_with_official_players(sample_players, sample_priors)
        
        # Should have same number of players as official
        assert len(candidates) == len(sample_players)
        
        # Should have all official player IDs
        assert set(candidates["player_id"]) == set(sample_players["player_id"])
        
        # Check has_player_prior flag
        alice_candidates = candidates[candidates["player_name"] == "Alice"]
        assert len(alice_candidates) == 1
        assert alice_candidates.iloc[0]["has_player_prior"] == True
        
        # Check default for non-prior player
        eve_candidates = candidates[candidates["player_name"] == "Eve"]
        assert len(eve_candidates) == 1
        assert eve_candidates.iloc[0]["has_player_prior"] == False
        assert eve_candidates.iloc[0]["base_player_rating"] == 50  # conservative default
    
    def test_merge_detects_unmatched_priors(self, sample_players, sample_priors):
        """Test unmatched priors are reported."""
        # Add a prior for non-existent player
        extra_prior = pd.DataFrame({
            "player": ["NonExistent"],
            "team": ["Germany"],
            "base_player_rating": [75],
            "expected_minutes_share": [0.5],
            "goals_prior": [0],
            "assists_prior": [0],
            "chance_creation_prior": [0],
            "defensive_actions_prior": [0],
            "goalkeeper_actions_prior": [0],
            "discipline_risk": [0.5],
            "star_role_score": [0],
            "flair_score": [0],
            "notes": [""],
        })
        priors_with_extra = pd.concat([sample_priors, extra_prior], ignore_index=True)
        
        candidates, unmatched = merge_player_priors_with_official_players(sample_players, priors_with_extra)
        
        assert len(unmatched) == 1
        assert unmatched.iloc[0]["player"] == "NonExistent"
