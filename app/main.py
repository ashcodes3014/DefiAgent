from fastapi import FastAPI
from apscheduler.schedulers.background import BackgroundScheduler
import time
from scheduler import process_user
from fetch import fetch_chosen_wallets, get_all_users_wallets

app = FastAPI()

def scheduled_update():
    print("⏳ Running scheduled wallet update...")
    result = fetch_chosen_wallets()
    users = get_all_users_wallets(result)
    for user in users:
        process_user(user)
        time.sleep(10)
    print("✅ Scheduled update complete")


@app.on_event("startup")
def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(scheduled_update, "interval", minutes=1, id="wallet_update_job")
    scheduler.start()
    print("Scheduler started - updates every 1 minute")


@app.get("/Update")
def update():
    return scheduled_update()
