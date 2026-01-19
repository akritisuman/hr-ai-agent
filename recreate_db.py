"""
Utility script to recreate the authentication database
Use this if you encounter schema mismatch errors

WARNING: This will delete all existing user accounts!
"""

import os
from database import Base, engine

def recreate_database():
    """Drop all tables and recreate with current schema"""
    print("Recreating authentication database...")
    
    # Drop all existing tables
    Base.metadata.drop_all(bind=engine)
    print("✓ Dropped all existing tables")
    
    # Create all tables with current schema
    Base.metadata.create_all(bind=engine)
    print("✓ Created all tables with current schema")
    
    print("\nDatabase recreated successfully!")
    print("All existing user accounts have been removed.")
    print("You can now create new accounts via the signup page.")

if __name__ == "__main__":
    # Confirm before proceeding
    response = input("This will delete all user accounts. Continue? (yes/no): ")
    if response.lower() == "yes":
        recreate_database()
    else:
        print("Cancelled.")








