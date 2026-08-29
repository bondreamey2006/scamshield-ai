import qrcode
import os

os.makedirs("demo_assets", exist_ok=True)

fixtures = {
    "1_trusted_merchant.png": "upi://pay?pa=demo_trusted_merchant@bank&pn=DemoStore&am=500.00",
    "2_caution_unknown.png": "upi://pay?pa=demo_caution_unknown@okaxis&pn=UnknownUser",
    "3_flagged_scammer.png": "upi://pay?pa=demo_flagged_scammer@paytm&pn=FakeSupport",
    "4_malformed_invalid.png": "upi://pay?pa=invalid_format_no_at_symbol&pn=ErrorTest",
    "5_intent_mismatch.png": "upi://collect?pa=demo_trusted_merchant@bank&am=10000.00"
}

for filename, payload in fixtures.items():
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(payload)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    filepath = os.path.join("demo_assets", filename)
    img.save(filepath)
    print(f"Generated: {filepath}")

print("✅ All QR fixtures generated successfully.")