# Autosend SDK FastAPI Example

A small FastAPI example that demonstrates storing subscribers and sending category-targeted bulk emails using the Autosend SDK.

## What this app is

This is a minimal demo service that:
- Stores subscribers (name, email, categories) in a local database.
- Adds new subscribers to the Autosend Contacts via the Autosend SDK.
- Sends bulk emails to all subscribers in a chosen category using the Autosend SDK's `send_bulk` endpoint.
- Sends unsubscribe configuration per-category so recipients can unsubscribe from a specific group.

The project is intended as an example of integrating Autosend into a Python FastAPI service.

## Project structure

```
src/
  app/
    database.py        # SQLAlchemy DB setup and dependency
    main.py            # FastAPI app and endpoints (/subscribe, /send-bulk)
    models.py          # SQLAlchemy models (Subscriber)
    schemas.py         # Pydantic request/response schemas
    services.py        # Business logic: add_subscriber, get_subscribers_by_category, send_bulk_email
    __pycache__/

README.md
```

Key files:
- `src/app/main.py` — defines two endpoints:
  - `POST /subscribe` — accepts `SubscriberIn` payload and stores subscriber.
  - `POST /send-bulk` — accepts `BulkEmailRequest` and triggers a bulk send.
- `src/app/services.py` — application logic and the place where the Autosend SDK is used.
- `src/app/schemas.py` — contains request validation and allowed categories.

## How the app uses the Autosend SDK

This project uses the Autosend Python SDK via an `AutosendClient` instance created in `services.py`.
The SDK is used in two places:

1. Adding contacts: when a subscriber is created, the app calls `client.contacts.create_contact(...)` to mirror the subscriber in the Autosend contacts system.
2. Sending emails: when sending bulk emails the app calls `client.sending.send_bulk(...)` to deliver the message to multiple recipients.

The SDK supports:
- Single and bulk sends.
- `dynamicData` for template variable substitution.
- attachments and unsubscribe fields (`unsubscribe.url` or `unsubscribe.groupId`).

Note: In the example code the API key is currently instantiated directly in `services.py`. For production, move the API key to an environment variable and load it at runtime (for security).

## Where exactly the SDK is used in the codebase

Open `src/app/services.py` — the relevant spots are:

- add_subscriber(...) — after persisting a subscriber locally, it calls:

```py
client.contacts.create_contact(
    email=sub.email,
    first_name=sub.name.split()[0],
    last_name=sub.name.split()[-1],
    user_id=None,
    custom_fields={"categories": sub.categories}
)
```

This syncs the local subscriber into Autosend's Contacts resource.

- send_bulk_email(db, payload) — builds recipient dictionaries from local subscribers and calls the Autosend sending API:

```py
client.sending.send_bulk(
    recipients=recipients,
    from_email=payload.from_email,
    from_name=payload.from_name,
    subject=payload.subject,
    html=payload.html,
    dynamic_data={},
    unsubscribe_group_id=<group id mapped from payload.category>
)
```

The project includes a hardcoded mapping of local category names to `unsubscribe_group_id` values. That allows the server to instruct the Autosend API to treat unsubscription actions as removing a user from a specific group/category.

## Endpoints and payloads

- POST /subscribe
  - Body: `SubscriberIn` (name, email, categories)
  - Behavior: store subscriber locally and create contact in Autosend.

- POST /send-bulk
  - Body: `BulkEmailRequest` (category, subject, html, from_email, from_name)
  - Behavior: find subscribers in given category, build recipients list, and call `client.sending.send_bulk(...)`.

Example `BulkEmailRequest`:

```json
{
  "category": "newsletter",
  "subject": "This week's news",
  "html": "<p>Hello {{name}}</p>",
  "from_email": "no-reply@example.com",
  "from_name": "Example Team"
}
```

## Notes & recommendations

- Security: Do not hardcode API keys. Use environment variables (e.g., `AUTOSEND_API_KEY`) and a secure secrets manager for production.
- Unsubscribe behavior: The current code sends `unsubscribe_group_id` to the SDK (hardcoded mapping). If you want per-recipient personalized unsubscribe links, create per-recipient `dynamicData` entries with a generated token and a URL that resolves to a backend route that removes the category for that subscriber.
- Tests: Add tests that mock `client.sending.send_bulk` to assert the payload contains the `unsubscribe.groupId` when expected.
- Error handling: Convert service dict error returns into proper HTTP responses (raise FastAPI `HTTPException`) to make client error handling consistent.

## Running locally (quick)

1. Create a virtualenv and install dependencies (your project should list them in a requirements file).
2. Set `PYTHONPATH=src` (or install package) so `app` can be imported.
3. Start the app, for example with Uvicorn:

```bash
uvicorn app.main:app --reload --app-dir src
```

4. Use curl or Postman to exercise `/subscribe` and `/send-bulk`.

## License & attribution

This is example/demo code. Review and adapt for production use.
