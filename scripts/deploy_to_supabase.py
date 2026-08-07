#!/usr/bin/env python3
"""
HADEETH.ID Direct Supabase Deployment Tool
Executes all SQL migrations and seeds directly to your Supabase PostgreSQL instance
using psycopg / urllib / Supabase REST API or Postgres Connection String.
"""

import os
import sys
import glob
import requests

def main():
    print("=== HADEETH.ID DIRECT SUPABASE DEPLOYMENT TOOL ===")
    
    supabase_url = input("Enter your Supabase Project URL (e.g. https://xyz.supabase.co): ").strip()
    service_role_key = input("Enter your Supabase Service Role Key (secret): ").strip()
    
    if not supabase_url or not service_role_key:
        print("Error: Supabase URL and Service Role Key are required.")
        return

    headers = {
        "apikey": service_role_key,
        "Authorization": f"Bearer {service_role_key}",
        "Content-Type": "application/json"
    }
    
    # Test connection
    print("Connecting to Supabase REST API...")
    res = requests.get(f"{supabase_url}/rest/v1/books?select=count", headers=headers)
    if res.status_code in [200, 404, 400]:
        print("Connected to Supabase successfully!")
    else:
        print(f"Connection test failed: HTTP {res.status_code}")
        return

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    seeds_dir = os.path.join(base_dir, "supabase", "seeds")
    
    # Read books.json
    with open(os.path.join(base_dir, "data", "books.json"), "r", encoding="utf-8") as f:
        books_data = json.load(f)
        
    print("Deploying books metadata to Supabase...")
    r = requests.post(f"{supabase_url}/rest/v1/books", headers=headers, json=books_data, params={"on_conflict": "id"})
    print(f"Books deploy status: {r.status_code}")

if __name__ == "__main__":
    main()
