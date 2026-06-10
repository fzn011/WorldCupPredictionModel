"""Tests for Step 17C: Official Final Readiness, Import Templates, and Apply Imports."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pandas as pd
import pytest

import src.utils.constants as C
from src.official.final_readiness import (
    evaluate_official_final_readiness,
    save_final_readiness_report,
    is_official_final_mode_allowed,
)
from src.official.import_templates import (
    generate_teams_import_template,
    generate_groups_import_template,
    generate_fixtures_import_template,
    generate_venues_import_template,
    generate_players_import_template,
    generate_squads_import_template,
    generate_all_import_templates,
    create_import_manifest,
    validate_import_file,
)
from src.official.apply_imports import (
    apply_teams_import,
    apply_official_import_file,
    _add_metadata_columns,
)


# ===== FIXTURES =====

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_teams_df():
    """Create a sample teams DataFrame."""
    return pd.DataFrame({
        "team": ["Brazil", "Argentina", "France", "Germany"],
        "team_code": ["BRA", "ARG", "FRA", "GER"],
        "confederation": ["CONMEBOL", "CONMEBOL", "UEFA", "UEFA"],
        "group": ["A", "A", "B", "B"],
        "group_slot": [1, 2, 1, 2],
        "is_host": [False, False, False, False],
        "qualified": [True, True, True, True],
        "source": ["fifa_official"] * 4,
    })


@pytest.fixture
def complete_teams_df():
    """Create a complete 48-team DataFrame."""
    teams = []
    for i in range(48):
        group = chr(65 + (i // 4))  # A-L
        teams.append({
            "team": f"Team_{i+1}",
            "team_code": f"TM{i+1:02d}",
            "confederation": "UEFA" if i < 24 else "CONMEBOL",
            "group": group,
            "group_slot": (i % 4) + 1,
            "is_host": i < 3,  # First 3 are hosts
            "qualified": True,
            "source": "fifa_official",
        })
    return pd.DataFrame(teams)


@pytest.fixture
def complete_players_df():
    """Create a complete 1248-player DataFrame."""
    players = []
    for team_i in range(48):
        team_name = f"Team_{team_i+1}"
        team_code = f"TM{team_i+1:02d}"
        group = chr(65 + (team_i // 4))
        for player_i in range(26):
            players.append({
                "player_id": f"p_{team_i+1:02d}_{player_i+1:02d}",
                "team": team_name,
                "team_code": team_code,
                "shirt_number": player_i + 1,
                "position_code": ["GK", "DF", "MF", "FW"][player_i % 4],
                "position": ["goalkeeper", "defender", "midfielder", "forward"][player_i % 4],
                "player_name": f"{team_name} Player {player_i+1}",
                "first_names": f"First{player_i+1}",
                "last_names": f"Last{player_i+1}",
                "name_on_shirt": f"P{player_i+1}",
                "date_of_birth": "1995-01-01",
                "age_at_tournament_start": 31,
                "club": f"Club {player_i+1}",
                "club_country": "England",
                "height_cm": 180,
                "source": "fifa_official",
            })
    return pd.DataFrame(players)


# ===== FINAL READINESS TESTS =====

class TestEvaluateOfficialFinalReadiness:
    """Tests for evaluate_official_final_readiness()."""

    def test_returns_valid_structure(self, temp_dir):
        """Test that the function returns a valid report structure."""
        report = evaluate_official_final_readiness(temp_dir)

        assert "status" in report
        assert "checklist" in report
        assert "blockers" in report
        assert "warnings" in report
        assert "summary" in report
        assert "timestamp" in report
        assert "is_official_final_ready" in report

    def test_status_is_valid(self, temp_dir):
        """Test that status is one of the valid values."""
        report = evaluate_official_final_readiness(temp_dir)
        assert report["status"] in [
            C.OFFICIAL_READINESS_BLOCKED,
            C.OFFICIAL_READINESS_WARNING,
            C.OFFICIAL_READINESS_READY,
        ]

    def test_blocked_when_no_data(self, temp_dir):
        """Test that status is blocked when no data files exist."""
        report = evaluate_official_final_readiness(temp_dir)
        assert report["status"] == C.OFFICIAL_READINESS_BLOCKED
        assert not report["is_official_final_ready"]

    def test_checklist_has_all_items(self, temp_dir):
        """Test that checklist contains all expected checks."""
        report = evaluate_official_final_readiness(temp_dir)
        check_ids = [c["id"] for c in report["checklist"]]

        expected_ids = [
            "teams_complete", "teams_no_placeholders",
            "groups_complete", "groups_no_placeholders",
            "venues_complete", "venues_no_placeholders",
            "fixtures_complete", "fixtures_no_placeholders",
            "squads_complete", "players_complete", "players_no_placeholders",
            "award_candidates_ready", "player_priors_merged",
            "no_sample_rows", "data_consistency",
        ]
        for eid in expected_ids:
            assert eid in check_ids, f"Missing check: {eid}"

    def test_summary_has_required_fields(self, temp_dir):
        """Test that summary contains required fields."""
        report = evaluate_official_final_readiness(temp_dir)
        summary = report["summary"]

        required_fields = [
            "total_checks", "passed_checks", "failed_checks",
            "blocker_count", "warning_count",
            "teams_count", "players_count", "teams_with_26_players",
        ]
        for field in required_fields:
            assert field in summary, f"Missing summary field: {field}"


class TestIsOfficialFinalModeAllowed:
    """Tests for is_official_final_mode_allowed()."""

    def test_returns_tuple(self, temp_dir):
        """Test that function returns a tuple."""
        result = is_official_final_mode_allowed(temp_dir)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert isinstance(result[0], bool)
        assert isinstance(result[1], list)

    def test_blocked_when_no_data(self, temp_dir):
        """Test that mode is not allowed when no data."""
        allowed, blockers = is_official_final_mode_allowed(temp_dir)
        assert not allowed
        assert len(blockers) > 0


class TestSaveFinalReadinessReport:
    """Tests for save_final_readiness_report()."""

    def test_saves_json_report(self, temp_dir, sample_teams_df):
        """Test that JSON report is saved."""
        report = {
            "status": C.OFFICIAL_READINESS_BLOCKED,
            "checklist": [],
            "blockers": [],
            "warnings": [],
            "summary": {"total_checks": 0},
            "timestamp": "2026-01-01T00:00:00Z",
            "is_official_final_ready": False,
        }

        report_path = save_final_readiness_report(report, temp_dir)
        assert report_path.exists()
        assert report_path.name == C.OFFICIAL_FINAL_READINESS_REPORT_FILE

    def test_saves_csv_checklist(self, temp_dir):
        """Test that CSV checklist is saved."""
        report = {
            "status": C.OFFICIAL_READINESS_READY,
            "checklist": [
                {"id": "test_check", "passed": True, "details": {}},
            ],
            "blockers": [],
            "warnings": [],
            "summary": {"total_checks": 1},
            "timestamp": "2026-01-01T00:00:00Z",
            "is_official_final_ready": True,
        }

        report_path = save_final_readiness_report(report, temp_dir)
        checklist_path = temp_dir / C.OFFICIAL_FINAL_READINESS_CHECKLIST_FILE
        assert checklist_path.exists()


# ===== IMPORT TEMPLATES TESTS =====

class TestGenerateImportTemplates:
    """Tests for import template generation."""

    def test_generate_teams_template(self, temp_dir):
        """Test teams template generation."""
        path = generate_teams_import_template(temp_dir)
        assert path.exists()
        assert path.name == C.OFFICIAL_IMPORT_TEAMS_TEMPLATE_FILE

        df = pd.read_csv(path)
        assert len(df) == C.OFFICIAL_REQUIRED_TEAM_COUNT
        for col in C.IMPORT_TEAMS_REQUIRED_COLUMNS:
            assert col in df.columns

    def test_generate_groups_template(self, temp_dir):
        """Test groups template generation."""
        path = generate_groups_import_template(temp_dir)
        assert path.exists()
        assert path.name == C.OFFICIAL_IMPORT_GROUPS_TEMPLATE_FILE

        df = pd.read_csv(path)
        assert len(df) == C.OFFICIAL_REQUIRED_TEAM_COUNT

    def test_generate_fixtures_template(self, temp_dir):
        """Test fixtures template generation."""
        path = generate_fixtures_import_template(temp_dir)
        assert path.exists()
        assert path.name == C.OFFICIAL_IMPORT_FIXTURES_TEMPLATE_FILE

        df = pd.read_csv(path)
        assert len(df) == C.OFFICIAL_TOTAL_MATCHES

    def test_generate_venues_template(self, temp_dir):
        """Test venues template generation."""
        path = generate_venues_import_template(temp_dir)
        assert path.exists()
        assert path.name == C.OFFICIAL_IMPORT_VENUES_TEMPLATE_FILE

        df = pd.read_csv(path)
        assert len(df) == 16

    def test_generate_players_template(self, temp_dir):
        """Test players template generation."""
        path = generate_players_import_template(temp_dir)
        assert path.exists()
        assert path.name == C.OFFICIAL_IMPORT_PLAYERS_TEMPLATE_FILE

        df = pd.read_csv(path)
        assert len(df) == C.OFFICIAL_REQUIRED_TOTAL_PLAYERS

    def test_generate_squads_template(self, temp_dir):
        """Test squads template generation."""
        path = generate_squads_import_template(temp_dir)
        assert path.exists()
        assert path.name == C.OFFICIAL_IMPORT_SQUADS_TEMPLATE_FILE

        df = pd.read_csv(path)
        assert len(df) == C.OFFICIAL_REQUIRED_TEAM_COUNT

    def test_generate_all_templates(self, temp_dir):
        """Test generating all templates at once."""
        templates = generate_all_import_templates(temp_dir)

        assert len(templates) == 6
        for name in ["teams", "groups", "fixtures", "venues", "players", "squads"]:
            assert name in templates
            assert templates[name].exists()

    def test_generate_all_with_existing_data(self, temp_dir, sample_teams_df):
        """Test generating templates with existing data."""
        # Save sample data
        sample_teams_df.to_csv(temp_dir / C.OFFICIAL_TEAMS_FILE, index=False)

        templates = generate_all_import_templates(temp_dir, include_existing_data=True)

        # Check that teams template was pre-populated
        teams_template = pd.read_csv(templates["teams"])
        assert len(teams_template) == len(sample_teams_df)


class TestValidateImportFile:
    """Tests for import file validation."""

    def test_valid_teams_file(self, temp_dir):
        """Test validation of a valid teams file."""
        template_path = generate_teams_import_template(temp_dir)
        is_valid, errors = validate_import_file(template_path, "teams")
        assert is_valid
        assert len(errors) == 0

    def test_unknown_type(self, temp_dir):
        """Test validation with unknown type."""
        path = temp_dir / "test.csv"
        path.touch()
        is_valid, errors = validate_import_file(path, "unknown_type")
        assert not is_valid
        assert any("Unknown template type" in e for e in errors)

    def test_file_not_found(self, temp_dir):
        """Test validation with non-existent file."""
        path = temp_dir / "nonexistent.csv"
        is_valid, errors = validate_import_file(path, "teams")
        assert not is_valid
        assert any("File not found" in e for e in errors)

    def test_missing_columns(self, temp_dir):
        """Test validation with missing columns."""
        df = pd.DataFrame({"team": ["Brazil"]})  # Missing required columns
        path = temp_dir / "incomplete.csv"
        df.to_csv(path, index=False)

        is_valid, errors = validate_import_file(path, "teams")
        assert not is_valid
        assert any("Missing required columns" in e for e in errors)


class TestCreateImportManifest:
    """Tests for import manifest creation."""

    def test_creates_manifest(self, temp_dir):
        """Test that manifest is created."""
        templates = generate_all_import_templates(temp_dir)
        manifest_path = create_import_manifest(templates, temp_dir)

        assert manifest_path.exists()
        assert manifest_path.name == "import_manifest.json"

        with open(manifest_path) as f:
            manifest = json.load(f)

        assert "generated_at" in manifest
        assert "templates" in manifest
        assert "instructions" in manifest
        assert "required_columns" in manifest


# ===== APPLY IMPORTS TESTS =====

class TestApplyImports:
    """Tests for applying import files."""

    def test_add_metadata_columns(self):
        """Test adding metadata columns to DataFrame."""
        df = pd.DataFrame({"team": ["Brazil"]})
        result = _add_metadata_columns(df)

        assert "source" in result.columns
        assert "last_verified_at" in result.columns
        assert result["source"].iloc[0] == "manual_import"

    def test_apply_teams_import(self, temp_dir):
        """Test applying a teams import file."""
        # Create a valid import file
        template_path = generate_teams_import_template(temp_dir)

        # Fill in some data
        df = pd.read_csv(template_path)
        df["team"] = [f"Team_{i+1}" for i in range(len(df))]
        df["team_code"] = [f"TM{i+1:02d}" for i in range(len(df))]
        df.to_csv(template_path, index=False)

        result = apply_teams_import(template_path, temp_dir, create_backup=False)

        assert result["success"]
        assert result["rows_imported"] == C.OFFICIAL_REQUIRED_TEAM_COUNT

        # Verify the file was created
        output_path = temp_dir / C.OFFICIAL_TEAMS_FILE
        assert output_path.exists()

    def test_apply_import_auto_detect_type(self, temp_dir):
        """Test auto-detection of import type from filename."""
        template_path = generate_teams_import_template(temp_dir)
        # Rename to match expected pattern
        new_path = temp_dir / "import_teams_template.csv"
        template_path.rename(new_path)

        result = apply_official_import_file(new_path, create_backup=False, re_prepare=False)

        assert result["success"]
        assert result["type"] == "teams"


# ===== INTEGRATION TESTS =====

class TestIntegration:
    """Integration tests for the full workflow."""

    def test_full_import_workflow(self, temp_dir):
        """Test the full import workflow: generate -> fill -> apply -> evaluate."""
        # Step 1: Generate templates
        templates = generate_all_import_templates(temp_dir)

        # Step 2: Fill teams template with complete data
        teams_df = pd.DataFrame({
            col: [f"{col}_{i+1}" for i in range(C.OFFICIAL_REQUIRED_TEAM_COUNT)]
            for col in C.IMPORT_TEAMS_REQUIRED_COLUMNS
        })
        teams_df.to_csv(templates["teams"], index=False)

        # Step 3: Apply the import to the same temp_dir
        result = apply_official_import_file(
            templates["teams"],
            output_dir=temp_dir,
            create_backup=False,
            re_prepare=False,
        )

        assert result["success"]

        # Step 4: Evaluate readiness (should still be blocked due to other missing data)
        report = evaluate_official_final_readiness(temp_dir)
        assert report["summary"]["teams_count"] == C.OFFICIAL_REQUIRED_TEAM_COUNT


if __name__ == "__main__":
    pytest.main([__file__, "-v"])