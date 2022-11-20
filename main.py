import requests
from bs4 import BeautifulSoup
import uvicorn
from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from httpx import AsyncClient

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

problem_info = {}

cur_problem = ''

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "cur_problem": cur_problem,
                                                     "problem_description": problem_info[
                                                         "problem_description"] if "problem_description" in problem_info else "",
                                                     "problem_input": problem_info[
                                                         "problem_input"] if "problem_input" in problem_info else "",
                                                     "problem_output": problem_info[
                                                         "problem_output"] if "problem_output" in problem_info else "",
                                                     "samples": problem_info[
                                                         "samples"] if "samples" in problem_info else "",
                                                     "samples_text": problem_info[
                                                         "samples_text"] if "samples_text" in problem_info else "",
                                                     })

# 문제 번호 제출 시
@app.post("/search")
async def search_boj_problem(request: Request, task: str = Form(...)):
    # 크롤링 서버로부터 받아옴
    global cur_problem
    cur_problem = task
    async with AsyncClient(base_url="http://localhost:7000/search/") as ac:
        response = await ac.get(task)
        response_json = response.json()
        problem_info["problem_description"] = response_json["problem_description"]
        problem_info["problem_input"] = response_json["problem_input"]
        problem_info["problem_output"] = response_json["problem_output"]
        problem_info["samples"] = response_json["samples"]
        problem_info["samples_text"] = response_json["samples_text"]
        return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

@app.post("/scoring")
async def send_request_to_scoring(request: Request, batch_content: str = Form(...)):
    # 크롤링 서버로부터 받아옴
    print(batch_content)
    if "samples_text" in problem_info:
        print(problem_info["samples_text"])
    # {"code": batch_content}
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

if __name__ == '__main__':
    # get_problem_info(1000)
    uvicorn.run("main:app", port=8000, reload=True)