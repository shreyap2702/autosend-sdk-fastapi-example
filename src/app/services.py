from sqlalchemy.orm import Session
from app.models import Subscriber
from autosend import AutosendClient
from app.schemas import SubscriberIn, BulkEmailRequest
from dotenv import load_dotenv
import os

load_dotenv()  # this loads variables from .env

API_KEY = os.getenv("AUTOSEND_API_KEY")

client = AutosendClient(API_KEY)

def add_subscriber(db: Session, payload: SubscriberIn):
    sub = Subscriber(
        name=payload.name,
        email=payload.email,
        categories=",".join(payload.categories)
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)

    # add to Autosend Contacts using your SDK
    client.contacts.create_contact(
        email=sub.email,
        first_name=sub.name.split()[0],
        last_name=sub.name.split()[-1],
        user_id=None,
        custom_fields={"categories": sub.categories}
    )

    return {"message": "Subscriber added", "subscriber": sub.email}


def get_subscribers_by_category(db: Session, category: str):
    # Return Subscriber objects (with .email and .name) so callers can
    # build recipient dicts including name and email.
    subs = db.query(Subscriber).all()
    return [s for s in subs if category in s.categories.split(",")]


def send_bulk_email(db: Session, payload: BulkEmailRequest):
    subs = get_subscribers_by_category(db, payload.category)

    recipients = [
        {"email": sub.email, "name": sub.name}
        for sub in subs
    ]

    if not recipients:
        return {"error": "No subscribers found in this category"}

    # Hardcoded mapping of category -> unsubscribe group id.
    # This will instruct the Autosend API to treat unsubscribe actions
    # as removing the recipient from that specific group.
    CATEGORY_GROUP_IDS = {
        "promotional": "1Z50B",
        "technical": "grp_tech_456",
        "newsletter": "8IV7J",
    }

    unsubscribe_group_id = CATEGORY_GROUP_IDS.get(payload.category)

    # We do NOT append any footer HTML to the provided template here.
    # The unsubscribe behavior is sent via the `unsubscribe` fields in the
    # API payload (groupId). The SDK/server is expected to render any
    # unsubscribe UI/button where appropriate. This keeps the email HTML
    # unchanged while enabling unsubscribe-by-group functionality.

    return client.sending.send_bulk(
        recipients=recipients,
        from_email=payload.from_email,
        from_name=payload.from_name,
        subject=payload.subject,
        html=payload.html,
        dynamic_data={},
        unsubscribe_group_id=unsubscribe_group_id,
    )

