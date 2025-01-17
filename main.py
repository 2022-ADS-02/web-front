import uvicorn
from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from httpx import AsyncClient
from fastapi.responses import FileResponse
import traceback

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

search_base_url = "http://172.17.0.1:8080/"
# search_base_url = "http://localhost:7001/"
judge_base_url = "http://172.17.0.1:8080/"
# judge_base_url = "http://172.17.0.1:9000/"
# judge_base_url = "http://localhost:9000/"

problem_info = {}
cur_problem = ''
test_passed = False
submit_passed = False
cur_code = ''
cur_language = 'Python'

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse("static/image/kuwhale.png")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request,
                                                     "cur_problem": cur_problem,
                                                     "cur_code": cur_code,
                                                     "cur_language": cur_language,
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
                                                     "test_passed": test_passed,
                                                     "submit_passed": submit_passed,
                                                     })


# 문제 번호 제출 시
@app.post("/search")
async def search_boj_problem(request: Request, task: str = Form(...)):
    global cur_problem
    # 크롤링 서버로부터 받아옴
    if task == "":
        cur_problem = ''
        problem_info.clear()
        return
    cur_problem = task
    # async with AsyncClient(base_url="http://172.17.0.1:7000/search/") as ac:
    async with AsyncClient(base_url=search_base_url) as ac:
        try:
            response = await ac.get(url="search/" + task)
            assert response.status_code == 200
            response_json = response.json()
            problem_info["problem_description"] = response_json["problem_description"]
            problem_info["problem_input"] = response_json["problem_input"]
            problem_info["problem_output"] = response_json["problem_output"]
            problem_info["samples"] = response_json["samples"]
            problem_info["samples_text"] = response_json["samples_text"]
            global test_passed, submit_passed
            test_passed = False
            submit_passed = False
        except Exception as e:
            traceback.print_exc()
        return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)


@app.post("/scoring/{language}")
async def send_request_to_scoring(request: Request, language: str, batch_content: str = Form(...)):
    if language != "Python" and language != "Java":
        print(language, "NOT SUPPORTED")
        return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)
    global cur_code, cur_language
    cur_code = batch_content
    cur_language = language
    post_request = {"language": language, "code": batch_content,
                    "samples_text": problem_info["samples_text"] if "samples_text" in problem_info else ""}
    print(post_request)
    async with AsyncClient(base_url=judge_base_url) as ac:
        try:
            response = await ac.post(url="judge", json=post_request)

            if response.status_code != 200:
                print('Response not OK:', response.status_code)

            assert response.status_code == 200
            global test_passed, submit_passed
            if response.json():
               print("맞았습니다!")
               test_passed = True
            else:
               print("틀렸습니다..")
               test_passed = False
        except Exception as e:
            traceback.print_exc()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)


@app.get("/init")
async def init_all_variables():
    global problem_info, cur_problem, cur_code, cur_language, test_passed, submit_passed
    problem_info = {}
    cur_problem = ''
    cur_code = ''
    cur_language = 'Python'
    test_passed = False
    submit_passed = False
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

if __name__ == '__main__':
    # get_problem_info(1000)
    uvicorn.run("main:app", port=8000, reload=True)
