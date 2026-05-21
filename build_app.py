import os
import base64

# Load the base64 encoded JSZip from the scratch directory
jszip_b64_path = r"C:\Users\Angel\.gemini\antigravity-ide\brain\e785b3d1-d6e8-4096-be3d-3ef38f987026\scratch\jszip_b64.txt"
with open(jszip_b64_path, "r") as f:
    jszip_b64_content = f.read().strip()

# Load the portal.html content and base64-encode it
portal_html_path = "portal.html"
with open(portal_html_path, "rb") as f:
    portal_html_data = f.read()
portal_html_b64 = base64.b64encode(portal_html_data).decode("utf-8")

# Load the index.html content and base64-encode it
index_html_path = "index.html"
with open(index_html_path, "rb") as f:
    index_html_data = f.read()
index_html_b64 = base64.b64encode(index_html_data).decode("utf-8")

# Load the touch.jpg content and base64-encode it
touch_jpg_path = "touch.jpg"
if os.path.exists(touch_jpg_path):
    with open(touch_jpg_path, "rb") as f:
        touch_jpg_data = f.read()
    touch_jpg_b64 = base64.b64encode(touch_jpg_data).decode("utf-8")
else:
    touch_jpg_b64 = ""

# Load the background video and base64-encode it
bg_video_path = "davinci.mp4"
if os.path.exists(bg_video_path):
    with open(bg_video_path, "rb") as f:
        bg_video_data = f.read()
    bg_video_b64 = base64.b64encode(bg_video_data).decode("utf-8")
else:
    bg_video_b64 = ""

