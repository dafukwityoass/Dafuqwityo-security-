"""
Enhanced Production-Ready Paymentus Server with Financial Infrastructure
=====================================================================

This enhanced server implements comprehensive financial services including:
- Stripe payment processing with emergentintegrations
- Banking API integrations with security frameworks
- KYC/AML compliance monitoring
- Multi-signature Bitcoin wallet management
- Direct deposit and ACH processing
- Regulatory compliance and audit trails

Built for production deployment with appropriate legal and regulatory approval.
"""

from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, Request, BackgroundTasks
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
import secrets
import json

# Import Stripe integration from emergentintegrations
from emergentintegrations.payments.stripe.checkout import (
    StripeCheckout, 
    CheckoutSessionResponse, 
    CheckoutStatusResponse, 
    CheckoutSessionRequest
)

# Import financial infrastructure
from financial_infrastructure import (
    FinancialInfrastructure,
    ProductionConfig,
    SecurityConfig,
    TransactionType,
    TransactionStatus,
    KYCStatus,
    RiskLevel
)

# Load environment variables
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(ROOT_DIR, '.env'))

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('financial_services.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security configuration
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
SECRET_KEY = os.environ.get("JWT_SECRET", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30 * 24  # 30 days

# Stripe configuration
stripe_api_key = os.environ.get("STRIPE_API_KEY", "sk_test_emergent")

# Initialize Financial Infrastructure
production_config = ProductionConfig(
    environment=os.environ.get("ENVIRONMENT", "development"),
    plaid_client_id=os.environ.get("PLAID_CLIENT_ID", ""),
    plaid_secret=os.environ.get("PLAID_SECRET", ""),
    plaid_environment=os.environ.get("PLAID_ENV", "sandbox")
)

financial_infrastructure = FinancialInfrastructure(production_config)

# Create FastAPI app
app = FastAPI(
    title="Paymentus Financial Services Platform", 
    version="2.0.0",
    description="Production-ready financial services platform with comprehensive compliance and security"
)

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

# Enhanced Pydantic Models
class User(BaseModel):
    id: str
    email: str
    name: str
    phone: Optional[str] = None
    kyc_status: str = Field(default="not_started")
    risk_level: str = Field(default="low")
    created_at: datetime

class EnhancedTransaction(BaseModel):
    id: str
    user_id: str
    transaction_type: str
    amount: float
    currency: str = Field(default="USD")
    status: str
    risk_score: float = Field(default=0.0)
    compliance_flags: List[str] = Field(default_factory=list)
    confirmation_number: str
    timestamp: datetime

class PaymentTransaction(BaseModel):
    id: str
    user_id: str
    session_id: Optional[str] = None
    amount: float
    currency: str = Field(default="USD") 
    payment_status: str = Field(default="pending")
    stripe_session_id: Optional[str] = None
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

class DirectDepositRequest(BaseModel):
    employer_name: str
    routing_number: str = Field(..., min_length=9, max_length=9)
    account_number: str = Field(..., min_length=4)
    deposit_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    deposit_amount: Optional[float] = Field(None, ge=0.0)
    effective_date: datetime

class BankAccountLinkRequest(BaseModel):
    public_token: str = Field(..., description="Plaid public token")
    account_id: str = Field(..., description="Selected account ID")
    account_type: str = Field(..., regex="^(checking|savings)$")

class KYCDocumentUpload(BaseModel):
    document_type: str = Field(..., regex="^(drivers_license|passport|ssn_card|utility_bill|bank_statement)$")
    document_url: str
    document_data: Optional[Dict[str, Any]] = None

class MultisigWalletRequest(BaseModel):
    signers: List[str] = Field(..., min_items=2)
    required_signatures: int = Field(..., ge=2)
    wallet_purpose: str = Field(default="general")

class BitcoinTransferRequest(BaseModel):
    wallet_id: str
    destination_address: str = Field(..., regex="^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,62}$")
    amount_btc: float = Field(..., gt=0.0)
    memo: Optional[str] = None

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
    
    return User(**parse_from_mongo(user))

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
            if isinstance(value, str) and key in ['created_at', 'updated_at', 'due_date', 'timestamp', 'expires_at', 'effective_date']:
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    pass
    return item

# Initialize Stripe Checkout
async def get_stripe_checkout(request: Request) -> StripeCheckout:
    """Initialize Stripe checkout with webhook URL"""
    host_url = str(request.base_url).rstrip('/')
    webhook_url = f"{host_url}/api/webhooks/stripe"
    return StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)

# Routes
api_router = APIRouter(prefix="/api")

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize financial infrastructure on startup"""
    try:
        init_result = await financial_infrastructure.initialize()
        logger.info(f"Financial infrastructure initialized: {init_result['status']}")
    except Exception as e:
        logger.error(f"Failed to initialize financial infrastructure: {e}")
        raise

@api_router.get("/")
async def root():
    return {"message": "Paymentus Financial Services Platform", "version": "2.0.0"}

@api_router.get("/health")
async def health_check():
    """Comprehensive health check including financial services"""
    try:
        # Basic health
        basic_health = {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
        
        # Financial infrastructure health
        financial_health = await financial_infrastructure.health_check()
        
        return {
            **basic_health,
            "financial_services": financial_health
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy", 
            "error": str(e), 
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

# Authentication endpoints (inherited from original)
@api_router.post("/auth/register")
async def register(user_create: dict):
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_create["email"]})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user with enhanced financial profile
    user_id = str(uuid.uuid4())
    hashed_password = get_password_hash(user_create["password"])
    user_data = {
        "id": user_id,
        "email": user_create["email"],
        "password": hashed_password,
        "name": user_create["name"],
        "phone": user_create.get("phone"),
        "kyc_status": KYCStatus.NOT_STARTED,
        "risk_level": RiskLevel.LOW,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    
    await db.users.insert_one(prepare_for_mongo(user_data))
    
    # Initialize KYC process
    kyc_session = await financial_infrastructure.kyc_processor.initiate_kyc_process(
        user_id, 
        {"name": user_create["name"], "email": user_create["email"]}
    )
    
    # Log registration for audit
    await financial_infrastructure.audit_logger.log_financial_action(
        "user_registration",
        user_id,
        {"email": user_create["email"], "kyc_session": kyc_session["session_id"]}
    )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id}, expires_delta=access_token_expires
    )
    
    user = User(
        id=user_id,
        email=user_create["email"],
        name=user_create["name"],
        phone=user_create.get("phone"),
        kyc_status=KYCStatus.NOT_STARTED,
        risk_level=RiskLevel.LOW,
        created_at=datetime.now(timezone.utc)
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@api_router.post("/auth/login")
async def login(user_login: dict):
    user_data = await db.users.find_one({"email": user_login["email"]})
    if not user_data or not verify_password(user_login["password"], user_data["password"]):
        # Log failed login attempt
        await financial_infrastructure.audit_logger.log_financial_action(
            "login_failed",
            user_login["email"],
            {"reason": "invalid_credentials"}
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_data["id"]}, expires_delta=access_token_expires
    )
    
    # Log successful login
    await financial_infrastructure.audit_logger.log_financial_action(
        "login_successful",
        user_data["id"],
        {"email": user_login["email"]}
    )
    
    user = User(**parse_from_mongo(user_data))
    return {"access_token": access_token, "token_type": "bearer", "user": user}

# Enhanced Stripe Payment Processing
@api_router.post("/payments/checkout/session", response_model=CheckoutSessionResponse)
async def create_checkout_session(
    request: Request,
    checkout_request: CheckoutSessionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Create Stripe checkout session with comprehensive security and compliance"""
    
    try:
        stripe_checkout = await get_stripe_checkout(request)
        
        # Enhanced security: Server-side amount validation for fixed packages
        PAYMENT_PACKAGES = {
            "basic_bill_pay": 5.00,
            "premium_bill_pay": 15.00,
            "business_bill_pay": 50.00,
            "enterprise_bill_pay": 150.00
        }
        
        # If using fixed packages, validate against server-defined amounts
        if checkout_request.stripe_price_id and checkout_request.stripe_price_id in PAYMENT_PACKAGES:
            validated_amount = PAYMENT_PACKAGES[checkout_request.stripe_price_id]
        else:
            # For custom amounts, perform additional validation
            validated_amount = checkout_request.amount or 0.0
            if validated_amount <= 0:
                raise HTTPException(status_code=400, detail="Invalid payment amount")
        
        # Perform AML compliance check
        aml_result = await financial_infrastructure.ach_processor._perform_aml_check(
            current_user.id, 
            validated_amount, 
            "payment"
        )
        
        if aml_result["risk_level"] == RiskLevel.CRITICAL:
            raise HTTPException(
                status_code=403, 
                detail="Payment blocked for compliance reasons"
            )
        
        # Add compliance metadata
        enhanced_metadata = {
            **(checkout_request.metadata or {}),
            "user_id": current_user.id,
            "risk_score": str(aml_result["risk_score"]),
            "compliance_flags": ",".join(aml_result["flags"]),
            "payment_type": "bill_payment"
        }
        
        # Create enhanced checkout request
        enhanced_request = CheckoutSessionRequest(
            amount=validated_amount,
            currency=checkout_request.currency,
            stripe_price_id=checkout_request.stripe_price_id,
            quantity=checkout_request.quantity,
            success_url=checkout_request.success_url,
            cancel_url=checkout_request.cancel_url,
            metadata=enhanced_metadata
        )
        
        # Create Stripe session
        session = await stripe_checkout.create_checkout_session(enhanced_request)
        
        # Store payment transaction record
        transaction_id = str(uuid.uuid4())
        payment_transaction = PaymentTransaction(
            id=transaction_id,
            user_id=current_user.id,
            session_id=session.session_id,
            amount=validated_amount,
            currency=checkout_request.currency,
            payment_status="initiated",
            stripe_session_id=session.session_id,
            metadata=enhanced_metadata,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        await db.payment_transactions.insert_one(prepare_for_mongo(payment_transaction.dict()))
        
        # Log payment initiation for audit
        await financial_infrastructure.audit_logger.log_financial_action(
            "payment_initiated",
            current_user.id,
            {
                "transaction_id": transaction_id,
                "amount": validated_amount,
                "session_id": session.session_id,
                "risk_score": aml_result["risk_score"]
            }
        )
        
        logger.info(f"Checkout session created: {session.session_id} for user: {current_user.id}")
        return session
        
    except Exception as e:
        logger.error(f"Checkout session creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to create checkout session: {str(e)}")

@api_router.get("/payments/checkout/status/{session_id}", response_model=CheckoutStatusResponse)
async def get_checkout_status(
    request: Request,
    session_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    """Get checkout session status with transaction updates"""
    
    try:
        stripe_checkout = await get_stripe_checkout(request)
        
        # Get status from Stripe
        checkout_status = await stripe_checkout.get_checkout_status(session_id)
        
        # Find and update local transaction record
        transaction = await db.payment_transactions.find_one({
            "stripe_session_id": session_id,
            "user_id": current_user.id
        })
        
        if transaction:
            # Update payment status based on Stripe response
            update_data = {
                "payment_status": checkout_status.payment_status,
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.payment_transactions.update_one(
                {"id": transaction["id"]},
                {"$set": update_data}
            )
            
            # If payment completed, perform additional compliance and processing
            if checkout_status.payment_status == "paid" and transaction["payment_status"] != "paid":
                background_tasks.add_task(
                    process_successful_payment,
                    transaction["id"],
                    checkout_status
                )
        
        logger.info(f"Checkout status retrieved: {session_id} - {checkout_status.payment_status}")
        return checkout_status
        
    except Exception as e:
        logger.error(f"Failed to get checkout status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve payment status")

async def process_successful_payment(transaction_id: str, checkout_status: CheckoutStatusResponse):
    """Background task to process successful payment with compliance checks"""
    
    try:
        # Get transaction details
        transaction = await db.payment_transactions.find_one({"id": transaction_id})
        if not transaction:
            return
        
        # Create enhanced transaction record for compliance monitoring
        enhanced_transaction = {
            "id": str(uuid.uuid4()),
            "user_id": transaction["user_id"],
            "transaction_type": TransactionType.BILL_PAYMENT,
            "amount": checkout_status.amount_total / 100,  # Convert from cents
            "currency": checkout_status.currency.upper(),
            "status": TransactionStatus.COMPLETED,
            "risk_score": float(checkout_status.metadata.get("risk_score", "0")),
            "compliance_flags": checkout_status.metadata.get("compliance_flags", "").split(",") if checkout_status.metadata.get("compliance_flags") else [],
            "confirmation_number": f"PAY{secrets.token_hex(6).upper()}",
            "stripe_session_id": transaction["stripe_session_id"],
            "timestamp": datetime.now(timezone.utc)
        }
        
        # Store enhanced transaction
        await db.enhanced_transactions.insert_one(prepare_for_mongo(enhanced_transaction))
        
        # Perform post-payment compliance monitoring
        compliance_result = await financial_infrastructure.compliance_monitor.monitor_transaction({
            "transaction_id": enhanced_transaction["id"],
            "user_id": enhanced_transaction["user_id"],
            "transaction_type": enhanced_transaction["transaction_type"],
            "amount": enhanced_transaction["amount"],
            "risk_score": enhanced_transaction["risk_score"]
        })
        
        # Log successful payment for audit
        await financial_infrastructure.audit_logger.log_financial_action(
            "payment_completed",
            transaction["user_id"],
            {
                "transaction_id": enhanced_transaction["id"],
                "amount": enhanced_transaction["amount"],
                "compliance_status": compliance_result["compliance_status"],
                "confirmation_number": enhanced_transaction["confirmation_number"]
            }
        )
        
        logger.info(f"Payment processed successfully: {enhanced_transaction['id']}")
        
    except Exception as e:
        logger.error(f"Failed to process successful payment: {e}")

@api_router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    """Handle Stripe webhooks for payment status updates"""
    
    try:
        stripe_checkout = await get_stripe_checkout(request)
        
        # Get webhook payload
        body = await request.body()
        signature = request.headers.get("stripe-signature", "")
        
        # Handle webhook
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Process webhook event
        if webhook_response.event_type == "checkout.session.completed":
            # Update transaction status
            await db.payment_transactions.update_one(
                {"stripe_session_id": webhook_response.session_id},
                {
                    "$set": {
                        "payment_status": webhook_response.payment_status,
                        "updated_at": datetime.now(timezone.utc).isoformat()
                    }
                }
            )
            
            logger.info(f"Webhook processed: {webhook_response.event_id}")
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Webhook processing failed: {e}")
        raise HTTPException(status_code=400, detail="Webhook processing failed")

# Banking Integration Endpoints
@api_router.post("/banking/link-account")
async def link_bank_account(
    link_request: BankAccountLinkRequest,
    current_user: User = Depends(get_current_user)
):
    """Link bank account using Plaid integration"""
    
    try:
        # Exchange public token for access token
        token_exchange = await financial_infrastructure.plaid.exchange_public_token(
            link_request.public_token
        )
        
        # Get account details
        accounts = await financial_infrastructure.plaid.get_accounts(
            token_exchange["access_token"]
        )
        
        # Find selected account
        selected_account = None
        for account in accounts:
            if account["account_id"] == link_request.account_id:
                selected_account = account
                break
        
        if not selected_account:
            raise HTTPException(status_code=404, detail="Selected account not found")
        
        # Encrypt and store account information
        account_id = str(uuid.uuid4())
        encrypted_account_number = financial_infrastructure.security.encrypt_sensitive_data(
            selected_account["mask"]
        )
        
        bank_account = {
            "id": account_id,
            "user_id": current_user.id,
            "plaid_account_id": selected_account["account_id"],
            "plaid_access_token": financial_infrastructure.security.encrypt_sensitive_data(
                token_exchange["access_token"]
            ),
            "account_type": link_request.account_type,
            "bank_name": selected_account.get("institution_name", "Unknown Bank"),
            "account_mask": selected_account["mask"],
            "encrypted_account_number": encrypted_account_number,
            "balance": selected_account["balances"]["current"],
            "verification_status": "linked",
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.bank_accounts.insert_one(prepare_for_mongo(bank_account))
        
        # Initiate micro deposits for verification
        micro_deposit_result = await financial_infrastructure.plaid.initiate_micro_deposits(
            token_exchange["access_token"],
            selected_account["account_id"]
        )
        
        # Log account linking for audit
        await financial_infrastructure.audit_logger.log_financial_action(
            "bank_account_linked",
            current_user.id,
            {
                "account_id": account_id,
                "bank_name": bank_account["bank_name"],
                "account_type": link_request.account_type,
                "micro_deposit_id": micro_deposit_result["micro_deposit_id"]
            }
        )
        
        return {
            "account_id": account_id,
            "status": "linked",
            "verification_status": "micro_deposits_initiated",
            "micro_deposit_info": micro_deposit_result
        }
        
    except Exception as e:
        logger.error(f"Bank account linking failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to link bank account")

@api_router.post("/banking/direct-deposit")
async def setup_direct_deposit(
    deposit_request: DirectDepositRequest,
    current_user: User = Depends(get_current_user)
):
    """Setup direct deposit for user"""
    
    try:
        # Create direct deposit setup
        deposit_setup = await financial_infrastructure.ach_processor.initiate_direct_deposit({
            "user_id": current_user.id,
            "employer_name": deposit_request.employer_name,
            "routing_number": deposit_request.routing_number,
            "account_number": deposit_request.account_number,
            "deposit_percentage": deposit_request.deposit_percentage,
            "deposit_amount": deposit_request.deposit_amount,
            "effective_date": deposit_request.effective_date
        })
        
        # Store direct deposit configuration
        deposit_id = str(uuid.uuid4())
        direct_deposit_config = {
            "id": deposit_id,
            "user_id": current_user.id,
            "employer_name": deposit_request.employer_name,
            "routing_number": deposit_request.routing_number,
            "encrypted_account_number": financial_infrastructure.security.encrypt_sensitive_data(
                deposit_request.account_number
            ),
            "deposit_percentage": deposit_request.deposit_percentage,
            "deposit_amount": deposit_request.deposit_amount,
            "effective_date": deposit_request.effective_date,
            "status": "pending_setup",
            "ach_transaction_id": deposit_setup["transaction_id"],
            "created_at": datetime.now(timezone.utc)
        }
        
        await db.direct_deposits.insert_one(prepare_for_mongo(direct_deposit_config))
        
        # Log direct deposit setup for audit
        await financial_infrastructure.audit_logger.log_financial_action(
            "direct_deposit_setup",
            current_user.id,
            {
                "deposit_id": deposit_id,
                "employer": deposit_request.employer_name,
                "effective_date": deposit_request.effective_date.isoformat()
            },
            {
                "routing_number": deposit_request.routing_number,
                "account_number": deposit_request.account_number
            }
        )
        
        return {
            "deposit_id": deposit_id,
            "status": "setup_initiated",
            "effective_date": deposit_request.effective_date,
            "ach_transaction": deposit_setup
        }
        
    except Exception as e:
        logger.error(f"Direct deposit setup failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to setup direct deposit")

# Bitcoin/Cryptocurrency Endpoints
@api_router.post("/crypto/wallet/create")
async def create_multisig_wallet(
    wallet_request: MultisigWalletRequest,
    current_user: User = Depends(get_current_user)
):
    """Create multi-signature Bitcoin wallet"""
    
    try:
        # Validate that current user is included in signers
        if current_user.id not in wallet_request.signers:
            raise HTTPException(status_code=400, detail="User must be included as a signer")
        
        # Create multisig wallet
        wallet = await financial_infrastructure.multisig_manager.create_multisig_wallet(
            wallet_request.signers,
            wallet_request.required_signatures
        )
        
        # Store wallet configuration
        wallet_config = {
            **wallet.dict(),
            "wallet_purpose": wallet_request.wallet_purpose,
            "creator_id": current_user.id
        }
        
        await db.multisig_wallets.insert_one(prepare_for_mongo(wallet_config))
        
        # Log wallet creation for audit
        await financial_infrastructure.audit_logger.log_financial_action(
            "multisig_wallet_created",
            current_user.id,
            {
                "wallet_id": wallet.wallet_id,
                "wallet_address": wallet.wallet_address,
                "signers_count": len(wallet_request.signers),
                "required_signatures": wallet_request.required_signatures
            }
        )
        
        return wallet
        
    except Exception as e:
        logger.error(f"Multisig wallet creation failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to create multisig wallet")

@api_router.post("/crypto/transfer")
async def initiate_bitcoin_transfer(
    transfer_request: BitcoinTransferRequest,
    current_user: User = Depends(get_current_user)
):
    """Initiate Bitcoin transfer from multisig wallet"""
    
    try:
        # Verify wallet access
        wallet = await db.multisig_wallets.find_one({
            "wallet_id": transfer_request.wallet_id,
            "signers": {"$in": [current_user.id]},
            "is_active": True
        })
        
        if not wallet:
            raise HTTPException(status_code=404, detail="Wallet not found or access denied")
        
        # Initiate multisig transaction
        transaction = await financial_infrastructure.multisig_manager.initiate_transaction(
            transfer_request.wallet_id,
            transfer_request.amount_btc,
            transfer_request.destination_address,
            current_user.id
        )
        
        # Store transaction record
        await db.bitcoin_transactions.insert_one(prepare_for_mongo(transaction))
        
        # Log Bitcoin transfer initiation
        await financial_infrastructure.audit_logger.log_financial_action(
            "bitcoin_transfer_initiated",
            current_user.id,
            {
                "transaction_id": transaction["transaction_id"],
                "wallet_id": transfer_request.wallet_id,
                "amount_btc": transfer_request.amount_btc,
                "destination_address": transfer_request.destination_address
            }
        )
        
        return {
            "transaction_id": transaction["transaction_id"],
            "status": transaction["status"],
            "signatures_required": transaction["signatures_required"],
            "expires_at": transaction["expires_at"]
        }
        
    except Exception as e:
        logger.error(f"Bitcoin transfer failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate Bitcoin transfer")

# KYC/Compliance Endpoints
@api_router.post("/kyc/upload-document")
async def upload_kyc_document(
    document_upload: KYCDocumentUpload,
    current_user: User = Depends(get_current_user)
):
    """Upload KYC document for verification"""
    
    try:
        # Create KYC document record
        document_id = str(uuid.uuid4())
        kyc_document = {
            "document_id": document_id,
            "user_id": current_user.id,
            "document_type": document_upload.document_type,
            "document_url": financial_infrastructure.security.encrypt_sensitive_data(
                document_upload.document_url
            ),
            "upload_date": datetime.now(timezone.utc),
            "verification_status": "pending",
            "extracted_data": document_upload.document_data,
            "confidence_score": None
        }
        
        # Submit for KYC processing
        verification_result = await financial_infrastructure.kyc_processor.submit_kyc_document(
            "kyc_session_id",  # Would be retrieved from user's KYC session
            kyc_document
        )
        
        # Update document with verification results
        kyc_document.update({
            "verification_status": verification_result["verification_status"],
            "confidence_score": verification_result["confidence_score"],
            "extracted_data": verification_result["extracted_data"],
            "processed_at": verification_result["processed_at"]
        })
        
        await db.kyc_documents.insert_one(prepare_for_mongo(kyc_document))
        
        # Log KYC document upload
        await financial_infrastructure.audit_logger.log_financial_action(
            "kyc_document_uploaded",
            current_user.id,
            {
                "document_id": document_id,
                "document_type": document_upload.document_type,
                "verification_status": verification_result["verification_status"]
            }
        )
        
        return verification_result
        
    except Exception as e:
        logger.error(f"KYC document upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload KYC document")

@api_router.get("/compliance/status")
async def get_compliance_status(current_user: User = Depends(get_current_user)):
    """Get user's compliance and KYC status"""
    
    try:
        # Get KYC documents
        kyc_documents = await db.kyc_documents.find(
            {"user_id": current_user.id}
        ).to_list(100)
        
        # Get recent transactions for compliance review
        recent_transactions = await db.enhanced_transactions.find(
            {"user_id": current_user.id}
        ).sort("timestamp", -1).limit(10).to_list(10)
        
        # Calculate compliance score
        compliance_score = 100.0
        compliance_issues = []
        
        # Check KYC completion
        required_docs = ["drivers_license", "utility_bill"]
        submitted_docs = [doc["document_type"] for doc in kyc_documents if doc["verification_status"] == "verified"]
        missing_docs = set(required_docs) - set(submitted_docs)
        
        if missing_docs:
            compliance_score -= len(missing_docs) * 20
            compliance_issues.extend([f"Missing {doc}" for doc in missing_docs])
        
        # Check for compliance flags in transactions
        flagged_transactions = [t for t in recent_transactions if t.get("compliance_flags")]
        if flagged_transactions:
            compliance_score -= len(flagged_transactions) * 5
            compliance_issues.append(f"{len(flagged_transactions)} flagged transactions")
        
        compliance_status = {
            "user_id": current_user.id,
            "kyc_status": current_user.kyc_status,
            "risk_level": current_user.risk_level,
            "compliance_score": max(0, compliance_score),
            "compliance_issues": compliance_issues,
            "kyc_documents": len(kyc_documents),
            "verified_documents": len(submitted_docs),
            "recent_transactions": len(recent_transactions),
            "flagged_transactions": len(flagged_transactions),
            "last_updated": datetime.now(timezone.utc)
        }
        
        return compliance_status
        
    except Exception as e:
        logger.error(f"Failed to get compliance status: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve compliance status")

# Include all routers
app.include_router(api_router)

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return {"error": "Internal server error", "detail": str(exc)}

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)