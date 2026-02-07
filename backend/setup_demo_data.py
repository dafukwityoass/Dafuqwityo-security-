import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import uuid

# Password hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_database')]

def prepare_for_mongo(data):
    """Prepare data for MongoDB insertion by converting dates to ISO strings"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

async def setup_demo_data():
    print("Setting up demo data...")
    
    # Create demo users
    demo_users = [
        {
            "id": "demo-user-1",
            "email": "demo@paymentus.com",
            "password": pwd_context.hash("demo123"),
            "name": "Demo User",
            "phone": "+1-555-0123",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": "demo-user-2", 
            "email": "test@paymentus.com",
            "password": pwd_context.hash("test123"),
            "name": "Test User",
            "phone": "+1-555-0124",
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    # Clear existing demo users and insert new ones
    await db.users.delete_many({"email": {"$in": ["demo@paymentus.com", "test@paymentus.com"]}})
    for user in demo_users:
        await db.users.insert_one(prepare_for_mongo(user))
    print(f"Created {len(demo_users)} demo users")
    
    # Create demo bills for first user
    demo_bills = [
        {
            "id": str(uuid.uuid4()),
            "user_id": "demo-user-1",
            "biller_name": "Spectrum Internet",
            "account_number": "ACC-001234",
            "amount": 79.99,
            "due_date": datetime.now(timezone.utc) + timedelta(days=5),
            "status": "pending",
            "bill_type": "telecom",
            "description": "Monthly internet service",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "demo-user-1", 
            "biller_name": "ConEd Electric",
            "account_number": "ELEC-567890",
            "amount": 156.78,
            "due_date": datetime.now(timezone.utc) + timedelta(days=12),
            "status": "pending",
            "bill_type": "utility",
            "description": "Monthly electricity bill",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "demo-user-1",
            "biller_name": "State Farm Insurance", 
            "account_number": "INS-789012",
            "amount": 234.50,
            "due_date": datetime.now(timezone.utc) + timedelta(days=20),
            "status": "pending",
            "bill_type": "insurance",
            "description": "Auto insurance premium",
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "demo-user-1",
            "biller_name": "NYC Parking Authority",
            "account_number": "PARK-345678",
            "amount": 45.00,
            "due_date": datetime.now(timezone.utc) - timedelta(days=2),
            "status": "overdue",
            "bill_type": "government",
            "description": "Parking ticket fine",
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    # Clear existing demo bills and insert new ones
    await db.bills.delete_many({"user_id": "demo-user-1"})
    for bill in demo_bills:
        await db.bills.insert_one(prepare_for_mongo(bill))
    print(f"Created {len(demo_bills)} demo bills")
    
    # Create demo payment methods for first user
    demo_payment_methods = [
        {
            "id": str(uuid.uuid4()),
            "user_id": "demo-user-1",
            "type": "credit_card",
            "last4": "4567",
            "brand": "Visa",
            "expiry_month": 12,
            "expiry_year": 2025,
            "bank_name": None,
            "account_type": None,
            "bitcoin_address": None,
            "is_default": True,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "demo-user-1",
            "type": "bank_account",
            "last4": "8901",
            "brand": None,
            "expiry_month": None,
            "expiry_year": None,
            "bank_name": "Chase Bank",
            "account_type": "checking",
            "bitcoin_address": None,
            "is_default": False,
            "created_at": datetime.now(timezone.utc)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "demo-user-1",
            "type": "bitcoin",
            "last4": None,
            "brand": None,
            "expiry_month": None,
            "expiry_year": None,
            "bank_name": None,
            "account_type": None,
            "bitcoin_address": "bc1q4y49r0x3v8kevysagjkjfesxgfnfqjd2rp0c90",
            "is_default": False,
            "created_at": datetime.now(timezone.utc)
        }
    ]
    
    # Clear existing demo payment methods and insert new ones
    await db.payment_methods.delete_many({"user_id": "demo-user-1"})
    for method in demo_payment_methods:
        await db.payment_methods.insert_one(prepare_for_mongo(method))
    print(f"Created {len(demo_payment_methods)} demo payment methods")
    
    # Create some demo transactions
    demo_transactions = [
        {
            "id": str(uuid.uuid4()),
            "user_id": "demo-user-1",
            "bill_id": "dummy-bill-1",
            "amount": 89.99,
            "payment_method_id": demo_payment_methods[0]["id"],
            "confirmation_number": "PAY1A2B3C",
            "status": "completed",
            "timestamp": datetime.now(timezone.utc) - timedelta(days=5)
        },
        {
            "id": str(uuid.uuid4()),
            "user_id": "demo-user-1", 
            "bill_id": "dummy-bill-2",
            "amount": 125.50,
            "payment_method_id": demo_payment_methods[1]["id"],
            "confirmation_number": "PAY4D5E6F",
            "status": "completed",
            "timestamp": datetime.now(timezone.utc) - timedelta(days=12)
        }
    ]
    
    # Clear existing demo transactions and insert new ones
    await db.transactions.delete_many({"user_id": "demo-user-1"})
    for txn in demo_transactions:
        await db.transactions.insert_one(prepare_for_mongo(txn))
    print(f"Created {len(demo_transactions)} demo transactions")
    
    print("Demo data setup complete!")

if __name__ == "__main__":
    asyncio.run(setup_demo_data())