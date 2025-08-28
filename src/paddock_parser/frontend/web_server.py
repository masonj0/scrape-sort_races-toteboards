from fastapi import FastAPI

app = FastAPI(title="Paddock Parser NG", version="1.0.0")

@app.get("/")
def read_root():
    """
    Root endpoint for the Paddock Parser NG API.
    """
    return {"message": "Welcome to the Paddock Parser Next Generation Monolith!"}

@app.get("/races")
def get_races():
    """
    Placeholder endpoint to get scored races.
    """
    return {"message": "This endpoint will return scored races."}
