import uvicorn
import matplotlib
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from decouple import config, Csv
from pydantic import Json

from service import service
from services.models.models import Options
from services.utils.exceptions import InvalidRequestError

# To ensure we can plot in different threads
# https://matplotlib.org/stable/users/faq/howto_faq.html#work-with-threads
# https://matplotlib.org/stable/users/explain/backends.html#selecting-a-backend
matplotlib.use("agg")

# with open(os.path.join(".", "plotter\\schema.json")) as f:
#     PLOTTER_OPTIONS_SCHEMA = load(f)

app = FastAPI()

origins = [
    "http://localhost:8080",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/plotter",
    responses={200: {"content": {"image/png": {}}}},
    # Prevent FastAPI from adding "application/json" as an additional
    # response media type in the autogenerated OpenAPI specification.
    # https://github.com/tiangolo/fastapi/issues/3258
    response_class=Response,
)
def plot_request(
    rawData: UploadFile = File(...),
    rawOptions: Json[Options] = Form(...),
):
    try:
        print(rawData)
        plot_img = service(rawData, rawOptions)
    except (InvalidRequestError, ValueError) as e:
        raise HTTPException(status_code=400, detail="Bad request: " + str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Oops my bad: " + str(e))
    return Response('plot_img', media_type="image/png")


def run():
    # .env file example:
    # PLOTTER_SERVER=127.0.0.1,8081,debug
    host, port, log_level = config("PLOTTER_SERVER", cast=Csv())
    uvicorn.run(
        "server:app", host=host, port=int(port), log_level=log_level, reload=True
    )


if __name__ == "__main__":
    run()
