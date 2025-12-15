# app.py
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from crypto_utils import encrypt_payload, decrypt_payload  # ← added decrypt_payload
from cryptography.exceptions import InvalidTag
import os
from datetime import datetime
import qrcode
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Folders
OUTPUT_DIR = "static/downloads"
QR_DIR = "static/qrcodes"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(QR_DIR, exist_ok=True)

# Use your actual domain in production!
BASE_URL = "http://localhost:5000"   # ← Change to https://yourdomain.com later


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        raw_names = request.form.get("names", "").strip()
        if not raw_names:
            flash("Please provide names!", "error")
            return redirect(url_for("index"))

        names = [n.strip() for n in raw_names.splitlines() if n.strip()]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_filename = f"tokens_{timestamp}.txt"
        txt_filepath = os.path.join(OUTPUT_DIR, txt_filename)

        results = []

        with open(txt_filepath, "w", encoding="utf-8") as f:
            for idx, full_name in enumerate(names, 1):
                first_name = full_name.split(maxsplit=1)[0].capitalize()

                payload = {
                    "name": full_name,
                    "cert_id": f"SKY-{datetime.now().year}-{idx:04d}",
                    "issued_at": datetime.now().strftime("%Y-%m-%d"),
                }

                token = encrypt_payload(payload)

                # === QR Code now contains SHORT URL (much cleaner when scanned) ===
                verify_url = f"{BASE_URL}/verify/{token}"
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(verify_url)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                # Save QR file
                qr_filename = f"{first_name}_{payload['cert_id']}.png"
                qr_path = os.path.join(QR_DIR, qr_filename)
                img.save(qr_path)

                # Base64 for inline display
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                img_b64 = base64.b64encode(buffer.getvalue()).decode()

                # Write to TXT
                f.write(f"{first_name}: {token}\n")

                results.append({
                    "first_name": first_name,
                    "full_name": full_name,
                    "cert_id": payload["cert_id"],
                    "token": token,
                    "qr_image_b64": img_b64,
                    "qr_download": f"qrcodes/{qr_filename}",
                    "verify_url": verify_url,
                })

        return render_template(
            "results.html",
            results=results,
            txt_download=url_for("download_txt", filename=txt_filename),
            txt_filename=txt_filename,
        )

    return render_template("index.html")


@app.route("/download/<filename>")
def download_txt(filename):
    return send_file(os.path.join(OUTPUT_DIR, filename), as_attachment=True)


# ==================== VERIFICATION PAGE ====================
@app.route("/verify", methods=["GET", "POST"])
@app.route("/verify/<token>", methods=["GET"])
def verify(token=None):
    result = None
    error = None

    if request.method == "POST":
        token = request.form.get("token", "").strip()

    if token:
        try:
            data = decrypt_payload(token)
            result = {
                "name": data.get("name", "Unknown"),
                "cert_id": data.get("cert_id", "N/A"),
                "issued_at": data.get("issued_at", "N/A"),
                "valid": True
            }
        except InvalidTag:
            error = "Invalid or tampered token!"
        except Exception as e:
            error = "Failed to decrypt token. It may be corrupted."

    return render_template("verify.html", result=result, error=error, token=token)


if __name__ == "__main__":
    app.run(debug=True)