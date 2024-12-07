from json import dump

from backend import app

with open("openapi.json", "w") as file:
    dump(app.openapi(), file)
