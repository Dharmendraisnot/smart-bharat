"""
utils/db_utils.py
Real SQLite persistence layer for Smart Bharat grievance management.

The database file is created automatically at db/grievances.db on first use.
Three demo rows are seeded once so the Track Complaint feature works
immediately without filing a new complaint.

Public API (unchanged from the placeholder — all pages work without edits):
    init_db()
    file_grievance(name, phone, description, location, category, priority, summary) -> str
    track_grievance(complaint_id) -> dict | None
    get_all_grievances() -> list[dict]
"""

from __future__ import annotations

import logging
import os
import random
import re
import sqlite3
import string
from contextlib import contextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Database path ──────────────────────────────────────────────────────────────
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DB_PATH  = os.path.join(_BASE_DIR, "db", "grievances.db")

# ── Demo seed data (inserted once) ────────────────────────────────────────────
_DEMO_ROWS: list[dict] = [
    {
        "id":          "SB-20240115-DEMO",
        "name":        "Ramesh Kumar",
        "phone":       "9876543210",
        "category":    "Roads & Infrastructure",
        "description": "Large pothole on MG Road near city bus stand causing accidents.",
        "location":    "MG Road, Bengaluru",
        "priority":    "High",
        "status":      "In Progress",
        "created_at":  "2024-01-15 09:30:00",
        "updated_at":  "2024-01-17 14:00:00",
    },
    {
        "id":          "SB-20240116-SAMP",
        "name":        "Priya Sharma",
        "phone":       "8765432109",
        "category":    "Water Supply",
        "description": "No water supply for the past 3 days in our area.",
        "location":    "Sector 12, Noida",
        "priority":    "High",
        "status":      "Pending",
        "created_at":  "2024-01-16 11:00:00",
        "updated_at":  "2024-01-16 11:00:00",
    },
    {
        "id":          "SB-20240110-TEST",
        "name":        "Sunil Patel",
        "phone":       "7654321098",
        "category":    "Sanitation & Waste",
        "description": "Garbage not collected for over a week. Street is overflowing.",
        "location":    "Ward 5, Ahmedabad",
        "priority":    "Medium",
        "status":      "Resolved",
        "created_at":  "2024-01-10 08:00:00",
        "updated_at":  "2024-01-13 16:30:00",
    },
]

# ── Internal helpers ───────────────────────────────────────────────────────────

@contextmanager
def _connect():
    """Yield a thread-safe SQLite connection with row_factory set."""
    os.makedirs(os.path.dirname(_DB_PATH), exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _generate_complaint_id() -> str:
    """
    Generate a unique, human-readable complaint ID: SB-YYYYMMDD-XXXX.
    Retries until the generated ID does not already exist in the DB.
    """
    date_str = datetime.now().strftime("%Y%m%d")
    for _ in range(10):
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        cid = f"SB-{date_str}-{suffix}"
        if track_grievance(cid) is None:
            return cid
    # Extremely unlikely collision fallback – extend suffix to 6 chars
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"SB-{date_str}-{suffix}"


def _row_to_dict(row: sqlite3.Row) -> dict:
    return dict(row)


# ── Public API ─────────────────────────────────────────────────────────────────

def init_db() -> None:
    """
    Create the grievances table if it does not exist and seed demo rows.
    Safe to call multiple times (idempotent).
    """
    try:
        with _connect() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS grievances (
                    id          TEXT PRIMARY KEY,
                    name        TEXT NOT NULL,
                    phone       TEXT NOT NULL,
                    category    TEXT NOT NULL DEFAULT 'Other',
                    description TEXT NOT NULL,
                    location    TEXT NOT NULL,
                    priority    TEXT NOT NULL DEFAULT 'Medium',
                    status      TEXT NOT NULL DEFAULT 'Pending',
                    created_at  TEXT NOT NULL,
                    updated_at  TEXT NOT NULL
                )
            """)

            # Seed demo rows (INSERT OR IGNORE keeps this idempotent)
            for row in _DEMO_ROWS:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO grievances
                        (id, name, phone, category, description, location,
                         priority, status, created_at, updated_at)
                    VALUES
                        (:id, :name, :phone, :category, :description, :location,
                         :priority, :status, :created_at, :updated_at)
                    """,
                    row,
                )

        logger.info("Database ready at %s", _DB_PATH)

    except Exception as exc:
        logger.error("init_db failed: %s", exc)
        # Re-raise so the caller (app.py) surfaces the problem clearly.
        raise


