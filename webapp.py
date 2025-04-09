import hashlib
import json
import sqlite3

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import __checking__

con = sqlite3.connect(r'db/archive_of_users.db')
cur = con.cursor()

app = FastAPI()

# Монтируем папку со статическими файлами (если понадобятся)
app.mount("/images", StaticFiles(directory="images"), name="images")

# Настройка шаблонов
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request, user_id: int = None, checking: str = None):
    new_checking = __checking__ + str(user_id)
    new_checking = hashlib.sha256(new_checking.encode("utf8")).hexdigest()
    if user_id is None:
        return ""
    if checking is None:
        return ""
    if checking != new_checking:
        return ""
    cur.execute(f"SELECT * FROM user{user_id}")
    user = cur.fetchall()

    data = []
    for day in user:
        data.append({
            "img": day[2],
            "date": day[0],
            "text": day[1]
        })

    # Передаём данные в шаблон, предварительно сериализовав их в JSON для использования в JS
    return templates.TemplateResponse("index.html", {
        "request": request,
        "gallery_data": json.dumps(data, ensure_ascii=False)
    })


uvicorn.run(app, host="127.0.0.1", port=80)
