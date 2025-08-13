from fastapi import FastAPI
from scheduler import run_scheduler
import threading

app = FastAPI()

@app.on_event("startup")
def start_scheduler():
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    print("Scheduler thread started.")


@app.get("/check")
def check():
   return "Backend is running ....."
