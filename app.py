#!/usr/bin/env python3
"""
Web interface for batch PDF password removal.
FastAPI version for Render deployment.
"""

import io
import zipfile
import uuid
from pathlib import Path
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import pikepdf

app = FastAPI(title="PDF Password Remover")
templates = Jinja2Templates(directory="templates")

# Temporary storage for processed files
PROCESSED_FILES = {}


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/unlock")
async def unlock_pdfs(
    password: str = Form(""),
    files: list[UploadFile] = File(...)
):
    """Process uploaded PDF files and remove passwords."""
    
    if not files or all(f.filename == "" for f in files):
        raise HTTPException(status_code=400, detail="No files selected")
    
    results = []
    session_id = str(uuid.uuid4())
    processed = []
    
    for file in files:
        if file.filename == "":
            continue
            
        if not file.filename.lower().endswith(".pdf"):
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "Not a PDF file"
            })
            continue
        
        try:
            # Read the file into memory
            file_bytes = await file.read()
            input_stream = io.BytesIO(file_bytes)
            
            # Try to open with password
            with pikepdf.open(input_stream, password=password) as pdf:
                output_stream = io.BytesIO()
                pdf.save(output_stream)
                output_stream.seek(0)
                
                # Store processed file
                new_filename = f"{Path(file.filename).stem}_unlocked.pdf"
                processed.append({
                    "filename": new_filename,
                    "data": output_stream.getvalue()
                })
                
                results.append({
                    "filename": file.filename,
                    "success": True,
                    "output": new_filename
                })
                
        except pikepdf.PasswordError:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": "Wrong password"
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    # Store processed files for download
    if processed:
        PROCESSED_FILES[session_id] = processed
    
    return {
        "session_id": session_id,
        "results": results,
        "success_count": sum(1 for r in results if r["success"]),
        "total_count": len(results)
    }


@app.get("/download/{session_id}")
async def download_files(session_id: str):
    """Download processed files as a ZIP or single PDF."""
    
    if session_id not in PROCESSED_FILES:
        raise HTTPException(status_code=404, detail="Session expired or invalid")
    
    files = PROCESSED_FILES[session_id]
    
    if len(files) == 1:
        # Single file - download directly
        file_data = files[0]
        # Clean up
        del PROCESSED_FILES[session_id]
        
        return StreamingResponse(
            io.BytesIO(file_data["data"]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{file_data["filename"]}"'
            }
        )
    
    # Multiple files - create ZIP
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_data in files:
            zip_file.writestr(file_data["filename"], file_data["data"])
    
    zip_buffer.seek(0)
    
    # Clean up
    del PROCESSED_FILES[session_id]
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": 'attachment; filename="unlocked_pdfs.zip"'
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint for Render."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*50)
    print("PDF Password Remover - Web Interface")
    print("="*50)
    print("Open http://localhost:8000 in your browser")
    print("="*50 + "\n")
    uvicorn.run(app, host="0.0.0.0", port=8000)
