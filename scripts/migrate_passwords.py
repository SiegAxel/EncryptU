#!/usr/bin/env python3
"""
Database migration script to handle existing plaintext passwords
This script helps migrate from plaintext to Argon2 hashed passwords
"""
import asyncio
import os
from typing import List, Tuple
from prisma import Prisma
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHash
import re

class PasswordMigration:
    def __init__(self):
        self.prisma = Prisma()
        self.ph = PasswordHasher()
        
    async def connect(self):
        """Connect to database"""
        await self.prisma.connect()
        print("✅ Connected to database")
    
    async def disconnect(self):
        """Disconnect from database"""
        await self.prisma.disconnect()
        print("✅ Disconnected from database")
    
    def is_plaintext_password(self, password_hash: str) -> bool:
        """
        Check if a password hash is plaintext (not Argon2)
        Argon2 hashes start with $argon2
        """
        return not (password_hash.startswith('$argon2') or 
                   password_hash.startswith('$bcrypt$') or 
                   password_hash.startswith('$2b$'))
    
    async def get_users_with_plaintext_passwords(self) -> List[dict]:
        """Get all users with plaintext passwords"""
        users = await self.prisma.user.find_many()
        plaintext_users = []
        
        for user in users:
            if self.is_plaintext_password(user.passwordHash):
                plaintext_users.append({
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'passwordHash': user.passwordHash
                })
        
        return plaintext_users
    
    async def migrate_user_password(self, user_data: dict) -> bool:
        """
        Migrate a single user's plaintext password to Argon2
        Returns True if successful, False otherwise
        """
        try:
            plaintext_password = user_data['passwordHash']
            
            # Hash the plaintext password with Argon2
            hashed_password = self.ph.hash(plaintext_password)
            
            # Update user in database
            await self.prisma.user.update(
                where={'id': user_data['id']},
                data={'passwordHash': hashed_password}
            )
            
            print(f"✅ Migrated user {user_data['email']} (ID: {user_data['id']})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to migrate user {user_data['email']}: {e}")
            return False
    
    async def add_backward_compatibility(self):
        """
        Add a new column to track password hash type
        This allows for gradual migration
        """
        try:
            # Add password_hash_type column if it doesn't exist
            await self.prisma.$execute_raw("""
                DO $$ 
                BEGIN
                    IF NOT EXISTS (
                        SELECT 1 FROM information_schema.columns 
                        WHERE table_name = 'User' AND column_name = 'password_hash_type'
                    ) THEN
                        ALTER TABLE "User" ADD COLUMN password_hash_type VARCHAR(20) DEFAULT 'argon2';
                    END IF;
                END $$;
            """)
            
            print("✅ Added password_hash_type column")
            
        except Exception as e:
            print(f"❌ Failed to add password_hash_type column: {e}")
    
    async def run_migration(self, dry_run: bool = False) -> Tuple[int, int]:
        """
        Run the full migration process
        
        Args:
            dry_run: If True, only show what would be migrated without making changes
            
        Returns:
            Tuple of (total_users, migrated_users)
        """
        try:
            await self.connect()
            
            # Add backward compatibility column
            await self.add_backward_compatibility()
            
            # Get users with plaintext passwords
            plaintext_users = await self.get_users_with_plaintext_passwords()
            total_users = len(plaintext_users)
            
            if total_users == 0:
                print("✅ No users with plaintext passwords found")
                await self.disconnect()
                return 0, 0
            
            print(f"\n🔍 Found {total_users} users with plaintext passwords:")
            for user in plaintext_users:
                print(f"  - {user['email']} (ID: {user['id']})")
            
            if dry_run:
                print("\n🧪 DRY RUN: No changes will be made")
                await self.disconnect()
                return total_users, 0
            
            # Migrate users
            migrated_count = 0
            failed_count = 0
            
            print(f"\n🔄 Starting migration of {total_users} users...")
            
            for user_data in plaintext_users:
                success = await self.migrate_user_password(user_data)
                if success:
                    migrated_count += 1
                else:
                    failed_count += 1
                
                # Small delay to avoid overwhelming the database
                await asyncio.sleep(0.1)
            
            print(f"\n📊 Migration complete:")
            print(f"  Total users with plaintext passwords: {total_users}")
            print(f"  Successfully migrated: {migrated_count}")
            print(f"  Failed migrations: {failed_count}")
            print(f"  Remaining: {total_users - migrated_count}")
            
            await self.disconnect()
            return total_users, migrated_count
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            await self.disconnect()
            return 0, 0

async def main():
    """Main migration function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate plaintext passwords to Argon2')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show what would be migrated without making changes')
    args = parser.parse_args()
    
    migration = PasswordMigration()
    
    if args.dry_run:
        print("🧪 DRY RUN MODE - No changes will be made to the database")
    
    total, migrated = await migration.run_migration(dry_run=args.dry_run)
    
    if args.dry_run:
        print(f"\n🧪 Dry run complete: {migrated} users would be migrated")
    else:
        print(f"\n🎉 Migration complete: {migrated} users migrated successfully")

if __name__ == "__main__":
    asyncio.run(main())