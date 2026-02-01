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
from supabase import create_client, Client
from bkash_service import create_bkash_payment, execute_bkash_payment, query_bkash_payment, verify_bkash_webhook
from scheduler import start_scheduler, shutdown_scheduler

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Supabase connection
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_ANON_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

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
    total_ratings: int = 0
    bio: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ListingCreate(BaseModel):
    title: str
    description: str
    category: str
    condition: str
    listing_type: str
    starting_price: Optional[float] = None
    buy_now_price: Optional[float] = None
    duration_hours: Optional[int] = 24
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
    status: str = "active"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ends_at: Optional[datetime] = None
    bid_count: int = 0
    winner_id: Optional[str] = None
    views: int = 0

class BidCreate(BaseModel):
    listing_id: str
    amount: float
    is_proxy_bid: bool = False
    max_amount: Optional[float] = None

class Bid(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    listing_id: str
    bidder_id: str
    bidder_username: str
    amount: float
    is_proxy_bid: bool = False
    max_amount: Optional[float] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WatchlistItem(BaseModel):
    user_id: str
    listing_id: str

class UserRating(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rated_user_id: str
    rater_id: str
    rater_username: str
    rating: int
    comment: Optional[str] = None
    listing_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class RatingCreate(BaseModel):
    rated_user_id: str
    rating: int
    comment: Optional[str] = None
    listing_id: Optional[str] = None

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

# ============ PROXY BID HELPER ============

async def process_proxy_bids(listing_id: str, new_bid_amount: float, new_bidder_id: str):
    """Process proxy bids when a new bid is placed"""
    proxy_bids = await db.bids.find({
        "listing_id": listing_id,
        "is_proxy_bid": True,
        "bidder_id": {"$ne": new_bidder_id}
    }, {"_id": 0}).sort("max_amount", -1).to_list(100)
    
    for proxy_bid in proxy_bids:
        if proxy_bid['max_amount'] > new_bid_amount:
            next_bid = new_bid_amount + 1.0
            if next_bid <= proxy_bid['max_amount']:
                bid_obj = Bid(
                    listing_id=listing_id,
                    bidder_id=proxy_bid['bidder_id'],
                    bidder_username=proxy_bid['bidder_username'],
                    amount=next_bid,
                    is_proxy_bid=True,
                    max_amount=proxy_bid['max_amount']
                )
                
                bid_doc = bid_obj.model_dump()
                bid_doc['timestamp'] = bid_doc['timestamp'].isoformat()
                await db.bids.insert_one(bid_doc)
                
                await db.listings.update_one(
                    {"id": listing_id},
                    {
                        "$set": {"current_price": next_bid},
                        "$inc": {"bid_count": 1}
                    }
                )
                
                # Sync to Supabase
                try:
                    supabase.table('bids').insert({
                        'id': bid_obj.id,
                        'listing_id': listing_id,
                        'bidder_id': proxy_bid['bidder_id'],
                        'bidder_username': proxy_bid['bidder_username'],
                        'amount': next_bid,
                        'is_proxy_bid': True,
                        'timestamp': bid_obj.timestamp.isoformat()
                    }).execute()
                except Exception as e:
                    logging.error(f"Supabase sync error: {e}")
                
                return True
    return False

# ============ AUTH ROUTES ============

@api_router.post("/auth/register")
async def register(user_input: UserRegister):
    existing = await db.users.find_one({"email": user_input.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
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

# ============ USER PROFILE ROUTES ============

@api_router.get("/users/{user_id}", response_model=User)
async def get_user_profile(user_id: str):
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if isinstance(user['created_at'], str):
        user['created_at'] = datetime.fromisoformat(user['created_at'])
    return User(**user)

@api_router.put("/users/me")
async def update_profile(bio: Optional[str] = None, authorization: Optional[str] = Header(None)):
    current_user = await get_current_user(authorization)
    update_data = {}
    if bio is not None:
        update_data['bio'] = bio
    
    if update_data:
        await db.users.update_one({"id": current_user['user_id']}, {"$set": update_data})
    
    return {"message": "Profile updated"}

@api_router.post("/ratings")
async def create_rating(rating_input: RatingCreate, authorization: Optional[str] = Header(None)):
    current_user = await get_current_user(authorization)
    
    if rating_input.rating < 1 or rating_input.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")
    
    user = await db.users.find_one({"id": current_user['user_id']}, {"_id": 0})
    
    rating_obj = UserRating(
        rated_user_id=rating_input.rated_user_id,
        rater_id=current_user['user_id'],
        rater_username=user['username'],
        rating=rating_input.rating,
        comment=rating_input.comment,
        listing_id=rating_input.listing_id
    )
    
    doc = rating_obj.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    await db.ratings.insert_one(doc)
    
    # Update user's average rating
    ratings = await db.ratings.find({"rated_user_id": rating_input.rated_user_id}, {"_id": 0}).to_list(1000)
    avg_rating = sum(r['rating'] for r in ratings) / len(ratings)
    
    await db.users.update_one(
        {"id": rating_input.rated_user_id},
        {"$set": {"rating_score": round(avg_rating, 2), "total_ratings": len(ratings)}}
    )
    
    return rating_obj

@api_router.get("/users/{user_id}/ratings")
async def get_user_ratings(user_id: str):
    ratings = await db.ratings.find({"rated_user_id": user_id}, {"_id": 0}).sort("created_at", -1).to_list(100)
    for rating in ratings:
        if isinstance(rating['created_at'], str):
            rating['created_at'] = datetime.fromisoformat(rating['created_at'])
    return ratings

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
async def get_listings(
    category: Optional[str] = None,
    status: str = "active",
    search: Optional[str] = None,
    condition: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: str = "created_at"
):
    query = {"status": status}
    if category:
        query["category"] = category
    if search:
        query["title"] = {"$regex": search, "$options": "i"}
    if condition:
        query["condition"] = condition
    if min_price is not None:
        query["current_price"] = query.get("current_price", {})
        query["current_price"]["$gte"] = min_price
    if max_price is not None:
        query["current_price"] = query.get("current_price", {})
        query["current_price"]["$lte"] = max_price
    
    sort_field = sort_by if sort_by != "ending_soon" else "ends_at"
    sort_dir = 1 if sort_by == "ending_soon" else -1
    
    listings = await db.listings.find(query, {"_id": 0}).sort(sort_field, sort_dir).to_list(100)
    
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
    
    # Increment views
    await db.listings.update_one({"id": listing_id}, {"$inc": {"views": 1}})
    
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
    
    listing = await db.listings.find_one({"id": bid_input.listing_id}, {"_id": 0})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing['status'] != 'active':
        raise HTTPException(status_code=400, detail="Listing is not active")
    
    if listing['listing_type'] != 'auction':
        raise HTTPException(status_code=400, detail="This is not an auction listing")
    
    if listing.get('ends_at'):
        ends_at = datetime.fromisoformat(listing['ends_at']) if isinstance(listing['ends_at'], str) else listing['ends_at']
        if ends_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=400, detail="Auction has ended")
    
    current_price = listing.get('current_price', listing.get('starting_price', 0.0))
    if bid_input.amount <= current_price:
        raise HTTPException(status_code=400, detail=f"Bid must be higher than current price of ${current_price}")
    
    if bid_input.is_proxy_bid and bid_input.max_amount:
        if bid_input.max_amount < bid_input.amount:
            raise HTTPException(status_code=400, detail="Max amount must be greater than or equal to bid amount")
    
    bid_obj = Bid(
        listing_id=bid_input.listing_id,
        bidder_id=current_user['user_id'],
        bidder_username=user['username'],
        amount=bid_input.amount,
        is_proxy_bid=bid_input.is_proxy_bid,
        max_amount=bid_input.max_amount if bid_input.is_proxy_bid else None
    )
    
    bid_doc = bid_obj.model_dump()
    bid_doc['timestamp'] = bid_doc['timestamp'].isoformat()
    await db.bids.insert_one(bid_doc)
    
    await db.listings.update_one(
        {"id": bid_input.listing_id},
        {
            "$set": {"current_price": bid_input.amount},
            "$inc": {"bid_count": 1}
        }
    )
    
    # Sync to Supabase for real-time
    try:
        supabase.table('bids').insert({
            'id': bid_obj.id,
            'listing_id': bid_input.listing_id,
            'bidder_id': current_user['user_id'],
            'bidder_username': user['username'],
            'amount': bid_input.amount,
            'is_proxy_bid': bid_input.is_proxy_bid,
            'timestamp': bid_obj.timestamp.isoformat()
        }).execute()
    except Exception as e:
        logging.error(f"Supabase sync error: {e}")
    
    # Process proxy bids
    if not bid_input.is_proxy_bid:
        await process_proxy_bids(bid_input.listing_id, bid_input.amount, current_user['user_id'])
    
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
    
    listing = await db.listings.find_one({"id": listing_id}, {"_id": 0})
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    if listing['status'] != 'active':
        raise HTTPException(status_code=400, detail="Listing is not active")
    
    amount = listing.get('buy_now_price') or listing.get('current_price', 0.0)
    
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Invalid listing price")
    
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
    
    payment = await db.payment_transactions.find_one({"session_id": session_id}, {"_id": 0})
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    if payment['payment_status'] == 'paid':
        return payment
    
    host_url = str(os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001'))
    webhook_url = f"{host_url}/api/webhook/stripe"
    stripe_checkout = StripeCheckout(api_key=stripe_api_key, webhook_url=webhook_url)
    
    checkout_status = await stripe_checkout.get_checkout_status(session_id)
    
    update_data = {
        "payment_status": checkout_status.payment_status,
        "status": checkout_status.status
    }
    
    await db.payment_transactions.update_one(
        {"session_id": session_id},
        {"$set": update_data}
    )
    
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
        
        if webhook_response.session_id:
            await db.payment_transactions.update_one(
                {"session_id": webhook_response.session_id},
                {"$set": {
                    "payment_status": webhook_response.payment_status,
                    "status": webhook_response.event_type
                }}
            )
            
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