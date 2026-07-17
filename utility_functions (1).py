import re
import math
import hashlib
import pandas as pd


def clean_customer_names(df):
    '''Normalize the customer_name column: fill missing values, strip whitespace, title-case.'''
    df = df.copy()
    df["customer_name"] = (
        df["customer_name"]
        .fillna("Unknown")
        .str.strip()
        .str.title()
    )
    return df


def calculate_discount(amount):
    '''Tiered discount rate. Platinum-level spend gets the deepest discount.'''
    if amount >= 1000:
        return amount * 0.15
    elif amount >= 500:
        return amount * 0.10
    elif amount >= 200:
        return amount * 0.07
    return amount * 0.05


def calculate_final_amount(amount):
    '''Purchase amount net of the tiered discount.'''
    discount = calculate_discount(amount)
    return amount - discount


def assign_customer_tier(amount):
    '''Map a purchase amount to a loyalty tier label.'''
    if amount >= 1000:
        return "Platinum"
    elif amount >= 500:
        return "Gold"
    elif amount >= 200:
        return "Silver"
    return "Bronze"


def validate_email(email):
    '''Lightweight structural email check (not RFC-complete, just enough to flag junk data).'''
    if not isinstance(email, str):
        return False
    pattern = r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))


def normalize_phone_number(phone, default_country_code="1"):
    '''Strip formatting characters from a phone number and prefix a country code if missing.'''
    if not isinstance(phone, str):
        return None
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return None
    if len(digits) == 10:
        digits = default_country_code + digits
    elif len(digits) < 10:
        return None
    return "+" + digits


def calculate_loyalty_points(amount, tier):
    '''Loyalty points earned on a purchase, with a per-tier multiplier bonus.'''
    base_points = math.floor(amount / 10)
    multipliers = {"Platinum": 3.0, "Gold": 2.0, "Silver": 1.5, "Bronze": 1.0}
    multiplier = multipliers.get(tier, 1.0)
    return int(base_points * multiplier)


def categorize_purchase_channel(channel):
    '''Bucket a raw channel string into a small set of canonical categories.'''
    if not isinstance(channel, str):
        return "unknown"
    channel_lower = channel.strip().lower()
    if channel_lower in ("web", "website", "online", "ecommerce"):
        return "online"
    elif channel_lower in ("app", "mobile", "ios", "android"):
        return "mobile"
    elif channel_lower in ("store", "in-store", "retail", "pos"):
        return "in_store"
    elif channel_lower in ("phone", "call", "call_center"):
        return "phone"
    return "other"


def compute_shipping_cost(amount, region, is_expedited=False):
    '''Region-tiered shipping cost, waived above a free-shipping threshold.'''
    FREE_SHIPPING_THRESHOLD = 750
    if amount >= FREE_SHIPPING_THRESHOLD and not is_expedited:
        return 0.0

    base_rates = {"domestic": 5.99, "north_america": 9.99, "international": 19.99}
    region_key = region.lower() if isinstance(region, str) else "international"
    base = base_rates.get(region_key, base_rates["international"])

    if is_expedited:
        base *= 2.5

    return round(base, 2)


def is_valid_postal_code(code, country="US"):
    '''Validate a postal code against a couple of common national formats.'''
    if not isinstance(code, str):
        return False
    code = code.strip()
    if country == "US":
        return bool(re.match(r"^\d{5}(-\d{4})?$", code))
    elif country == "CA":
        return bool(re.match(r"^[A-Za-z]\d[A-Za-z] ?\d[A-Za-z]\d$", code))
    elif country == "UK":
        return bool(re.match(r"^[A-Za-z]{1,2}\d[A-Za-z\d]? ?\d[A-Za-z]{2}$", code))
    return len(code) >= 3


def calculate_tax(amount, region):
    '''Flat regional tax rate lookup, applied to the (pre-discount) purchase amount.'''
    tax_rates = {
        "CA": 0.0725, "NY": 0.08875, "TX": 0.0625, "WA": 0.065,
        "domestic": 0.05, "international": 0.0,
    }
    rate = tax_rates.get(region, tax_rates["domestic"])
    return round(amount * rate, 2)


def generate_customer_id(name, index):
    '''Deterministic short customer ID derived from name + row index.'''
    raw = f"{name}-{index}".encode("utf-8")
    digest = hashlib.sha1(raw).hexdigest()[:8]
    return f"CUST-{digest.upper()}"


def deduplicate_customers(df, subset=("customer_name", "email")):
    '''Drop duplicate customer rows, keeping the first (earliest) occurrence.'''
    df = df.copy()
    before = len(df)
    df = df.drop_duplicates(subset=list(subset), keep="first")
    removed = before - len(df)
    if removed > 0:
        print(f"[deduplicate_customers] removed {removed} duplicate row(s)")
    return df


def flag_high_risk_transaction(amount, country, email_valid):
    '''Heuristic fraud/risk flag combining amount, geography, and email validity.'''
    risk_score = 0
    if amount >= 2000:
        risk_score += 2
    elif amount >= 1000:
        risk_score += 1

    if not email_valid:
        risk_score += 2

    high_risk_countries = {"XX", "ZZ", "QQ"}
    if country in high_risk_countries:
        risk_score += 3

    if risk_score >= 4:
        return "high"
    elif risk_score >= 2:
        return "medium"
    return "low"


def summarize_customer_batch(df):
    '''Roll a customer-level dataframe up into a small dict of summary statistics.'''
    if df.empty:
        return {"count": 0, "total_revenue": 0.0, "avg_purchase": 0.0}
    return {
        "count": len(df),
        "total_revenue": round(df["purchase_amount"].sum(), 2),
        "avg_purchase": round(df["purchase_amount"].mean(), 2),
        "top_tier": df["tier"].mode().iloc[0] if "tier" in df.columns and not df["tier"].mode().empty else None,
    }
