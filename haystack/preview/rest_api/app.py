from fastapi import FastAPI, HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse
from canals import load_pipelines

from haystack import __version__
from haystack.preview.rest_api.config import DEFAULT_PIPELINES


APP = None
OPENAPI_TAGS = [
    {"name": "about", "description": "Check the app's status"},
    {"name": "pipelines", "description": "Operations on Pipelines: list, warmup, run, etc..."},
    {"name": "files", "description": "Operations on files: upload, dowload, list, etc..."},
]


async def http_error_handler(_: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse({"errors": [exc.detail]}, status_code=exc.status_code)


class HaystackAPI(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pipelines = load_pipelines(DEFAULT_PIPELINES)

        from haystack.preview.rest_api.routers import pipelines, about, files

        self.include_router(pipelines.router, tags=["pipelines"])
        self.include_router(files.router, tags=["files"])
        self.include_router(about.router, tags=["about"])

        self.add_exception_handler(HTTPException, http_error_handler)


def get_app():
    global APP  # pylint: disable=global-statement
    if not APP:
        APP = HaystackAPI(title="Haystack", debug=False, version=__version__, root_path="/", openapi_tags=OPENAPI_TAGS)
    return APP
