"""
FastAPI app for invoice upload + extraction
"""
import logging
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import shutil
import uuid

from .config import BASE_DIR, DEMO_DATA_PATH
from .extract import extract_invoice
from .validate import validate_extraction
from .sheets_writer import SheetsWriter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Invoice Agent - Document Processing", version="1.0.0")

templates_dir = BASE_DIR / "templates"
templates_dir.mkdir(exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health():
    return {"status": "ok", "service": "invoice-agent"}

@app.post("/api/extract")
async def api_extract(file: UploadFile = File(...)):
    """
    Upload invoice image/PDF and extract structured data
    """
    try:
        # Save uploaded file
        file_id = str(uuid.uuid4())[:8]
        suffix = Path(file.filename).suffix or ".png"
        saved_path = UPLOAD_DIR / f"{file_id}{suffix}"
        
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Saved uploaded file to {saved_path}")
        
        # Extract
        extraction = extract_invoice(saved_path)
        extraction.source_file = str(saved_path)
        
        # Validate
        validation = validate_extraction(extraction)
        
        # Write to sheets/CSV (optional)
        # writer = SheetsWriter()
        # writer.write([(extraction, validation)])
        
        return {
            "status": "success",
            "file": file.filename,
            "saved_path": str(saved_path),
            "extraction": extraction.model_dump(),
            "validation": validation.model_dump(),
            "needs_review": validation.needs_review
        }
    
    except Exception as e:
        logger.exception(f"Extraction failed: {e}")
        return JSONResponse(status_code=500, content={"status": "error", "error": str(e)})

@app.get("/api/demo-invoices")
async def demo_invoices():
    """
    List demo invoices
    """
    invoices = []
    for img_path in sorted(DEMO_DATA_PATH.glob("*.png")):
        json_path = img_path.with_suffix('.json')
        if json_path.exists():
            import json
            with open(json_path) as f:
                gt = json.load(f)
            invoices.append({
                "id": img_path.stem,
                "image": f"/demo-data/invoices/{img_path.name}",
                "ground_truth": gt,
                "is_low_quality": gt.get("low_quality", False)
            })
    return {"invoices": invoices, "count": len(invoices)}

if __name__ == "__main__":
    import uvicorn
    from .config import APP_HOST, APP_PORT
    uvicorn.run("src.app:app", host=APP_HOST, port=APP_PORT, reload=True)
