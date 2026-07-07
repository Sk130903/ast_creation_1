
import pandas as pd

def clean_customer_names(df):
    df = df.copy()
    df["customer_name"] = (
        df["customer_name"]
        .fillna("Unknown")
        .str.strip()
        .str.title()
    )
    return df

def calculate_discount(amount):
    if amount >= 1000:
        return amount * 0.15
    elif amount >= 500:
        return amount * 0.10
    return amount * 0.05

def calculate_final_amount(amount):
    discount = calculate_discount(amount)
    return amount - discount

def assign_customer_tier(amount):
    if amount >= 1000:
        return "Platinum"
    elif amount >= 500:
        return "Gold"
    return "Silver"

def validate_email(email):
    return isinstance(email, str) and "@" in email and "." in email
