from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.database import get_db, engine
from app.models import Base
from app.schemas import SubscriberIn, BulkEmailRequest
from app.services import add_subscriber, get_subscribers_by_category, send_bulk_email

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/subscribe")
def subscribe(payload: SubscriberIn, db: Session = Depends(get_db)):
    return add_subscriber(db, payload)

@app.post("/send-bulk")
def send_bulk(payload: BulkEmailRequest, db: Session = Depends(get_db)):
    # Pass the DB session and the full payload to the service function.
    # The service will resolve subscribers and build recipient objects.
    return send_bulk_email(db, payload)
