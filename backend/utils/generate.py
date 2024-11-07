from json import dump

from src.main import app

with open("openapi.json", "w") as file:
    dump(app.openapi(), file)
