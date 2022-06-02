from Meeting_Management import app


@app.get("/")
def home():
    return {"Hello": "World"}


