import threading
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import helpers
import common


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
    start_time = common.time()
    res: Response = await call_next(req)
    res.headers["X-PROCESS-TIME"] = str(common.time() - start_time)
    return res

@app.middleware('http')
async def add_x_response_id_header(req: Request, call_next):
    res: Response = await call_next(req)
    res.headers["X-RESPONSE-ID"] = common.gen_id()
    return res

@app.on_event('startup')
async def test_service():
    assert helpers.exists(helpers.join(helpers.config.template_folder_path, 'index.html'))
    assert helpers.exists(helpers.join(helpers.config.template_folder_path, 'template.eml'))
    assert helpers.exists(helpers.join(helpers.config.resources_folder_path, 'properties.json'))
    props = helpers.config.get_resource('properties.json')
    for v in props.values():
        assert v != ""

@app.get('/')
async def index(req: Request): return templates.TemplateResponse('index.html', {"request": req})

@app.post('/api/tasks')
async def start_task(req: Request):
    form_data = await req.form()
    if all([v != '' for k, v in form_data._dict.items()]):
        task_id = common.gen_id()
        t = threading.Thread(target=common.sendmail, args=(form_data, task_id))
        t.run()
        return JSONResponse(
            content=jsonable_encoder({
                "status": "success",
                "timestamp": common.stamp(),
                "taskId": task_id
            }),
            status_code=200,
            media_type="application/json",
            headers={"content-type": "application/json"}
        )
    return JSONResponse(
            content=jsonable_encoder({
                "status": "fail",
                "timestamp": common.stamp(),
                "reason": "Missing Parameters!"
            }),
            status_code=400,
            media_type="application/json",
            headers={"content-type": "application/json"}
        )

@app.get('/api/tasks')
async def get_task(req: Request):
    """ TODO : Future implementation for getting a task status """
    return JSONResponse(
        content=jsonable_encoder({
            "status": "Not Implemented Yet!",
            "timestamp": common.stamp(),
            "requester": req.client.host
        }),
        status_code=200,
        media_type="application/json",
        headers={"content-type": "application/json"}
    )

if __name__ == '__main__':
    from uvicorn import run
    run(app, host="localhost", port=6061)
