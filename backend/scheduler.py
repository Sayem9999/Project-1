from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import os

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
db_name = os.environ.get('DB_NAME', 'test_database')
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

async def close_expired_auctions():
    """Close all expired auctions"""
    try:
        current_time = datetime.now(timezone.utc)
        
        # Find all active auctions that have expired
        expired_auctions = await db.listings.find({
            "listing_type": "auction",
            "status": "active",
            "ends_at": {"$lte": current_time.isoformat()}
        }, {"_id": 0}).to_list(100)
        
        if not expired_auctions:
            logger.info("No expired auctions to close")
            return
        
        logger.info(f"Found {len(expired_auctions)} expired auctions to close")
        
        for auction in expired_auctions:
            listing_id = auction['id']
            
            # Get the highest bid
            highest_bid = await db.bids.find_one(
                {"listing_id": listing_id},
                {"_id": 0},
                sort=[("amount", -1)]
            )
            
            if highest_bid:
                # Auction has bids - mark as sold to highest bidder
                await db.listings.update_one(
                    {"id": listing_id},
                    {
                        "$set": {
                            "status": "sold",
                            "winner_id": highest_bid['bidder_id'],
                            "closed_at": current_time.isoformat(),
                            "final_price": highest_bid['amount']
                        }
                    }
                )
                logger.info(f"Auction {listing_id} closed - Winner: {highest_bid['bidder_username']} - Amount: {highest_bid['amount']}")
            else:
                # No bids - mark as expired
                await db.listings.update_one(
                    {"id": listing_id},
                    {
                        "$set": {
                            "status": "expired",
                            "closed_at": current_time.isoformat()
                        }
                    }
                )
                logger.info(f"Auction {listing_id} expired with no bids")
        
        logger.info(f"Successfully closed {len(expired_auctions)} auctions")
    
    except Exception as e:
        logger.error(f"Error in close_expired_auctions: {str(e)}")

# Initialize scheduler
scheduler = AsyncIOScheduler()

def start_scheduler():
    """Start the background scheduler"""
    # Run close_expired_auctions every 1 minute
    scheduler.add_job(
        close_expired_auctions,
        'interval',
        minutes=1,
        id='close_expired_auctions',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started - Running auction auto-close every 1 minute")

def shutdown_scheduler():
    """Shutdown the scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down")
