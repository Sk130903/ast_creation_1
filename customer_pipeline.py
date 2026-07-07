
import pandas as pd
from utility_functions import (
    clean_customer_names,
    calculate_final_amount,
    assign_customer_tier,
    validate_email,
)

# -------- Cell 1 --------
customers = pd.DataFrame({
    "customer_id":[1,2,3,4],
    "customer_name":[" alice ","BOB",None,"charlie"],
    "purchase_amount":[1200,650,300,1800],
    "email":[
        "alice@test.com",
        "bob@test.com",
        "invalid_email",
        "charlie@test.com"
    ]
})

# -------- Cell 2 --------
customers = clean_customer_names(customers)

# -------- Cell 3 --------
customers["final_amount"] = customers["purchase_amount"].apply(
    calculate_final_amount
)

# -------- Cell 4 --------
customers["tier"] = customers["purchase_amount"].apply(
    assign_customer_tier
)

# -------- Cell 5 --------
customers["email_valid"] = customers["email"].apply(
    validate_email
)

# -------- Cell 6 --------
summary = (
    customers.groupby("tier")
    .agg(
        customers=("customer_id","count"),
        revenue=("final_amount","sum")
    )
    .reset_index()
)

print(customers)
print(summary)
