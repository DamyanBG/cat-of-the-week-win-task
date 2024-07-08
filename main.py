import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db_operations.cat_operations import select_all_next_round_cats, insert_current_round_cats, delete_all_next_round_cats
from models.cat_model import CurrentRoundCatCreate


async def fetch_firestore_data():
    print('working')
    next_round_cats = await select_all_next_round_cats()
    current_round_cats = [CurrentRoundCatCreate(**cat.model_dump()) for cat in next_round_cats]
    await insert_current_round_cats(current_round_cats)
    await delete_all_next_round_cats(next_round_cats)
    print('done')


# Set up the async scheduler
scheduler = AsyncIOScheduler()

# Schedule the job to run every 10 seconds
scheduler.add_job(fetch_firestore_data, 'interval', seconds=30)

# Start the scheduler
scheduler.start()


asyncio.get_event_loop().run_forever()
