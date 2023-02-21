import common
import helpers
from fastapi import FastAPI
from fastapi.background import BackgroundTasks
from fastapi.requests import Request
from fastapi.encoders import jsonable_encoder
from fastapi.templating import Jinja2Templates
from fastapi.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware


app = FastAPI()
app.add_middleware(
    GZipMiddleware, minimum_size=1024
)
app.add_middleware(
    CORSMiddleware,
    allow_headers=["*"], allow_credentials=True,
    allow_origins=["*"], allow_methods=["GET", "POST"]
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

@app.on_event('startup')
async def test_service():
    assert helpers.exists(helpers.join(helpers.config.template_folder_path, 'index.html')), \
        "Error! `index.html` does not exists!"
    assert helpers.exists(helpers.join(helpers.config.resources_folder_path, 'properties.yml')), \
        "Error! `properties.yml` does not exists!"
    props = helpers.config.get_resource('properties.yml')
    assert isinstance(props.get('config'), dict), "Error! bad properties `config` structure!"
    assert props.get('config').get('service') is not None, "Error! properties `config.service` is missing!"
    assert props.get('config').get('region') is not None, "Error! properties `config.region` is missing!"
    assert props.get('config').get('access-key') is not None, "Error! properties `config.access-key` is missing!"
    assert props.get('config').get('secret-key') is not None, "Error! properties `config.secret-key` is missing!"

@app.get('/')
async def index(req: Request): return templates.TemplateResponse('index.html', {"request": req})


@app.post('/api/tasks')
async def start_task(req: Request, bgt: BackgroundTasks):
    form_data = await req.form()
    if all([v != '' for k, v in form_data._dict.items()]):
        task_id = helpers.gen_id()
        bgt.add_task(common.sendmail, form_data, task_id, request=req)
        return JSONResponse(
            content=jsonable_encoder({
                "status": "success",
                "timestamp": helpers.stamp(),
                "taskId": task_id[:10]
            }),
            status_code=200,
            media_type="application/json",
            headers={"content-type": "application/json"}
        )
    return JSONResponse(
            content=jsonable_encoder({
                "status": "fail",
                "timestamp": helpers.stamp(),
                "reason": "Missing Parameters!"
            }),
            status_code=400,
            media_type="application/json",
            headers={"content-type": "application/json"}
        )
