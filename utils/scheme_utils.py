"""
utils/scheme_utils.py
Helpers for loading and formatting the government schemes knowledge base.
"""

import json
import os


# ── Load schemes JSON ──────────────────────────────────────────────────────────

def load_schemes() -> list:
    """
    Load government schemes from data/schemes.json.
    Returns an empty list if the file is missing.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "data", "schemes.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def load_documents() -> list:
    """
    Load government document info from data/documents.json.
    Returns an empty list if the file is missing.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = os.path.join(base_dir, "data", "documents.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def format_schemes_context() -> str:
    """
    Format all schemes from schemes.json into a single string for Gemini injection.
    """
    schemes = load_schemes()
    if not schemes:
        return "No scheme data available."

    lines = []
    for s in schemes:
        lines.append(
            f"SCHEME: {s.get('name', 'N/A')}\n"
            f"  Category: {s.get('category', 'N/A')}\n"
            f"  Description: {s.get('description', 'N/A')}\n"
            f"  Eligibility: {s.get('eligibility', 'N/A')}\n"
            f"  Benefits: {s.get('benefits', 'N/A')}\n"
            f"  Apply URL: {s.get('apply_url', 'N/A')}\n"
        )
    return "\n".join(lines)


def format_documents_context() -> str:
    """
    Format all documents from documents.json into a single string for Gemini injection.
    """
    docs = load_documents()
    if not docs:
        return "No document data available."

    lines = []
    for d in docs:
        required = ", ".join(d.get("required_documents", []))
        steps = " | ".join(d.get("steps", []))
        lines.append(
            f"DOCUMENT: {d.get('name', 'N/A')}\n"
            f"  Purpose: {d.get('purpose', 'N/A')}\n"
            f"  Issuing Authority: {d.get('issuing_authority', 'N/A')}\n"
            f"  Required Documents: {required}\n"
            f"  Steps: {steps}\n"
        )
    return "\n".join(lines)


def get_scheme_names() -> list:
    """Return a flat list of all scheme names for display."""
    return [s.get("name", "") for s in load_schemes()]


def get_document_names() -> list:
    """Return a flat list of all document names for quick-select buttons."""
    return [d.get("name", "") for d in load_documents()]


# ── Indian states list ─────────────────────────────────────────────────────────
INDIAN_STATES = [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
    "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur", "Meghalaya",
    "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim",
    "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh", "Uttarakhand",
    "West Bengal",
    # Union Territories
    "Andaman & Nicobar Islands", "Chandigarh", "Dadra & Nagar Haveli",
    "Daman & Diu", "Delhi", "Jammu & Kashmir", "Ladakh", "Lakshadweep",
    "Puducherry",
]

INCOME_RANGES = [
    "Below ₹1 Lakh",
    "₹1 Lakh – ₹2.5 Lakh",
    "₹2.5 Lakh – ₹5 Lakh",
    "₹5 Lakh – ₹10 Lakh",
    "Above ₹10 Lakh",
]

CATEGORIES = ["General", "OBC", "SC", "ST", "EWS (Economically Weaker Section)"]

OCCUPATIONS = [
    "Farmer / Agricultural Labourer",
    "Daily Wage Worker",
    "Self-Employed / Small Business",
    "Salaried (Private Sector)",
    "Salaried (Government)",
    "Student",
    "Homemaker",
    "Unemployed",
    "Other",
]
