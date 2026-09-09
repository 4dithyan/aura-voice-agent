"""app/browser/form_filler.py — Safe, semantic form filling."""
from __future__ import annotations
from typing import Dict, Any, TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page


# Known field name -> profile key mappings
FIELD_MAPPINGS: Dict[str, str] = {
    "first_name": ["first_name", "firstName", "first-name", "fname", "given-name"],
    "last_name": ["last_name", "lastName", "last-name", "lname", "family-name"],
    "email": ["email", "email_address", "emailAddress"],
    "phone": ["phone", "mobile", "tel", "telephone", "phonenumber", "phone_number"],
    "address": ["address", "address1", "street", "street_address"],
    "city": ["city", "town"],
    "state": ["state", "province", "region"],
    "postal_code": ["postal_code", "zip", "zipcode", "pincode", "postcode"],
    "country": ["country"],
    "name": ["name", "full_name", "fullName", "cardholder"],
}

# These fields must NEVER be auto-filled from profile data
BLOCKED_FIELDS = {"password", "cvv", "card_number", "otp", "ssn", "credit_card"}


def fill_form(page: "Page", profile: Dict[str, str]) -> Dict[str, Any]:
    """
    Fills a form using user-provided profile data.
    Blocked / sensitive fields are skipped; user must fill them manually.
    Returns a dict of filled and skipped fields.
    """
    filled = []
    skipped = []

    try:
        inputs = page.query_selector_all("input:not([type='hidden']), textarea")
        for inp in inputs:
            try:
                if not inp.is_visible():
                    continue

                name_attr = (
                    inp.get_attribute("name") or
                    inp.get_attribute("id") or
                    inp.get_attribute("autocomplete") or
                    inp.get_attribute("placeholder") or ""
                ).lower()

                # Block sensitive fields
                if any(b in name_attr for b in BLOCKED_FIELDS):
                    skipped.append(name_attr)
                    continue

                # Match to profile data
                matched_key = None
                matched_value = None
                for profile_key, aliases in FIELD_MAPPINGS.items():
                    if any(alias.lower() in name_attr for alias in aliases):
                        if profile_key in profile:
                            matched_key = profile_key
                            matched_value = profile[profile_key]
                            break

                if matched_key and matched_value:
                    inp.fill(matched_value)
                    filled.append(f"{matched_key}={matched_value[:10]}...")
            except Exception:
                continue
    except Exception as e:
        return {"success": False, "error": str(e), "filled": [], "skipped": []}

    return {"success": True, "filled": filled, "skipped": skipped}
