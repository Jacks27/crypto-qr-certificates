# qr-token-certifier

A lightweight Flask web application for generating secure, verifiable "certificates" (or tokens) in bulk. It creates encrypted tokens for each participant, generates QR codes linking to a public verification page, and provides downloadable QR images and a token list.

Perfect for events, workshops, memberships, or any scenario needing tamper-proof digital credentials without full PDF certificates.

## Features

- **Bulk Input**: Paste a list of full names (one per line) to generate tokens for multiple people at once.
- **Encrypted Tokens**: Payload (name, unique cert ID like `SKY-2025-0001`, issue date) is encrypted using Fernet (from `cryptography` library) for security.
- **QR Codes**: Each QR contains a short verification URL (e.g., `https://yourdomain.com/verify/<token>`). Scanning it directly opens the verification page.
- **Public Verification**: Anyone can visit `/verify` and paste/enter a token (or scan QR) to check authenticity and view details. Invalid/tampered tokens are rejected.
- **Downloads**:
  - Individual QR code PNGs.
  - A TXT file with first name + token pairs.
- **Simple & Secure**: No database needed; runs locally or on any host.

## Demo Screenshots

(Once deployed, add screenshots here of the input page, results page with QRs, and verification page.)

## Requirements

- Python 3.6+
- Flask
- cryptography
- qrcode[pil]

Install dependencies:

```bash
pip install flask cryptography qrcode[pil]