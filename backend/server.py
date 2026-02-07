from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
import os
import logging
import uuid
import stripe
import secrets

# Load environment variables
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT_DIR, '.env'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security configuration - using pbkdf2_sha256 instead of bcrypt to avoid 72-byte limit issues
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
SECRET_KEY = os.environ.get("JWT_SECRET", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24  # 30 days

# Stripe configuration with emergentintegrations
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

stripe_api_key = os.environ.get("STRIPE_API_KEY", "sk_test_emergent")

# Create FastAPI app
app = FastAPI(title="Paymentus Clone API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Pydantic Models
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=1)
    phone: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class BillCreate(BaseModel):
    biller_name: str
    account_number: str
    amount: float = Field(..., gt=0)
    due_date: datetime
    bill_type: str = Field(..., pattern="^(utility|telecom|insurance|government)$")
    description: Optional[str] = None

class Bill(BaseModel):
    id: str
    user_id: str
    biller_name: str
    account_number: str
    amount: float
    due_date: datetime
    status: str  # pending, paid, overdue
    bill_type: str
    description: Optional[str] = None
    created_at: datetime

class PaymentMethodCreate(BaseModel):
    type: str = Field(..., pattern="^(credit_card|bank_account|bitcoin)$")
    card_number: Optional[str] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    cvv: Optional[str] = None
    bank_name: Optional[str] = None
    account_type: Optional[str] = None
    bitcoin_address: Optional[str] = None
    is_default: bool = False

class PaymentMethod(BaseModel):
    id: str
    user_id: str
    type: str
    last4: Optional[str] = None
    brand: Optional[str] = None
    expiry_month: Optional[int] = None
    expiry_year: Optional[int] = None
    bank_name: Optional[str] = None
    account_type: Optional[str] = None
    bitcoin_address: Optional[str] = None
    is_default: bool
    created_at: datetime

class PaymentRequest(BaseModel):
    bill_id: str
    payment_method_id: str
    amount: float = Field(..., gt=0)

class Transaction(BaseModel):
    id: str
    user_id: str
    bill_id: str
    amount: float
    payment_method_id: str
    confirmation_number: str
    status: str  # processing, completed, failed
    timestamp: datetime

class DashboardMetrics(BaseModel):
    total_due: float
    next_due_date: Optional[datetime]
    monthly_total: float
    method_count: int
    recent_transactions: List[Transaction]

class LightningInvoice(BaseModel):
    payment_hash: str
    payment_request: str
    amount_sat: int
    amount_usd: float
    expires_at: datetime
    memo: str

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"id": user_id})
    if user is None:
        raise credentials_exception
    
    return User(**user)

def prepare_for_mongo(data):
    """Prepare data for MongoDB insertion by converting dates to ISO strings"""
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, datetime):
                data[key] = value.isoformat()
    return data

def parse_from_mongo(item):
    """Parse data from MongoDB by converting ISO strings back to datetime objects"""
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str) and key in ['created_at', 'updated_at', 'due_date', 'timestamp', 'expires_at']:
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    pass
    return item

# Routes
api_router = APIRouter(prefix="/api")

@api_router.get("/")
async def root():
    return {"message": "Paymentus Clone API", "version": "1.0.0"}

@api_router.get("/status")
async def get_status():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

