"""Tests for official squad parser."""

import pytest
import pandas as pd
from datetime import datetime

from src.official.squad_parser import (
    normalize_position_code,
    calculate_age_at_tournament_start,
    create_official_players_template_from_sample,
)


class TestSquadParser:
    """Test squad parsing and normalization."""
    
    def test_normalize_position_code_from_code(self):
        """Test normalizing position from code."""
        code, pos = normalize_position_code("GK")
        assert code == "GK"
        assert pos == "goalkeeper"
        
        code, pos = normalize_position_code("DF")
        assert code == "DF"
        assert pos == "defender"
        
        code, pos = normalize_position_code("MF")
        assert code == "MF"
        assert pos == "midfielder"
        
        code, pos = normalize_position_code("FW")
        assert code == "FW"
        assert pos == "forward"
    
    def test_normalize_position_code_from_name(self):
        """Test normalizing position from full name."""
        code, pos = normalize_position_code("goalkeeper")
        assert code == "GK"
        assert pos == "goalkeeper"
        
        code, pos = normalize_position_code("forward")
        assert code == "FW"
        assert pos == "forward"
    
    def test_normalize_position_code_case_insensitive(self):
        """Test position normalization is case-insensitive."""
        code, pos = normalize_position_code("gk")
        assert code == "GK"
        
        code, pos = normalize_position_code("GOALKEEPER")
        assert code == "GK"
    
    def test_normalize_position_code_invalid(self):
        """Test invalid position raises ValueError."""
        with pytest.raises(ValueError):
            normalize_position_code("invalid_position")
    
    def test_calculate_age_at_tournament_start(self):
        """Test age calculation."""
        age = calculate_age_at_tournament_start("2000-06-12", "2026-06-11")
        assert age == 25
        
        age = calculate_age_at_tournament_start("1995-01-01", "2026-06-11")
        assert age == 31
    
    def test_calculate_age_at_tournament_start_invalid_date(self):
        """Test invalid date returns None."""
        age = calculate_age_at_tournament_start("invalid-date", "2026-06-11")
        assert age is None
    
    def test_calculate_age_at_tournament_start_default_date(self):
        """Test default tournament date."""
        age = calculate_age_at_tournament_start("2000-06-12")
        assert age == 25
    
    def test_create_official_players_template_from_sample(self):
        """Test creating official players template from sample."""
        sample_df = pd.DataFrame({
            "player": ["Alice", "Bob"],
            "team": ["France", "England"],
            "position": ["forward", "goalkeeper"],
            "club": ["PSG", "Man City"],
            "date_of_birth": ["1998-12-20", "1995-07-03"],
        })
        
        template = create_official_players_template_from_sample(sample_df)
        
        assert len(template) == 2
        assert "player_id" in template.columns
        assert "position_code" in template.columns
        assert "source" in template.columns
        
        # Check source is marked as template
        assert all(template["source"] == "sample_to_be_verified")
        
        # Check position normalization
        assert template.iloc[0]["position_code"] == "FW"
        assert template.iloc[1]["position_code"] == "GK"
