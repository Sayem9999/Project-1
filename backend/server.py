from fastapi import FastAPI, APIRouter, HTTPException, Request, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict
import uuid
from datetime import datetime, timezone, timedelta
import bcrypt
import jwt
from emergentintegrations.payments.stripe.checkout import StripeCheckout, CheckoutSessionResponse, CheckoutStatusResponse, CheckoutSessionRequest

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Stripe setup
stripe_api_key = os.environ.get('STRIPE_API_KEY')

# JWT Secret
JWT_SECRET = os.environ.get('JWT_SECRET', 'nilam-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'

app = FastAPI()
api_router = APIRouter(prefix="/api")

# ============ MODELS ============

class UserRegister(BaseModel):
    email: str
    password: str
    username: str

class UserLogin(BaseModel):
    email: str
    password: str

class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    username: str
    avatar_url: Optional[str] = None
    rating_score: float = 0.0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ListingCreate(BaseModel):
    title: str
    description: str
    category: str
    condition: str  # New, Used, Refurbished
    listing_type: str  # auction or buy_now
    starting_price: Optional[float] = None
    buy_now_price: Optional[float] = None
    duration_hours: Optional[int] = 24  # For auctions
    images: List[str] = []

class Listing(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    seller_id: str
    seller_username: str
    title: str
    description: str
    category: str
    condition: str
    listing_type: str
    starting_price: Optional[float] = None
    current_price: float = 0.0
    buy_now_price: Optional[float] = None
    images: List[str] = []
    status: str = "active"  # active, sold, expired
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ends_at: Optional[datetime] = None
    bid_count: int = 0
    winner_id: Optional[str] = None

class BidCreate(BaseModel):
    listing_id: str
    amount: float

class Bid(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    listing_id: str
    bidder_id: str
    bidder_username: str
    amount: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WatchlistItem(BaseModel):
    user_id: str
    listing_id: str

# ============ AUTH HELPERS ============

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_token(user_id: str, email: str) -> str:
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.now(timezone.utc) + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except:
        return None

async def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.split(' ')[1]
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

# ============ AUTH ROUTES ============

@api_router.post("/auth/register")
async def register(user_input: UserRegister):
    # Check if user exists
    existing = await db.users.find_one({"email": user_input.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user_dict = user_input.model_dump()
    hashed = hash_password(user_dict.pop('password'))
    user_obj = User(**user_dict)
    
    doc = user_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['password_hash'] = hashed
    
    await db.users.insert_one(doc)
    
    token = create_token(user_obj.id, user_obj.email)
    return {"token": token, "user": user_obj}

@api_router.post("/auth/login")
async def login(user_input: UserLogin):
    user = await db.users.find_one({"email": user_input.email}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not verify_password(user_input.password, user['password_hash']):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user.pop('password_hash', None)
    if isinstance(user['created_at'], str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])
    
    token = create_token(user['id'], user['email'])
    return {"token": token, "user": User(**user)}

@api_router.get("/auth/me")
async def get_me(authorization: Optional[str] = Header(None)):
    current_user = await get_current_user(authorization)
    user = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if isinstance(user['created_at'], str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])
    return User(**user)

# ============ LISTING ROUTES ============

@api_router.post("/listings", response_model=Listing)
async def create_listing(listing_input: ListingCreate, authorization: Optional[str] = Header(None)):
    current_user = await get_current_user(authorization)
    user = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0})
    
    listing_dict = listing_input.model_dump()
    listing_obj = Listing(
        **listing_dict,
        seller_id=current_user['user_id'],
        seller_username=user['username']
    )
    
    if listing_obj.listing_type == 'auction':
        listing_obj.current_price = listing_obj.starting_price or 0.0
        listing_obj.ends_at = datetime.now(timezone.utc) + timedelta(hours=listing_input.duration_hours or 24)
    else:
        listing_obj.current_price = listing_obj.buy_now_price or 0.0
    
    doc = listing_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    if doc['ends_at']:
        doc['ends_at'] = doc['ends_at'].isoformat()
    
    await db.listings.insert_one(doc)
    return listing_obj

@api_router.get("/listings", response_model=List[Listing])
async def get_listings(category: Optional[str] = None, status: str = "active", search: Optional[str] = None):
    query = {"status": status}
    if category:
        query["category"] = category
    if search:
        query["title"] = {"$regex": search, "$options": "i"}
    
    listings = await db.listings.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    for listing in listings:
        if isinstance(listing['created_at'], str):
            listing['created_at'] = datetime.fromisoformat(listing['created_at'])
        if listing.get('ends_at') and isinstance(listing['ends_at'], str):
            listing['ends_at'] = datetime.fromisoformat(listing['ends_at'])
    
    return listings

@api_router.get("/listings/{listing_id}", response_model=Listing)
async def get_listing(listing_id: str):
    listing = await db.listings.find_one({"id": listing_id}, {"_id": 0})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if isinstance(listing['created_at'], str):
        listing['created_at'] = datetime.fromisoformat(listing['created_at'])
    if listing.get('ends_at') and isinstance(listing['ends_at'], str):
        listing['ends_at'] = datetime.fromisoformat(listing['ends_at'])
    
    return Listing(**listing)

# ============ BIDDING ROUTES ============

@api_router.post("/bids", response_model=Bid)
async def place_bid(bid_input: BidCreate, authorization: Optional[str] = Header(None)):
    current_user = await get_current_user(authorization)
    user = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0})
    
    # Get listing
    listing = await db.listings.find_one({"id": bid_input.listing_id}, {"_id": 0})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing['status'] != 'active':
        raise HTTPException(status_code=400, detail="Listing is not active")
    
    if listing['listing_type'] != 'auction':
        raise HTTPException(status_code=400, detail="This is not an auction listing")
    
    # Check if auction ended
    if listing.get('ends_at'):
        ends_at = datetime.fromisoformat(listing['ends_at']) if isinstance(listing['ends_at'], str) else listing['ends_at']
        if ends_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Auction has ended")
    
    # Validate bid amount
    current_price = listing.get('current_price', listing.get('starting_price', 0.0))
    if bid_input.amount <= current_price:
        raise HTTPException(status_code=400, detail=f"Bid must be higher than current price of ${current_price}")
    
    # Create bid
    bid_obj = Bid(
        listing_id=bid_input.listing_id,
        bidder_id=current_user['user_id'],
        bidder_username=user['username'],
        amount=bid_input.amount
    )
    
    bid_doc = bid_obj.model_dump()
    bid_doc['timestamp'] = bid_doc['timestamp'].isoformat()
    await db.bids.insert_one(bid_doc)
    
    # Update listing
    await db.listings.update_one(
        {"id": bid_input.listing_id},
        {
            "$set": {"current_price": bid_input.amount},
            "$inc": {"bid_count": 1}
        }
    )
    
    return bid_obj

