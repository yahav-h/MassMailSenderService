import threading
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import helpers


app = FastAPI()
app.add_middleware(
    GZipMiddleware, minimum_size=1000
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"], allow_credentials=True
)
templates = Jinja2Templates(directory=helpers.config.template_folder_path)

@app.middleware('http')
async def add_x_process_time_header(req: Request, call_next):
    start_time = helpers.time()
    res: Response = await call_next(req)
    res.headers["X-PROCESS-TIME"] = str(helpers.time() - start_time)
    return res

@app.middleware('http')
async def add_x_response_id_header(req: Request, call_next):
    res: Response = await call_next(req)
    res.headers["X-RESPONSE-ID"] = helpers.gen_id()
    return res

@app.get('/')
async def index(req: Request): return templates.TemplateResponse('index.html', {"request": req})

@app.post('/api/sendmail')
async def sendmail(req: Request):
    form_data = await req.form()
    task_id = helpers.gen_id()
    t = threading.Thread(target=helpers.sendmail, args=(form_data, task_id))
    t.run()
    return JSONResponse(
        content=jsonable_encoder({
            "status": "success",
            "timestamp": helpers.stamp(),
            "taskId": task_id
        }),
        status_code=200,
        media_type="application/json",
        headers={"content-type": "application/json"}
    )

if __name__ == '__main__':
    from uvicorn import run
    run(app, host="localhost", port=6061)
