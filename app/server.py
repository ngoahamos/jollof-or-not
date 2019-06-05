import aiohttp
import asyncio
import uvicorn
from fastai import *
from fastai.vision import *
from io import BytesIO
from starlette.applications import Starlette
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, JSONResponse
from starlette.staticfiles import StaticFiles
import base64

export_file_url = 'https://drive.google.com/uc?export=download&id=11XIWG1Af21Bg2Tj8Ai23dDdz_pajgK70'
export_file_name = 'export.pkl'

classes = ['jollof','waakye']
path = Path(__file__).parent

app = Starlette()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_headers=['X-Requested-With', 'Content-Type'])
app.mount('/static', StaticFiles(directory='app/static'))


async def download_file(url, dest):
    if dest.exists(): return
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.read()
            with open(dest, 'wb') as f:
                f.write(data)


async def setup_learner():
    await download_file(export_file_url, path / export_file_name)
    try:
        learn = load_learner(path, export_file_name)
        return learn
    except RuntimeError as e:
        if len(e.args) > 0 and 'CPU-only machine' in e.args[0]:
            print(e)
            message = "\n\nThis model was trained with an old version of fastai and will not work in a CPU environment.\n\nPlease update the fastai library in your training environment and export your model again.\n\nSee instructions for 'Returning to work' at https://course.fast.ai."
            raise RuntimeError(message)
        else:
            raise


loop = asyncio.get_event_loop()
tasks = [asyncio.ensure_future(setup_learner())]
learn = loop.run_until_complete(asyncio.gather(*tasks))[0]
loop.close()


@app.route('/')
async def homepage(request):
    html_file = path / 'view' / 'index.html'
    return HTMLResponse(html_file.open().read())


@app.route('/analyze', methods=['POST'])
async def analyze(request):
    data = await request.form()
    bytes = await (data["file"].read())
    result = predict_image_from_bytes(bytes)
    return pretty_result(result)
    

@app.route("/base64", methods=["POST"])
async def upload(request):
    data = await request.json()
    bytes = await (data.base64.read())
    imgdata = base64.b64decode(str(bytes))
    result = predict_image_from_bytes(imgdata)
    return pretty_result(result)

def pretty_result(result):
    prediction = str(result[0])
    probability = map(float, result[2])
    return JSONResponse({"result": prediction, "pro": probability})

def predict_image_from_bytes(bytes):
    img = open_image(BytesIO(bytes))
    return learn.predict(img)
    return JSONResponse({"predictions": losses})

if __name__ == '__main__':
    if 'serve' in sys.argv:
        uvicorn.run(app=app, host='0.0.0.0', port=5000, log_level="info")