# Template for app.py
app_code_template = """import os
import sys

import ctypes

# Hide console window immediately on Windows if frozen
# Also patch stdout/stderr to devnull — windowed EXE sets them to None,
# which causes uvicorn's formatter to crash on .isatty() call.
if getattr(sys, 'frozen', False):
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd != 0:
        ctypes.windll.user32.ShowWindow(hwnd, 0)
    if sys.stdout is None:
        sys.stdout = open(os.devnull, 'w')
    if sys.stderr is None:
        sys.stderr = open(os.devnull, 'w')

import socket
import qrcode
import tkinter as tk
from tkinter import filedialog
import uvicorn
from fastapi import FastAPI, UploadFile, File, Form, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
import threading
import zipfile
import shutil
import queue
from pathlib import Path
import time
from datetime import datetime
import base64
import secrets
import webbrowser
import io

# Base configuration
PORT = 8080
UPLOAD_TOKEN = secrets.token_hex(4)
log_queue = queue.Queue()
SHARED_FILES = {}
last_heartbeat = time.time()  # tracks when browser last pinged

def get_local_ips():
    ips = []
    try:
        # Connect to a dummy external address to find primary routing IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if ip and ip != "127.0.0.1":
            ips.append(ip)
    except Exception:
        pass
    
    # Fallback/Additional check using socket.getaddrinfo
    try:
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("172."):
                if ip not in ips:
                    ips.append(ip)
    except Exception:
        pass
        
    if not ips:
        ips = ["127.0.0.1"]
    return ips

# Initialize save directory in user's Downloads folder
DEFAULT_SAVE_DIR = os.path.join(str(Path.home() / "Downloads"), "GhostDrop")
SAVE_DIR = DEFAULT_SAVE_DIR
os.makedirs(SAVE_DIR, exist_ok=True)

# Detect host IP
HOST_IP = get_local_ips()[0]
TARGET_URL = f"http://{HOST_IP}:{PORT}/{UPLOAD_TOKEN}"

# Base64 assets embedded for offline use
JSZIP_B64 = "JSZIP_B64_PLACEHOLDER"
PORTAL_HTML_B64 = "PORTAL_HTML_B64_PLACEHOLDER"
INDEX_HTML_B64 = "INDEX_HTML_B64_PLACEHOLDER"
TOUCH_JPG_B64 = "TOUCH_JPG_B64_PLACEHOLDER"
BG_VIDEO_B64 = "BG_VIDEO_B64_PLACEHOLDER"

# Decode HTML at runtime
PORTAL_HTML_CONTENT = base64.b64decode(PORTAL_HTML_B64).decode("utf-8")
INDEX_HTML_CONTENT = base64.b64decode(INDEX_HTML_B64).decode("utf-8")

# Create FastAPI app
app = FastAPI(title="GhostDrop Server")

# Allow CORS for direct mobile device connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def log_message(msg):
    timestamp = datetime.now().strftime("[%H:%M:%S]")
    log_queue.put(f"{timestamp} {msg}")
    print(f"{timestamp} {msg}")

def generate_qr_buffer(url):
    qr = qrcode.QRCode(version=1, box_size=5, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="#201d1d", back_color="#fdfcfc")
    buffer = io.BytesIO()
    if type(qr_img).__name__ == "PyPNGImage":
        qr_img.save(buffer)
    else:
        try:
            qr_img.save(buffer, format="PNG")
        except TypeError:
            qr_img.save(buffer)
    buffer.seek(0)
    return buffer.getvalue()

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    return INDEX_HTML_CONTENT

@app.get(f"/{UPLOAD_TOKEN}", response_class=HTMLResponse)
async def serve_portal():
    log_message("Phone connected.")
    return PORTAL_HTML_CONTENT

@app.get("/qr.png")
async def get_qr_code(url: str = None):
    target = url if url else f"http://{HOST_IP}:{PORT}/{UPLOAD_TOKEN}"
    qr_data = generate_qr_buffer(target)
    return Response(content=qr_data, media_type="image/png")

@app.get("/static/jszip.min.js")
async def serve_jszip():
    js_content = base64.b64decode(JSZIP_B64)
    return Response(content=js_content, media_type="application/javascript")

@app.get("/touch.jpg")
async def serve_touch_jpg():
    if os.path.exists("touch.jpg"):
        return FileResponse("touch.jpg")
    elif TOUCH_JPG_B64:
        content = base64.b64decode(TOUCH_JPG_B64)
        return Response(content=content, media_type="image/jpeg")
    return HTMLResponse("Image not found", status_code=404)

@app.get("/davinci.mp4")
async def serve_bg_video():
    if os.path.exists("davinci.mp4"):
        return FileResponse("davinci.mp4", media_type="video/mp4")
    elif BG_VIDEO_B64:
        content = base64.b64decode(BG_VIDEO_B64)
        return Response(content=content, media_type="video/mp4")
    return HTMLResponse("Video not found", status_code=404)

@app.get("/api/initial-data")
async def api_initial_data():
    shares = []
    for token, info in SHARED_FILES.items():
        shares.append({
            "token": token,
            "filename": info["filename"],
            "size": info["size"],
            "download_url": f"http://{HOST_IP}:{PORT}/download/{token}"
        })
    return {
        "target_url": f"http://{HOST_IP}:{PORT}/{UPLOAD_TOKEN}",
        "save_dir": SAVE_DIR,
        "upload_token": UPLOAD_TOKEN,
        "active_shares": shares
    }

@app.post("/api/select-share-file")
async def api_select_share_file():
    global SHARED_FILES
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        selected_file = filedialog.askopenfilename(title="Select File to Share")
        root.destroy()
        if selected_file:
            abs_path = os.path.abspath(selected_file)
            filename = os.path.basename(abs_path)
            token = secrets.token_hex(8)
            file_size = os.path.getsize(abs_path)
            SHARED_FILES[token] = {
                "path": abs_path,
                "filename": filename,
                "size": file_size
            }
            download_url = f"http://{HOST_IP}:{PORT}/download/{token}"
            log_message(f"Sharing file: {filename} ({file_size} bytes)")
            return {
                "status": "success",
                "token": token,
                "filename": filename,
                "size": file_size,
                "download_url": download_url
            }
    except Exception as e:
        log_message(f"File picker error: {str(e)}")
    return {"status": "cancelled"}

@app.post("/api/cancel-share/{token}")
async def api_cancel_share(token: str):
    if token in SHARED_FILES:
        info = SHARED_FILES.pop(token)
        log_message(f"Stopped sharing file: {info['filename']}")
        return {"status": "success"}
    return {"status": "not_found"}

@app.get("/download/{token}")
async def download_file(token: str):
    if token in SHARED_FILES:
        info = SHARED_FILES[token]
        file_path = info["path"]
        filename = info["filename"]
        if os.path.exists(file_path):
            log_message(f"File downloaded by client: {filename}")
            return FileResponse(
                path=file_path,
                filename=filename,
                media_type="application/octet-stream"
            )
        else:
            log_message(f"Download error: File not found at {file_path}")
            return HTMLResponse("File not found on host", status_code=404)
    return HTMLResponse("Invalid download token or link expired", status_code=404)

@app.post("/api/select-folder")
async def api_select_folder():
    global SAVE_DIR
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        selected_dir = filedialog.askdirectory(initialdir=SAVE_DIR, title="Select Save Folder")
        root.destroy()
        if selected_dir:
            SAVE_DIR = os.path.abspath(selected_dir)
            log_message(f"Save path updated: {SAVE_DIR}")
            return {"save_dir": SAVE_DIR}
    except Exception as e:
        log_message(f"Directory picker error: {str(e)}")
    return {"save_dir": None}

@app.post("/api/open-folder")
async def api_open_folder():
    try:
        os.startfile(SAVE_DIR)
        return {"status": "success"}
    except Exception as e:
        log_message(f"Open folder error: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/api/scan-networks")
async def api_scan_networks():
    global HOST_IP, TARGET_URL
    try:
        ips = get_local_ips()
        if ips:
            HOST_IP = ips[0]
            TARGET_URL = f"http://{HOST_IP}:{PORT}/{UPLOAD_TOKEN}"
            log_message(f"Network interfaces scanned. Active target: {TARGET_URL}")
        return {"target_url": TARGET_URL}
    except Exception as e:
        log_message(f"Network scan error: {str(e)}")
        return {"target_url": TARGET_URL}

@app.get("/api/logs")
async def api_get_logs():
    logs = []
    while not log_queue.empty():
        logs.append(log_queue.get_nowait())
    return {"logs": logs}

@app.post("/api/heartbeat")
async def api_heartbeat():
    global last_heartbeat
    last_heartbeat = time.time()
    return {"status": "ok"}

@app.post("/api/shutdown")
async def api_shutdown():
    log_message("Shutdown signal received. Exiting...")
    def self_destruct():
        time.sleep(0.5)
        os._exit(0)
    threading.Thread(target=self_destruct, daemon=True).start()
    return {"status": "shutting_down"}

@app.post("/upload-chunk")
async def upload_chunk(
    file: UploadFile = File(...),
    filename: str = Form(...),
    upload_id: str = Form(...),
    chunk_index: int = Form(...),
    total_chunks: int = Form(...)
):
    global SAVE_DIR
    
    # Store chunks inside a hidden temp subdirectory of SAVE_DIR
    temp_session_dir = os.path.join(SAVE_DIR, ".tmp_uploads", upload_id)
    os.makedirs(temp_session_dir, exist_ok=True)
    
    part_path = os.path.join(temp_session_dir, f"{chunk_index}.part")
    
    # Save the chunk data
    with open(part_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
    # Check if all parts have been received
    received_parts = os.listdir(temp_session_dir)
    
    if len(received_parts) == total_chunks:
        # Assemble files
        final_path = os.path.join(SAVE_DIR, filename)
        
        # Deduplicate final filename if it already exists
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(final_path):
            final_path = os.path.join(SAVE_DIR, f"{base}_{counter}{ext}")
            counter += 1
            
        log_message(f"Assembling {filename} ({total_chunks} parts)...")
        
        with open(final_path, "wb") as outfile:
            for i in range(total_chunks):
                part_file = os.path.join(temp_session_dir, f"{i}.part")
                with open(part_file, "rb") as infile:
                    shutil.copyfileobj(infile, outfile)
                    
        # Remove temporary chunk folder
        shutil.rmtree(temp_session_dir)
        
        log_message(f"Saved file: {os.path.basename(final_path)}")
        
        # Check if zip for extraction
        if final_path.endswith(".zip"):
            threading.Thread(target=extract_zip_archive, args=(final_path, SAVE_DIR), daemon=True).start()
            
    return {"status": "success", "chunk": chunk_index}

def extract_zip_archive(zip_path, extract_dir):
    try:
        folder_name = os.path.basename(zip_path).replace(".zip", "")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_folder = os.path.join(extract_dir, f"{folder_name}_{timestamp}")
        os.makedirs(target_folder, exist_ok=True)
        
        log_message(f"Extracting zip archive: {os.path.basename(zip_path)}...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_folder)
            
        os.remove(zip_path)
        log_message(f"Zip extracted successfully to: {os.path.basename(target_folder)}")
    except Exception as e:
        log_message(f"Extraction error: {str(e)}")

def start_server():
    log_message("GhostDrop Server initializing...")
    log_message(f"Web interface serving on: http://127.0.0.1:{PORT}")
    log_message(f"Mobile portal: {TARGET_URL}")
    log_message(f"Download output bound to: {SAVE_DIR}")
    
    def auto_open():
        time.sleep(0.8)
        webbrowser.open(f"http://127.0.0.1:{PORT}")
        
    threading.Thread(target=auto_open, daemon=True).start()

    def heartbeat_watchdog():
        # Terminate server if browser has not pinged in 8 seconds.
        global last_heartbeat
        # Give browser time to open and connect before watching
        time.sleep(15)
        # Reset clock so the 8s timeout starts NOW, not from server boot
        last_heartbeat = time.time()
        while True:
            time.sleep(2)
            if time.time() - last_heartbeat > 8:
                log_message("Browser closed. Shutting down GhostDrop...")
                time.sleep(0.3)
                os._exit(0)

    threading.Thread(target=heartbeat_watchdog, daemon=True).start()
    try:
        uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="warning")
    except Exception as e:
        import tkinter.messagebox as messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        messagebox.showerror(
            "GhostDrop Error", 
            f"Failed to start server on port {PORT}.\\n\\n"
            f"Error details: {str(e)}\\n\\n"
            "Please check if another instance of GhostDrop is already running."
        )
        root.destroy()

if __name__ == "__main__":
    start_server()
"""

# Write code to app.py
final_code = app_code_template.replace("JSZIP_B64_PLACEHOLDER", jszip_b64_content)
final_code = final_code.replace("PORTAL_HTML_B64_PLACEHOLDER", portal_html_b64)
final_code = final_code.replace("INDEX_HTML_B64_PLACEHOLDER", index_html_b64)
final_code = final_code.replace("TOUCH_JPG_B64_PLACEHOLDER", touch_jpg_b64)
final_code = final_code.replace("BG_VIDEO_B64_PLACEHOLDER", bg_video_b64)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(final_code)

print("app.py built successfully.")
