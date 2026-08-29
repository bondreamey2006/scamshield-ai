from PIL import Image, ImageDraw
import os
import io

os.makedirs("demo_assets", exist_ok=True)

def create_base_receipt():
    img = Image.new('RGB', (400, 600), color='white')
    d = ImageDraw.Draw(img)
    d.rectangle([(20, 20), (380, 580)], outline="black", width=2)
    d.text((120, 50), "Payment Success", fill="green")
    d.text((50, 200), "Amount: Rs. 500.00", fill="black") 
    return img

# Clean Version
clean = create_base_receipt()
clean.save("demo_assets/6_clean_receipt.jpg", "JPEG", quality=100)

# Forged Version (ELA anomaly trigger)
forged = create_base_receipt()
d = ImageDraw.Draw(forged)
d.rectangle([(130, 190), (300, 220)], fill="white")
d.text((135, 200), "Rs. 10000.00", fill="red")
temp = io.BytesIO()
forged.save(temp, "JPEG", quality=15)
temp.seek(0)
Image.open(temp).save("demo_assets/7_forged_receipt.jpg", "JPEG", quality=95)

print("✅ Demo receipts created in demo_assets/")