def file_grievance(
    name:        str,
    phone:       str,
    description: str,
    location:    str,
    category:    str = "Other",
    priority:    str = "Medium",
    summary:     str = "",          # accepted but not stored (kept for API compat)
) -> str:
    """
    Insert a new grievance row and return the generated complaint ID.

    Args:
        name:        Citizen's full name.
        phone:       10-digit mobile number (validated by the page, stored as-is).
        description: Full complaint text.
        location:    City / area / landmark.
        category:    AI-assigned category string.
        priority:    AI-assigned priority ("High" | "Medium" | "Low").
        summary:     Short AI summary (optional, kept for interface compatibility).

    Returns:
        str: Complaint ID, e.g. "SB-20240120-AB3X"

    Raises:
        RuntimeError: If the INSERT fails after ID generation.
    """
    complaint_id = _generate_complaint_id()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with _connect() as conn:
            conn.execute(
                """
                INSERT INTO grievances
                    (id, name, phone, category, description, location,
                     priority, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'Pending', ?, ?)
                """,
                (complaint_id, name, phone, category, description,
                 location, priority, now, now),
            )
        logger.info("Grievance filed: %s", complaint_id)
        return complaint_id

    except Exception as exc:
        logger.error("file_grievance failed: %s", exc)
        raise RuntimeError(f"Failed to save complaint: {exc}") from exc


def track_grievance(complaint_id: str) -> dict | None:
    """
    Retrieve a single grievance by complaint ID.

    Args:
        complaint_id: ID string (case-insensitive).

    Returns:
        dict with all columns, or None if no matching row found.
    """
    cid = complaint_id.strip().upper()
    try:
        with _connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM grievances WHERE id = ?", (cid,)
            )
            row = cursor.fetchone()
        return _row_to_dict(row) if row else None
    except Exception as exc:
        logger.error("track_grievance failed for %s: %s", cid, exc)
        return None


def get_all_grievances() -> list[dict]:
    """
    Return all grievances ordered by creation time (newest first).
    Used for admin views or exports.
    """
    try:
        with _connect() as conn:
            cursor = conn.execute(
                "SELECT * FROM grievances ORDER BY created_at DESC"
            )
            return [_row_to_dict(r) for r in cursor.fetchall()]
    except Exception as exc:
        logger.error("get_all_grievances failed: %s", exc)
        return []


def update_grievance_status(complaint_id: str, new_status: str) -> bool:
    """
    Update the status of an existing grievance.

    Args:
        complaint_id: Target complaint ID.
        new_status:   One of "Pending", "In Progress", "Resolved".

    Returns:
        True if the row was updated, False if ID not found or error occurred.
    """
    allowed = {"Pending", "In Progress", "Resolved"}
    if new_status not in allowed:
        logger.warning("Invalid status '%s' – must be one of %s", new_status, allowed)
        return False

    cid = complaint_id.strip().upper()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with _connect() as conn:
            cursor = conn.execute(
                "UPDATE grievances SET status = ?, updated_at = ? WHERE id = ?",
                (new_status, now, cid),
            )
        updated = cursor.rowcount > 0
        if updated:
            logger.info("Status of %s updated to '%s'", cid, new_status)
        else:
            logger.warning("update_grievance_status: ID %s not found", cid)
        return updated
    except Exception as exc:
        logger.error("update_grievance_status failed: %s", exc)
        return False
