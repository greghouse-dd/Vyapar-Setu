"""
Vyapar Setu — Database & Scenario Service Unit Tests
=====================================================
Tests SQLite database schema creation, audit logging, and demo scenario configuration.
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# Add backend root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from db.init_db import init_db
from db.database import engine
from services.scenario_service import get_demo_scenario, PORT_CONSTRAINTS


class TestDatabaseAndScenario:
    def test_database_initialization(self):
        """Database initialization should create vyapar_setu.db with required tables."""
        init_db()

        inspector = sqlite3.connect("vyapar_setu.db")
        cursor = inspector.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        inspector.close()


        expected_tables = ["weekly_features", "port_constraints", "decision_log", "voice_note_log"]
        for t in expected_tables:
            assert t in tables, f"Table {t} missing from SQLite schema"

    def test_demo_scenario_integrity(self):
        """get_demo_scenario() should return required fields and valid current dates."""
        scenario = get_demo_scenario()

        assert scenario["origin"] == "Australia"
        assert scenario["destination"] == "Paradip"
        assert scenario["cargo_tonnes"] == 65_000
        assert scenario["vessel_class"] == "Panamax"
        assert "as_of_date" in scenario
        assert "required_by_date" in scenario

    def test_port_constraints_lookup(self):
        """PORT_CONSTRAINTS should cover all named destination ports with valid max DWT."""
        ports = ["Paradip", "Dhamra", "Vizag", "Gangavaram", "Gopalpur", "Haldia", "Sagar-Sandheads"]
        for p in ports:
            assert p in PORT_CONSTRAINTS
            assert PORT_CONSTRAINTS[p]["max_dwt_tonnes"] > 0
            assert PORT_CONSTRAINTS[p]["max_draft_m"] > 0
