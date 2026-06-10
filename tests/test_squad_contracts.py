"""Tests for official squad contracts."""

import pytest
import pandas as pd

from src.official.squad_contracts import get_squad_contract, check_squad_required_columns


class TestSquadContracts:
    """Test squad data contracts."""
    
    def test_get_squad_contract_official_players(self):
        """Test retrieving official_players contract."""
        cols = get_squad_contract("official_players")
        assert isinstance(cols, list)
        assert len(cols) > 0
        assert "player_id" in cols
        assert "player_name" in cols
        assert "team" in cols
    
    def test_get_squad_contract_official_award_candidates(self):
        """Test retrieving official_award_candidates contract."""
        cols = get_squad_contract("official_award_candidates")
        assert isinstance(cols, list)
        assert len(cols) > 0
        assert "player_id" in cols
        assert "base_player_rating" in cols
    
    def test_get_squad_contract_player_priors(self):
        """Test retrieving player_priors contract."""
        cols = get_squad_contract("player_priors")
        assert isinstance(cols, list)
        assert "player" in cols
        assert "team" in cols
        assert "base_player_rating" in cols
    
    def test_get_squad_contract_unknown(self):
        """Test unknown contract raises ValueError."""
        with pytest.raises(ValueError):
            get_squad_contract("unknown_contract")
    
    def test_check_squad_required_columns_all_present(self):
        """Test checking columns when all present."""
        df = pd.DataFrame({
            "player_id": ["p1", "p2"],
            "player_name": ["Alice", "Bob"],
            "team": ["Team A", "Team B"],
        })
        required = ["player_id", "player_name", "team"]
        passed, missing = check_squad_required_columns(df, required)
        
        assert passed is True
        assert len(missing) == 0
    
    def test_check_squad_required_columns_missing(self):
        """Test checking columns when some missing."""
        df = pd.DataFrame({
            "player_id": ["p1", "p2"],
            "player_name": ["Alice", "Bob"],
        })
        required = ["player_id", "player_name", "team"]
        passed, missing = check_squad_required_columns(df, required)
        
        assert passed is False
        assert "team" in missing
    
    def test_check_squad_required_columns_extra_columns(self):
        """Test checking columns with extra columns in df."""
        df = pd.DataFrame({
            "player_id": ["p1", "p2"],
            "player_name": ["Alice", "Bob"],
            "team": ["Team A", "Team B"],
            "extra_col": [1, 2],
        })
        required = ["player_id", "player_name", "team"]
        passed, missing = check_squad_required_columns(df, required)
        
        assert passed is True
        assert len(missing) == 0
