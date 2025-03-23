# mypy: ignore-errors
import logging
import os
import tempfile

import uvicorn
from fastapi import FastAPI, HTTPException, Request, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from swecc_email_sender.core.loader import DataLoader
from swecc_email_sender.core.sender import EmailSender
from swecc_email_sender.utils.markdown_utils import convert_markdown_to_html

logger = logging.getLogger(__name__)

app = FastAPI()

state = {
    "api_key": None,
    "from_email": None,
    "subject": None,
    "content": None,
    "template_path": None,
    "data_path": None,
    "data": None,
    "is_markdown": False,
}

app.mount("/static", StaticFiles(directory="swecc_email_sender/server/static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open(os.path.join("swecc_email_sender", "server", "static", "index.html")) as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.get("/api/state")
async def get_state():
    """Get the current state of the application"""
    # don't return API key in the response
    response_state = state.copy()
    response_state.pop("api_key", None)

    response_state["has_api_key"] = state["api_key"] is not None
    response_state["has_data"] = state["data"] is not None
    response_state["has_content"] = state["content"] is not None

    return response_state


@app.post("/api/upload/data")
async def upload_data(file: UploadFile):
    """Upload CSV or JSON data file"""
    try:
        suffix = ".csv" if file.filename.endswith(".csv") else ".json"
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
            content = await file.read()
            temp.write(content)
            temp_file_path = temp.name

        data = DataLoader.load_data(temp_file_path)

        state["data_path"] = temp_file_path
        state["data"] = data

        return {"message": "Data uploaded successfully", "rows": len(data)}

    except Exception as e:
        logger.error(f"Error uploading data: {e}")
        raise HTTPException(status_code=400, detail=f"Error uploading data: {e!s}") from e


@app.post("/api/upload/template")
async def upload_template(file: UploadFile):
    """Upload email template file"""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as temp:
            content = await file.read()
            temp.write(content)
            temp_file_path = temp.name

        template_content = DataLoader.load_template(temp_file_path)

        state["template_path"] = temp_file_path
        state["content"] = template_content

        return {"message": "Template uploaded successfully", "content": template_content}

    except Exception as e:
        logger.error(f"Error uploading template: {e}")
        raise HTTPException(status_code=400, detail=f"Error uploading template: {e!s}") from e


@app.post("/api/settings")
async def update_settings(request: Request):
    """Update email sender settings"""
    try:
        data = await request.json()

        if data.get("api_key"):
            state["api_key"] = data["api_key"]

        if data.get("from_email"):
            state["from_email"] = data["from_email"]

        if "subject" in data and data["subject"] is not None:
            state["subject"] = data["subject"]

        if "content" in data and data["content"] is not None:
            state["content"] = data["content"]

        if "is_markdown" in data:
            state["is_markdown"] = data["is_markdown"]

        return {"message": "Settings updated successfully"}

    except Exception as e:
        logger.error(f"Error updating settings: {e}")
        raise HTTPException(status_code=400, detail=f"Error updating settings: {e!s}") from e


@app.get("/api/preview")
async def preview_email(row_index: int = 0):
    """Preview email for a specific row in the data"""
    try:
        if not state["content"]:
            raise HTTPException(status_code=400, detail="No content or template provided")

        if not state["data"] or row_index >= len(state["data"]):
            raise HTTPException(status_code=400, detail="Data not available or invalid row index")

        sender = EmailSender(state["api_key"] or "dummy_key")

        data_row = state["data"][row_index]
        formatted_content = sender.format_with_fallback(state["content"], data_row)

        formatted_subject = state["subject"]
        if formatted_subject:
            formatted_subject = sender.format_with_fallback(formatted_subject, data_row)

        html_content = (
            convert_markdown_to_html(formatted_content)
            if state["is_markdown"]
            else formatted_content
        )

        return {
            "to_email": data_row.get("to_email", "Not specified"),
            "from_email": state["from_email"],
            "subject": formatted_subject,
            "content": formatted_content,
            "html_content": html_content,
            "data_row": data_row,
            "row_index": row_index,
            "total_rows": len(state["data"]),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating preview: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating preview: {e!s}") from e


@app.get("/api/validate")
async def validate_template():
    """Validate the template against all data rows"""
    try:
        if not state["content"]:
            raise HTTPException(status_code=400, detail="No content or template provided")

        if not state["data"]:
            raise HTTPException(status_code=400, detail="No data available")

        sender = EmailSender(state["api_key"] or "dummy_key")

        validation_results = []
        for i, item in enumerate(state["data"]):
            missing_keys = sender.validate_template_keys(state["content"], item)

            missing_subject_keys = []
            if state["subject"]:
                missing_subject_keys = sender.validate_template_keys(state["subject"], item)

            validation_results.append(
                {
                    "row_index": i,
                    "to_email": item.get("to_email", "Not specified"),
                    "missing_keys": missing_keys,
                    "missing_subject_keys": missing_subject_keys,
                    "has_errors": bool(missing_keys or missing_subject_keys),
                }
            )

        return {
            "validation_results": validation_results,
            "total_valid": sum(1 for r in validation_results if not r["has_errors"]),
            "total_invalid": sum(1 for r in validation_results if r["has_errors"]),
            "total_rows": len(validation_results),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating template: {e}")
        raise HTTPException(status_code=500, detail=f"Error validating template: {e!s}") from e


def main(args) -> int:
    """Main entry point for the web interface"""
    state["api_key"] = args.api_key or os.environ.get("SENDGRID_API_KEY")
    state["from_email"] = args.from_email
    state["subject"] = args.subject
    state["is_markdown"] = args.markdown

    if args.template:
        try:
            state["template_path"] = args.template
            state["content"] = DataLoader.load_template(args.template)
        except Exception as e:
            logger.error(f"Error loading template: {e}")

    elif args.content:
        state["content"] = args.content

    if args.src:
        try:
            state["data_path"] = args.src
            state["data"] = DataLoader.load_data(args.src)
        except Exception as e:
            logger.error(f"Error loading data: {e}")

    logger.info(f"Starting email sender web interface on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port)

    return 0
