import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timedelta

# Set a random seed for reproducibility (so you get the same numbers every time)
np.random.seed(42)

# --- CONFIGURATION ---
NUM_USERS = 50000
CONVERSION_RATE_CONTROL = 0.150  # 15.0% baseline conversion
CONVERSION_RATE_TREATMENT = 0.165  # 16.5% new UI conversion (10% relative uplift)
AVERAGE_ORDER_VALUE = 350 # in INR
AOV_STD_DEV = 80 # Standard deviation for order value noise

print("Starting data generation...")

# --- 1. GENERATE USERS TABLE ---
print("Generating Users table...")
user_ids = [str(uuid.uuid4()) for _ in range(NUM_USERS)]
signup_dates = [datetime.now() - timedelta(days=np.random.randint(10, 365)) for _ in range(NUM_USERS)]
locations = np.random.choice(['Koramangala', 'Indiranagar', 'HSR Layout', 'Whitefield', 'Jayanagar'], NUM_USERS)

users_df = pd.DataFrame({
    'user_id': user_ids,
    'signup_date': signup_dates,
    'primary_location': locations
})

# --- 2. GENERATE EXPERIMENTS TABLE ---
print("Generating Experiments table...")
# Randomly assign 50% to Control and 50% to Treatment
variants = np.random.choice(['Control', 'Treatment'], NUM_USERS, p=[0.5, 0.5])
# Simulate session timestamps over a 14-day A/B test period
session_timestamps = [datetime.now() - timedelta(days=np.random.randint(1, 14), hours=np.random.randint(0, 24)) for _ in range(NUM_USERS)]
session_ids = [str(uuid.uuid4()) for _ in range(NUM_USERS)]

experiments_df = pd.DataFrame({
    'session_id': session_ids,
    'user_id': user_ids,
    'timestamp': session_timestamps,
    'variant': variants
})

# --- 3. GENERATE ORDERS TABLE ---
print("Generating Orders table...")
orders_data = []

for i in range(NUM_USERS):
    variant = variants[i]
    
    # Determine if this user checked out based on their group's probability
    if variant == 'Control':
        converted = np.random.rand() < CONVERSION_RATE_CONTROL
    else:
        converted = np.random.rand() < CONVERSION_RATE_TREATMENT
        
    if converted:
        # Generate a realistic order value using a normal distribution
        order_value = max(50, np.random.normal(AVERAGE_ORDER_VALUE, AOV_STD_DEV))
        orders_data.append({
            'order_id': str(uuid.uuid4()),
            'session_id': session_ids[i],
            'order_amount': round(order_value, 2),
            'restaurant_id': f"REST_{np.random.randint(100, 999)}"
        })

orders_df = pd.DataFrame(orders_data)

# --- 4. EXPORT TO CSV ---
print("Saving files to /data directory...")
users_df.to_csv('../data/users.csv', index=False)
experiments_df.to_csv('../data/experiments.csv', index=False)
orders_df.to_csv('../data/orders.csv', index=False)

print(f"Success! Generated {len(users_df)} users and {len(orders_df)} orders.")