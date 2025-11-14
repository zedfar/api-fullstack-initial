#!/usr/bin/env python3
"""
Script untuk test apakah ACCESS_TOKEN_EXPIRE_MINUTES dibaca dengan benar
"""
import sys
from datetime import timedelta

# Test 1: Load config
try:
    from app.config import settings
    print("✓ Config loaded successfully")
    print(f"  ACCESS_TOKEN_EXPIRE_MINUTES type: {type(settings.ACCESS_TOKEN_EXPIRE_MINUTES)}")
    print(f"  ACCESS_TOKEN_EXPIRE_MINUTES value: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
except Exception as e:
    print(f"✗ Error loading config: {e}")
    sys.exit(1)

# Test 2: Check if it's int
if isinstance(settings.ACCESS_TOKEN_EXPIRE_MINUTES, int):
    print("✓ ACCESS_TOKEN_EXPIRE_MINUTES is int")
else:
    print(f"✗ ACCESS_TOKEN_EXPIRE_MINUTES is {type(settings.ACCESS_TOKEN_EXPIRE_MINUTES).__name__}, not int!")

# Test 3: Test dengan timedelta
try:
    td = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    print(f"✓ timedelta works: {td}")
    print(f"  Total seconds: {td.total_seconds()}")
    print(f"  Total minutes: {td.total_seconds() / 60}")
except Exception as e:
    print(f"✗ timedelta error: {e}")

# Test 4: Simulate token creation
try:
    from datetime import datetime
    from app.utils.security import create_access_token

    token = create_access_token(data={"sub": "testuser"})
    print("✓ Token created successfully")

    # Decode to check expiration
    from jose import jwt
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    exp_timestamp = decoded['exp']
    iat_timestamp = decoded.get('iat', datetime.utcnow().timestamp())

    exp_time = datetime.fromtimestamp(exp_timestamp)
    current_time = datetime.utcnow()

    difference_seconds = exp_timestamp - current_time.timestamp()
    difference_minutes = difference_seconds / 60

    print(f"  Token expires at: {exp_time}")
    print(f"  Current time: {current_time}")
    print(f"  Time until expiration: {difference_minutes:.2f} minutes")

    if abs(difference_minutes - 240) < 1:  # tolerance 1 minute
        print("✓ Token expiration is correct (~240 minutes)")
    else:
        print(f"✗ Token expiration is WRONG! Expected 240, got {difference_minutes:.2f} minutes")

except Exception as e:
    print(f"✗ Token test error: {e}")
    import traceback
    traceback.print_exc()
