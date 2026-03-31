"""
Synthetic Data Seeder for Weedscore.
Generates Reproducible scenarios for mathematical logic validation.
"""

import sys
import argparse
from datetime import datetime, timedelta, timezone
from sqlalchemy import text
from src.database.connection import get_session
from src.database.models import Session

def seed_db(scenario: str) -> None:
    """
    Seeds the database with predefined sessions based on the requested scenario.
    Ensures an idempotent 'clean slate' by truncating the sessions table.
    """
    try:
        with get_session() as db:
            # 1. Clean slate (Idempotency)
            print("Cleaning existing sessions...")
            db.execute(text("TRUNCATE TABLE sessions RESTART IDENTITY CASCADE;"))
            db.commit()

            now = datetime.now(timezone.utc)
            sessions_to_add = []

            # Scenario 1: The Moderator (4 sessions)
            # Spaced 12 days apart, most recent 21 days ago: T-21, T-33, T-45, T-57
            if scenario == "moderator":
                print("Preparing Scenario: The Moderator...")
                for days in [21, 33, 45, 57]:
                    sessions_to_add.append(Session(
                        timestamp=now - timedelta(days=days),
                        is_solo=False,
                        is_special_occasion=False,
                        score_at_time=0.0,
                        notes="Scenario: The Moderator"
                    ))

            # Scenario 2: The Bender (4 sessions) - Kept for reference
            elif scenario == "bender":
                print("Preparing Scenario: The Bender...")
                for hours in [0, 12, 36, 60]:
                    sessions_to_add.append(Session(
                        timestamp=now - timedelta(hours=hours),
                        is_solo=True,
                        is_special_occasion=False,
                        score_at_time=0.0,
                        notes="Scenario: The Bender"
                    ))

            # Scenario 3: The Sabbatical (1 session)
            # Exactly 60 days ago
            elif scenario == "sabbatical":
                print("Preparing Scenario: The Sabbatical...")
                sessions_to_add.append(Session(
                    timestamp=now - timedelta(days=60),
                    is_solo=False,
                    is_special_occasion=False,
                    score_at_time=0.0,
                    notes="Scenario: The Sabbatical"
                ))

            # Scenario 4: The Clean Slate
            # Zero sessions
            elif scenario == "clean_slate":
                print("Preparing Scenario: The Clean Slate...")
                # No sessions to add

            if sessions_to_add or scenario == "clean_slate":
                if sessions_to_add:
                    db.add_all(sessions_to_add)
                    db.commit()
                print(f"Successfully seeded {len(sessions_to_add)} sessions for scenario: {scenario}")
            else:
                print(f"No sessions added. Invalid or empty scenario: {scenario}")

    except Exception as e:
        print(f"Error seeding database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the Weedscore database with test scenarios.")
    parser.add_argument(
        "--scenario",
        type=str,
        required=True,
        choices=["moderator", "bender", "sabbatical", "clean_slate"],
        help="The specific scenario to seed (moderator, bender, sabbatical, or clean_slate)."
    )
    args = parser.parse_args()
    seed_db(args.scenario)
