import asyncio
import json
import logging
import time
import os
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from typing import List, Annotated
from datetime import datetime

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse

from app.models import QueueItem, QueueItemWebhookIncoming, QueueItemWebhookStored, QueueItemWebhookNormalized
from app.settings import get_settings
from formbricks.client import FormbricksClient
from formbricks.handler import normalize_webhook_content
from formbricks.models import FormbricksWebhook
from grist import handler as grist_handler
from grist.client import GristClient
from grist.handler import add_webhook_row
from notification.handler import send_email_for_record


async def process_requests(q: asyncio.Queue, pool: ProcessPoolExecutor):

    while True:
        item: QueueItem = await q.get()  # Get a request from the queue
        loop = asyncio.get_running_loop()
        try:
            if isinstance(item, QueueItemWebhookIncoming):
                q.put_nowait(
                    QueueItemWebhookNormalized(
                        data=await loop.run_in_executor(pool, normalize_webhook_content, item.data, form_client)
                    )
                )
            elif isinstance(item, QueueItemWebhookNormalized):
                q.put_nowait(
                    QueueItemWebhookStored(
                        data=await loop.run_in_executor(pool, add_webhook_row, item.data, grist)
                    )
                )
            elif isinstance(item, QueueItemWebhookStored):
                await loop.run_in_executor(pool, send_email_for_record, item.data)

            # await loop.run_in_executor(pool, send_email_for_record, record_id)
            q.task_done()  # tell the queue that the processing on the task is completed
        except Exception as e:
            logger.error(f"processing of {item.data.webhook_id} failed: {e}")
            time.sleep(1)
            item.retries += 1
            if item.retries <= 3:
                q.put_nowait(item)
        logger.debug(f"queue size: {q.qsize()}")


@asynccontextmanager
async def lifespan(_: FastAPI):
    q = asyncio.Queue()  # note that asyncio.Queue() is not thread safe
    pool = ProcessPoolExecutor()
    # noinspection PyAsyncCall
    asyncio.create_task(process_requests(q, pool))  # Start the requests processing task
    yield {'q': q, 'pool': pool}
    pool.shutdown()  # free any resources that the pool is using when the currently pending futures are done executing


# ========================
# Application setup
# ========================


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app_name = "Formbricks2Grist API"
app_description = "Add Formbricks survey response to Grist document"
app_version = "0.0.1"

settings = get_settings()

# ========================
# FastAPI Application
# ========================

app = FastAPI(
    title=app_name,
    description=app_description,
    version=app_version,
    debug=True if settings.logging.level == "DEBUG" else False,
    lifespan=lifespan
)

try:
    form_client = FormbricksClient(settings.formbricks)
except Exception as error:
    logger.error(f"failed to connect to Formbricks: {error}")
    exit(1)

try:
    grist = GristClient(settings.grist)
except Exception as error:
    logger.error(f"failed to connect to grist: {error}")
    exit(1)

# ========================
# API Endpoints
# ========================


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "app": app_name,
        "version": app_version,
        "message": "API is running"
    }


@app.get("/config")
async def get_config(request: Request):

    if "localhost" not in request.headers.get("host", ""):
        return {"status": "ok"}

    return {
        "app_name": app_name,
        "app_version": app_version,
        **json.loads(settings.model_dump_json())}


@app.post("/webhook/formbricks")
async def handle_formbricks_webhook(request: Request, api_token: Annotated[str | None, Query()] = None):
    """
    hand formbricks webhooks
    """

    try:

        if settings.formbricks.webhook_api_token is not None:
            if api_token != settings.formbricks.webhook_api_token.get_secret_value():
                return JSONResponse(
                    status_code=401,
                    content={"status": "error", "message":  "401 - unauthorized"}
                )

        # get content
        payload = await request.json()

        webhook_data = FormbricksWebhook(**payload)

        dump_file_dir = "dump"
        dump_file_name = f'{webhook_data.event}_{datetime.now().strftime("%F_%T")}_{webhook_data.webhookId}.json'

        if settings.logging.level == "DEBUG" and os.access(dump_file_dir, os.W_OK | os.X_OK):
            with open(f'{dump_file_dir}/formbricks_webhook_{dump_file_name}', 'w') as f:
                f.write(webhook_data.model_dump_json(indent=2))

        logger.info(f"Webhook event received: {webhook_data.event}")

        if webhook_data.event == "responseFinished":
            request.state.q.put_nowait(QueueItemWebhookIncoming(data=webhook_data))
        else:
            logger.warning(f"unhandled event type: {webhook_data.event}")

        return JSONResponse(
            status_code=200,
            content={"status": "success", "message": "received webhook"}
        )

    except Exception as e:
        logger.error(f"issue while handling webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/public-list")
async def grist_export() -> List:

    return grist_handler.grist_export(grist_client=grist)


@app.get("/health")
async def health_check():

    return {
        "status": "healthy",
        "service": app_name,
        "version": app_version
    }


# ========================
# Application Entry Point
# ========================

if __name__ == "__main__":
    import uvicorn

    # set log level
    logging.getLogger().setLevel(settings.logging.level)

    uvicorn.run(
        "main:app",
        host=settings.server.listen,
        port=settings.server.port,
        reload=settings.server.reload,
        workers=settings.server.workers
    )