# Authentication routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_create: UserCreate):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_create.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_create.password)
    user_data = {
        "id": user_id,
        "email": user_create.email,
        "password": hashed_password,
        "name": user_create.name,
        "phone": user_create.phone,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    await db.users.insert_one(prepare_for_mongo(user_data))
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )
    
    user = User(
        id=user_id,
        email=user_create.email,
        name=user_create.name,
        phone=user_create.phone,
        created_at=datetime.now(timezone.utc)
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    user_data = await db.users.find_one({"email": user_login.email})
    if not user_data or not verify_password(user_login.password, user_data["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["id"]}, expires_delta=access_token_expires
    )
    
    user = User(**parse_from_mongo(user_data))
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.post("/auth/logout")
async def logout():
    return {"message": "Successfully logged out"}

# Bills management
@api_router.get("/bills", response_model=List[Bill])
async def get_bills(current_user: User = Depends(get_current_user)):
    bills = await db.bills.find({"user_id": current_user.id}).to_list(1000)
    return [Bill(**parse_from_mongo(bill)) for bill in bills]

@api_router.post("/bills", response_model=Bill)
async def create_bill(bill_create: BillCreate, current_user: User = Depends(get_current_user)):
    bill_id = str(uuid.uuid4())
    bill_data = {
        "id": bill_id,
        "user_id": current_user.id,
        **bill_create.dict(),
        "status": "pending",
        "created_at": datetime.now(timezone.utc),
    }
    
    await db.bills.insert_one(prepare_for_mongo(bill_data))
    return Bill(**parse_from_mongo(bill_data))

@api_router.put("/bills/{bill_id}", response_model=Bill)
async def update_bill(bill_id: str, bill_update: dict, current_user: User = Depends(get_current_user)):
    bill = await db.bills.find_one({"id": bill_id, "user_id": current_user.id})
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    update_data = prepare_for_mongo(bill_update)
    await db.bills.update_one({"id": bill_id}, {"$set": update_data})
    
    updated_bill = await db.bills.find_one({"id": bill_id})
    return Bill(**parse_from_mongo(updated_bill))

@api_router.delete("/bills/{bill_id}")
async def delete_bill(bill_id: str, current_user: User = Depends(get_current_user)):
    result = await db.bills.delete_one({"id": bill_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Bill not found")
    return {"message": "Bill deleted successfully"}

# Payment methods management
@api_router.get("/payment-methods", response_model=List[PaymentMethod])
async def get_payment_methods(current_user: User = Depends(get_current_user)):
    methods = await db.payment_methods.find({"user_id": current_user.id}).to_list(1000)
    return [PaymentMethod(**parse_from_mongo(method)) for method in methods]

@api_router.post("/payment-methods", response_model=PaymentMethod)
async def create_payment_method(method_create: PaymentMethodCreate, current_user: User = Depends(get_current_user)):
    method_id = str(uuid.uuid4())
    
    # Extract last 4 digits for cards
    last4 = None
    if method_create.type == "credit_card" and method_create.card_number:
        last4 = method_create.card_number[-4:]
    
    method_data = {
        "id": method_id,
        "user_id": current_user.id,
        "type": method_create.type,
        "last4": last4,
        "brand": "Visa" if method_create.card_number and method_create.card_number.startswith('4') else "Mastercard",
        "expiry_month": method_create.expiry_month,
        "expiry_year": method_create.expiry_year,
        "bank_name": method_create.bank_name,
        "account_type": method_create.account_type,
        "bitcoin_address": method_create.bitcoin_address,
        "is_default": method_create.is_default,
        "created_at": datetime.now(timezone.utc),
    }
    
    # If this is set as default, unset other defaults
    if method_create.is_default:
        await db.payment_methods.update_many(
            {"user_id": current_user.id},
            {"$set": {"is_default": False}}
        )
    
    await db.payment_methods.insert_one(prepare_for_mongo(method_data))
    return PaymentMethod(**parse_from_mongo(method_data))

@api_router.delete("/payment-methods/{method_id}")
async def delete_payment_method(method_id: str, current_user: User = Depends(get_current_user)):
    result = await db.payment_methods.delete_one({"id": method_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Payment method not found")
    return {"message": "Payment method deleted successfully"}

# Lightning Network endpoints
@api_router.post("/lightning/invoice", response_model=LightningInvoice)
async def create_lightning_invoice(amount_usd: float, memo: str, current_user: User = Depends(get_current_user)):
    # Simulate Lightning Network invoice creation
    # In production, this would integrate with actual Lightning Network daemon
    
    btc_usd_rate = 45000  # This should be fetched from a price API
    btc_amount = amount_usd / btc_usd_rate
    sat_amount = int(btc_amount * 100_000_000)  # Convert to satoshis
    
    payment_hash = secrets.token_hex(32)
    
    # Generate a realistic-looking Lightning invoice
    payment_request = f"lnbc{sat_amount}u1p{secrets.token_hex(25)}..."
    
    invoice_data = {
        "payment_hash": payment_hash,
        "payment_request": payment_request,
        "amount_sat": sat_amount,
        "amount_usd": amount_usd,
        "expires_at": datetime.now(timezone.utc) + timedelta(hours=1),
        "memo": memo,
    }
    
    return LightningInvoice(**invoice_data)

@api_router.post("/lightning/verify")
async def verify_lightning_payment(payment_hash: str, current_user: User = Depends(get_current_user)):
    # Simulate Lightning Network payment verification
    # In production, this would check actual Lightning Network daemon
    
    return {
        "payment_hash": payment_hash,
        "settled": True,  # Simulate successful payment for demo
        "amount_paid_sat": 1000,
        "settle_date": datetime.now(timezone.utc).timestamp(),
        "memo": "Payment verified"
    }

# Payment processing
@api_router.post("/payments/process", response_model=Transaction)
async def process_payment(payment_request: PaymentRequest, current_user: User = Depends(get_current_user)):
    # Get bill and payment method
    bill = await db.bills.find_one({"id": payment_request.bill_id, "user_id": current_user.id})
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
    
    payment_method = await db.payment_methods.find_one({
        "id": payment_request.payment_method_id,
        "user_id": current_user.id
    })
    if not payment_method:
        raise HTTPException(status_code=404, detail="Payment method not found")
    
    # Generate transaction
    transaction_id = str(uuid.uuid4())
    confirmation_number = f"PAY{secrets.token_hex(4).upper()}"
    
    transaction_data = {
        "id": transaction_id,
        "user_id": current_user.id,
        "bill_id": payment_request.bill_id,
        "amount": payment_request.amount,
        "payment_method_id": payment_request.payment_method_id,
        "confirmation_number": confirmation_number,
        "status": "completed",  # Simulate successful payment
        "timestamp": datetime.now(timezone.utc),
    }
    
    # Update bill status
    await db.bills.update_one(
        {"id": payment_request.bill_id},
        {"$set": {"status": "paid"}}
    )
    
    # Save transaction
    await db.transactions.insert_one(prepare_for_mongo(transaction_data))
    
    return Transaction(**parse_from_mongo(transaction_data))

@api_router.get("/payments/history", response_model=List[Transaction])
async def get_payment_history(current_user: User = Depends(get_current_user)):
    transactions = await db.transactions.find(
        {"user_id": current_user.id}
    ).sort("timestamp", -1).to_list(1000)
    
    return [Transaction(**parse_from_mongo(transaction)) for transaction in transactions]

# Dashboard metrics
@api_router.get("/dashboard/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics(current_user: User = Depends(get_current_user)):
    # Get pending bills
    pending_bills = await db.bills.find({
        "user_id": current_user.id,
        "status": "pending"
    }).to_list(1000)
    
    total_due = sum(bill["amount"] for bill in pending_bills)
    
    # Get next due date
    next_due_date = None
    if pending_bills:
        sorted_bills = sorted(pending_bills, key=lambda x: x["due_date"])
        next_due_date = datetime.fromisoformat(sorted_bills[0]["due_date"].replace('Z', '+00:00'))
    
    # Get monthly total (current month transactions)
    current_month_start = datetime.now(timezone.utc).replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_transactions = await db.transactions.find({
        "user_id": current_user.id,
        "timestamp": {"$gte": current_month_start.isoformat()}
    }).to_list(1000)
    
    monthly_total = sum(transaction["amount"] for transaction in monthly_transactions)
    
    # Get payment method count
    method_count = await db.payment_methods.count_documents({"user_id": current_user.id})
    
    # Get recent transactions (last 5)
    recent_transactions_data = await db.transactions.find(
        {"user_id": current_user.id}
    ).sort("timestamp", -1).limit(5).to_list(5)
    
    recent_transactions = [Transaction(**parse_from_mongo(t)) for t in recent_transactions_data]
    
    return DashboardMetrics(
        total_due=total_due,
        next_due_date=next_due_date,
        monthly_total=monthly_total,
        method_count=method_count,
        recent_transactions=recent_transactions
    )

# Enhanced Stripe Integration
async def get_stripe_checkout(request) -> StripeCheckout:
    """Initialize Stripe checkout with webhook URL"""
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhooks/stripe"
    return StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)

@api_router.post("/payments/stripe/checkout", response_model=CheckoutSessionResponse)
async def create_stripe_checkout(
    request: Request,
    checkout_request: CheckoutSessionRequest,
    current_user: User = Depends(get_current_user)
):
    """Create Stripe checkout session for bill payments"""
    try:
        stripe_checkout = await get_stripe_checkout(request)
        
        # Validate payment packages (server-side security)
        BILL_PAYMENT_PACKAGES = {
            "utility_payment": 5.00,
            "telecom_payment": 10.00, 
            "insurance_payment": 25.00,
            "government_payment": 15.00
        }
        
        # Enhanced metadata with user context
        enhanced_metadata = {
            **(checkout_request.metadata or {}),
            "user_id": current_user.id,
            "payment_type": "bill_payment",
            "platform": "paymentus_clone"
        }
        
        enhanced_request = CheckoutSessionRequest(
            amount=checkout_request.amount,
            currency=checkout_request.currency or "USD",
            stripe_price_id=checkout_request.stripe_price_id,
            quantity=checkout_request.quantity or 1,
            success_url=checkout_request.success_url,
            cancel_url=checkout_request.cancel_url,
            metadata=enhanced_metadata
        )
        
        session = await stripe_checkout.create_checkout_session(enhanced_request)
        
        # Store payment transaction
        transaction_id = str(uuid.uuid4())
        payment_transaction = {
            "id": transaction_id,
            "user_id": current_user.id,
            "session_id": session.session_id,
            "amount": checkout_request.amount or 0.0,
            "currency": checkout_request.currency or "USD",
            "payment_status": "initiated",
            "stripe_session_id": session.session_id,
            "metadata": enhanced_metadata,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.payment_transactions.insert_one(prepare_for_mongo(payment_transaction))
        
        return session
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create checkout: {str(e)}")

@api_router.get("/payments/stripe/status/{session_id}", response_model=CheckoutStatusResponse)
async def get_stripe_status(
    request: Request,
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get Stripe checkout status and update local records"""
    try:
        stripe_checkout = await get_stripe_checkout(request)
        status = await stripe_checkout.get_checkout_status(session_id)
        
        # Update local transaction record
        await db.payment_transactions.update_one(
            {"stripe_session_id": session_id, "user_id": current_user.id},
            {
                "$set": {
                    "payment_status": status.payment_status,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get payment status")

@api_router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Enhanced Stripe webhook handler"""
    try:
        stripe_checkout = await get_stripe_checkout(request)
        body = await request.body()
        signature = request.headers.get("stripe-signature", "")
        
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        if webhook_response.event_type == "checkout.session.completed":
            # Update payment status and create transaction record
            await db.payment_transactions.update_one(
                {"stripe_session_id": webhook_response.session_id},
                {
                    "$set": {
                        "payment_status": webhook_response.payment_status,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            # Create completed transaction for history
            if webhook_response.payment_status == "paid":
                transaction_data = await db.payment_transactions.find_one({
                    "stripe_session_id": webhook_response.session_id
                })
                
                if transaction_data:
                    completed_transaction = {
                        "id": str(uuid.uuid4()),
                        "user_id": transaction_data["user_id"],
                        "bill_id": "stripe_payment",
                        "amount": transaction_data["amount"],
                        "payment_method_id": "stripe",
                        "confirmation_number": f"STRIPE_{secrets.token_hex(6).upper()}",
                        "status": "completed",
                        "timestamp": datetime.now(timezone.utc)
                    }
                    
                    await db.transactions.insert_one(prepare_for_mongo(completed_transaction))
        
        return {"status": "success", "event_id": webhook_response.event_id}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail="Webhook processing failed")

# Include router
app.include_router(api_router)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)