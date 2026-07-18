from mcp.server.fastmcp import FastMCP
from PIL import Image
import pytesseract
import shutil
import os
import json
from pathlib import Path

mcp = FastMCP("mcp-tesseract")

def get_tesseract_cmd() -> str:
    # 1. Check environment variable override
    env_path = os.getenv("TESSERACT_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    # 2. Check standard PATH
    which_path = shutil.which("tesseract")
    if which_path:
        return which_path

    # 3. Check common Windows paths
    if os.name == "nt":
        candidates = [
            Path.home() / "AppData/Local/Programs/Tesseract-OCR/tesseract.exe",
            Path("C:/Program Files/Tesseract-OCR/tesseract.exe"),
            Path("C:/Program Files (x86)/Tesseract-OCR/tesseract.exe"),
        ]
        for c in candidates:
            if c.exists():
                return str(c)
    return "tesseract"

# Configure pytesseract cmd path
pytesseract.pytesseract.tesseract_cmd = get_tesseract_cmd()

@mcp.tool()
def ocr_image_to_text(image_path: str) -> str:
    """Perform Optical Character Recognition (OCR) on an image using Tesseract to extract its text.
    
    Args:
        image_path: The absolute or relative path to the image file (PNG, JPEG, etc.).
    """
    try:
        tess_cmd = pytesseract.pytesseract.tesseract_cmd
        # Validate that the tesseract command actually exists
        if not shutil.which(tess_cmd) and not os.path.exists(tess_cmd):
            return json.dumps({
                "success": False,
                "error": f"Tesseract binary not found at '{tess_cmd}'. Please install Tesseract OCR or set the TESSERACT_PATH env var."
            })
            
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return json.dumps({"success": True, "text": text}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)})

if __name__ == "__main__":
    mcp.run()
