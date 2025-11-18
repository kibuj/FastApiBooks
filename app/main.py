from fastapi import FastAPI
from app.routers import auth, book, admin

app = FastAPI(title="Book API with RBAC")


app.include_router(auth.router)
app.include_router(book.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Main Page"}