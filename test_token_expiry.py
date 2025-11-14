#!/usr/bin/env python3
"""
Simple test untuk verifikasi JWT expiration time
Decode existing token untuk cek berapa lama expire-nya
"""

from jose import jwt
from datetime import datetime

# Paste token Anda di sini
TEST_TOKEN = input("Paste your JWT token (or press Enter to skip): ").strip()

if TEST_TOKEN:
    try:
        # Decode tanpa verify signature (hanya untuk cek payload)
        decoded = jwt.decode(TEST_TOKEN, options={"verify_signature": False})

        print("\n=== Token Info ===")
        print(f"Subject (sub): {decoded.get('sub')}")

        if 'exp' in decoded:
            exp_timestamp = decoded['exp']
            exp_time = datetime.fromtimestamp(exp_timestamp)
            current_time = datetime.utcnow()

            print(f"Expires at: {exp_time} UTC")
            print(f"Current time: {current_time} UTC")

            # Calculate difference
            if current_time < exp_time:
                diff_seconds = exp_timestamp - current_time.timestamp()
                diff_minutes = diff_seconds / 60
                diff_hours = diff_minutes / 60

                print(f"\nTime until expiration:")
                print(f"  {diff_minutes:.2f} minutes")
                print(f"  {diff_hours:.2f} hours")

                # Check if it's 240 minutes from creation
                if 'iat' in decoded:
                    iat_timestamp = decoded['iat']
                    iat_time = datetime.fromtimestamp(iat_timestamp)
                    total_lifetime_seconds = exp_timestamp - iat_timestamp
                    total_lifetime_minutes = total_lifetime_seconds / 60

                    print(f"\nToken lifetime (from creation to expiry):")
                    print(f"  {total_lifetime_minutes:.2f} minutes")
                    print(f"  {total_lifetime_minutes / 60:.2f} hours")

                    if abs(total_lifetime_minutes - 240) < 1:
                        print("\n✓ Token configured correctly (240 minutes)")
                    else:
                        print(f"\n✗ Token NOT configured for 240 minutes!")
                        print(f"  Expected: 240 minutes")
                        print(f"  Actual: {total_lifetime_minutes:.2f} minutes")
            else:
                print("\n✗ Token already expired!")
        else:
            print("No expiration (exp) field found in token")

    except Exception as e:
        print(f"Error decoding token: {e}")
else:
    print("\nTest dibatalkan. Untuk test:")
    print("1. Login ke API dan dapatkan access_token")
    print("2. Run script ini dan paste token")
    print("3. Script akan menampilkan berapa menit token akan expire")
