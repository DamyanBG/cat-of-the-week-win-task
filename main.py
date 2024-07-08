import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import date

from queries.cat_queries import CatQueries
from models.cat_model import CurrentRoundCatCreate, CatOfTheWeekCreate


async def fetch_firestore_data():
    print("working")
    winning_cat = await CatQueries.select_winning_cat()
    current_date = date.today()
    iso_calendar = current_date.isocalendar()
    cat_of_the_week = CatOfTheWeekCreate(
        week_number=iso_calendar.week,
        year=iso_calendar.year,
        **winning_cat.model_dump()
    )
    await CatQueries.insert_cat_of_the_week(cat_of_the_week)
    await CatQueries.delete_all_current_round_cats()
    next_round_cats = await CatQueries.select_all_next_round_cats()
    current_round_cats = [
        CurrentRoundCatCreate(**cat.model_dump()) for cat in next_round_cats
    ]
    await CatQueries.insert_current_round_cats(current_round_cats)
    await CatQueries.delete_all_next_round_cats(next_round_cats)
    print("done")


# Set up the async scheduler
scheduler = AsyncIOScheduler()

# Schedule the job to run every 10 seconds
scheduler.add_job(fetch_firestore_data, "interval", seconds=30)

# Start the scheduler
scheduler.start()


asyncio.get_event_loop().run_forever()