@api_router.get("/bids/{listing_id}", response_model=List[Bid])
async def get_listing_bids(listing_id: str):
    bids = await db.bids.find({"listing_id": listing_id}, {"_id": 0}).sort("timestamp", -1).to_list(100)
    
    for bid in bids:
        if isinstance(bid['timestamp'], str):
            bid['timestamp'] = datetime.fromisoformat(bid['timestamp'])
    
    return bids

@api_router.get("/users/{user_id}/bids", response_model=List[Bid])
async def get_user_bids(user_id: str):
    bids = await db.bids.find({"bidder_id": user_id}, {"_id": 0}).sort("timestamp", -1).to_list(100)
    
    for bid in bids:
        if isinstance(bid['timestamp'], str):
            bid['timestamp'] = datetime.fromisoformat(bid['timestamp'])
    
    return bids

# ============ WATCHLIST ROUTES ============

@api_router.post("/watchlist")
async def add_to_watchlist(item: WatchlistItem, authorization: Optional[str] = Header(None)):
    current_user = await get_current_user(authorization)
    
    existing = await db.watchlist.find_one({
        "user_id": current_user['user_id'],
        "listing_id": item.listing_id
    }, {"_id": 0})
    
    if existing:
        return {"message": "Already in watchlist"}
    
    await db.watchlist.insert_one({
        "user_id": current_user['user_id'],
        "listing_id": item.listing_id
    })
    
    return {"message": "Added to watchlist"}

@api_router.delete("/watchlist/{listing_id}")
async def remove_from_watchlist(listing_id: str, authorization: Optional[str] = Header(None)):
    current_user = await get_current_user(authorization)
    
    await db.watchlist.delete_one({
        "user_id": current_user['user_id'],
        "listing_id": listing_id
    })
    
    return {"message": "Removed from watchlist"}

