from backend.src.main import app
from json import dump

with open("../openapi.json", "w") as file:
    dump(app.openapi(), file)
