from pydantic import BaseModel, EmailStr, field_validator

ALLOWED_CATEGORIES = ["promotional", "technical", "newsletter"]

class SubscriberIn(BaseModel):
    name: str
    email: EmailStr
    categories: list[str]

    @field_validator("categories")
    def validate_categories(cls, v):
        if len(v) == 0:
            raise ValueError("At least 1 category is required.")
        if len(v) > 3:
            raise ValueError("Max 3 categories allowed.")
        for c in v:
            if c not in ALLOWED_CATEGORIES:
                raise ValueError(f"Invalid category: {c}")
        return v


class BulkEmailRequest(BaseModel):
    category: str
    subject: str
    html: str
    from_email: EmailStr
    from_name: str