@api_router.get("/watchlist", response_model=List[str])
async def get_watchlist(authorization: Optional[str] = Header(None)):
    current_user = await get_current_user(authorization)
    
    items = await db.watchlist.find({"user_id": current_user['user_id']}, {"_id": 0}).to_list(100)
    return [item['listing_id'] for item in items]

# ============ USER LISTINGS ============

@api_router.get("/users/me/listings", response_model=List[Listing])
async def get_my_listings(authorization: Optional[str] = Header(None)):
    current_user = await get_current_user(authorization)
    
    listings = await db.listings.find({"seller_id": current_user['user_id']}, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    for listing in listings:
        if isinstance(listing['created_at'], str):
            listing['created_at'] = datetime.fromisoformat(listing['created_at'])
        if listing.get('ends_at') and isinstance(listing['ends_at'], str):
            listing['ends_at'] = datetime.fromisoformat(listing['ends_at'])
    
    return listings

# ============ STRIPE PAYMENT ROUTES ============

@api_router.post("/payments/checkout")
async def create_checkout(request: Request, authorization: Optional[str] = Header(None)):
    current_user = await get_current_user(authorization)
    body = await request.json()
    
    listing_id = body.get('listing_id')
    origin_url = body.get('origin_url')
    
    if not listing_id or not origin_url:
        raise HTTPException(status_code=400, detail="listing_id and origin_url required")
    
    # Get listing
    listing = await db.listings.find_one({"id": listing_id}, {"_id": 0})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing['status'] != 'active':
        raise HTTPException(status_code=400, detail="Listing is not active")
    
    # Determine amount
    amount = listing.get('buy_now_price') or listing.get('current_price', 0.0)
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid listing price")
    
    # Create Stripe checkout
    host_url = origin_url
    webhook_url = f"{origin_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    success_url = f"{host_url}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&listing_id={listing_id}"
    cancel_url = f"{host_url}/listings/{listing_id}"
    
    checkout_request = CheckoutSessionRequest(
        amount=amount,
        currency="usd",
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={
            "listing_id": listing_id,
            "buyer_id": current_user['user_id'],
            "seller_id": listing['seller_id']
        }
    )
    
    session = await stripe_checkout.create_checkout_session(checkout_request)
    
    # Create payment transaction record
    payment_doc = {
        "session_id": session.session_id,
        "listing_id": listing_id,
        "buyer_id": current_user['user_id'],
        "seller_id": listing['seller_id'],
        "amount": amount,
        "currency": "usd",
        "payment_status": "pending",
        "status": "initiated",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
    
    await db.payment_transactions.insert_one(payment_doc)
    
    return {"url": session.url, "session_id": session.session_id}

@api_router.get("/payments/status/{session_id}")
async def get_payment_status(session_id: str, authorization: Optional[str] = Header(None)):
    current_user = await get_current_user(authorization)
    
    # Check database first
    payment = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    # If already processed, return cached status
    if payment['payment_status'] == 'paid':
        return payment
    
    # Poll Stripe
    host_url = str(os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001'))
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    checkout_status = await stripe_checkout.get_checkout_status(session_id)
    
    # Update payment record
    update_data = {
        "payment_status": checkout_status.payment_status,
        "status": checkout_status.status
    }
    
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": update_data}
    )
    
    # If paid, mark listing as sold
    if checkout_status.payment_status == 'paid' and payment['payment_status'] != 'paid':
        await db.listings.update_one(
            {"id": payment['listing_id']},
            {"$set": {"status": "sold", "winner_id": payment['buyer_id']}}
        )
    
    payment.update(update_data)
    return payment

@api_router.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    body = await request.body()
    signature = request.headers.get("Stripe-Signature")
    
    host_url = str(request.base_url)
    webhook_url = f"{host_url}api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    try:
        webhook_response = await stripe_checkout.handle_webhook(body, signature)
        
        # Update payment transaction
        if webhook_response.session_id:
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {
                    "payment_status": webhook_response.payment_status,
                    "status": webhook_response.event_type
                }}
            )
            
            # If paid, mark listing as sold
            if webhook_response.payment_status == 'paid':
                payment = await db.payment_transactions.find_one({"session_id": webhook_response.session_id}, {"_id": 0})
                if payment:
                    await db.listings.update_one(
                        {"id": payment['listing_id']},
                        {"$set": {"status": "sold", "winner_id": payment['buyer_id']}}
                    )
        
        return {"status": "success"}
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

# ============ ROOT ============

@api_router.get("/")
async def root():
    return {"message": "Nilam API"}

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()