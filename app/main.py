from fastapi import FastAPI
from app.routers import auth, book, admin
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.limiter import limiter

app = FastAPI(title="Book API")

#рейзить помилку при перевищенні кількості запитів
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.state.limiter = limiter
app.include_router(auth.router)
app.include_router(book.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Main Page"}