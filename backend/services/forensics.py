import cv2
import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import re
import io

# Lazy load the OCR reader to prevent startup crashes (WinError 10053)
_reader = None

def get_reader():
    global _reader
    if _reader is None:
        try:
            import easyocr
            _reader = easyocr.Reader(['en'], gpu=False)
        except Exception as e:
            print(f"⚠️ EasyOCR initialization failed (Network/Firewall drop): {e}")
            return None
    return _reader

def perform_ela(image_bytes: bytes, quality: int = 90) -> float:
    """
    Error Level Analysis (ELA): Resaves the image at a known quality and compares
    it to the original. High differences indicate potential splicing or editing.
    """
    try:
        original = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        
        temp_io = io.BytesIO()
        original.save(temp_io, 'JPEG', quality=quality)
        temp_io.seek(0)
        
        compressed = Image.open(temp_io)
        diff = ImageChops.difference(original, compressed)
        
        extrema = diff.getextrema()
        max_diff = max([ex[1] for ex in extrema])
        
        if max_diff == 0:
            return 0.0
            
        scale = 255.0 / max_diff
        enhanced_diff = ImageEnhance.Brightness(diff).enhance(scale)
        np_diff = np.array(enhanced_diff)
        
        return round(float(np.mean(np_diff)), 2)
    except Exception as e:
        print(f"ELA Error: {e}")
        return 0.0

def extract_amount(text_list: list) -> float | None:
    """Finds the first recognizable currency amount in the OCR text."""
    for text in text_list:
        match = re.search(r'(?:₹|rs\.?|inr)?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', text.lower())
        if match:
            clean_num = match.group(1).replace(',', '')
            return float(clean_num)
    return None

def analyze_payment_proof(image_bytes: bytes, expected_amount: float = None) -> dict:
    """
    The core Person 3 Forensics function: Runs OCR and ELA, generates signals.
    """
    signals = []
    
    # 1. Run EasyOCR safely using lazy-load
    try:
        reader = get_reader()
        if reader is None:
            raise ValueError("OCR engine offline due to network restrictions.")
            
        nparr = np.frombuffer(image_bytes, np.uint8)
        img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        ocr_results = reader.readtext(img_cv, detail=0)
    except Exception as e:
        print(f"Forensics Pipeline Exception: {e}")
        return {
            "status": "UNABLE_TO_VERIFY",
            "extracted_amount": None,
            "ela_anomaly_score": None,
            "signals": [{"code": "OCR_FAILED", "severity": "caution", "message": "Image is unreadable or OCR engine is offline."}]
        }

    # 2. Extract Data
    extracted_amount = extract_amount(ocr_results)
    if extracted_amount is None:
        return {
            "status": "UNABLE_TO_VERIFY",
            "extracted_amount": None,
            "ela_anomaly_score": None,
            "signals": [{"code": "NO_AMOUNT_FOUND", "severity": "caution", "message": "Could not extract a valid payment amount."}]
        }

    # 3. Compare with Expected Amount
    if expected_amount:
        if extracted_amount == expected_amount:
            signals.append({"code": "AMOUNT_MATCH", "severity": "success", "message": f"Visible amount matches {expected_amount}."})
        else:
            signals.append({"code": "AMOUNT_MISMATCH", "severity": "danger", "message": f"Expected {expected_amount}, but read {extracted_amount}."})

    # 4. Run Error Level Analysis
    ela_score = perform_ela(image_bytes)
    
    if ela_score > 45.0:
        signals.append({"code": "ELA_ANOMALY", "severity": "danger", "message": "Strong image compression anomalies detected. Possible edit."})

    return {
        "status": "SUCCESS",
        "extracted_amount": extracted_amount,
        "ela_anomaly_score": ela_score,
        "signals": signals
    }