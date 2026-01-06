from flask import Flask, request, jsonify, session
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv
from flask_cors import CORS
import smtplib
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.secret_key = os.getenv("FLASK_SECRET_KEY")


@app.route("/health", methods=["POST", "GET"])
def health_check():
    return jsonify({"sucess": "✅ Good....!"}), 200




@app.route("/accept-email-iv", methods=["POST"])
def send_mail():

    # Check method
    if request.method != "POST":
        return jsonify({"error": "❌ Method Not Allowed!"}), 405
    
    # Check API key in headers
    client_key = request.headers.get("X-API-KEY")
    if client_key != os.getenv("ROUT_API_KEY"):
        return jsonify({"error": "❌ Unauthorized"}), 401
    
    # Check JSON
    if not request.is_json:
        return jsonify({"error": "JSON required"}), 400
    
    data = request.get_json()

    # check the missing value
    required_fields = ["subject", "body", "receiver_email", "body_type"]
    missing = [f for f in required_fields if f not in data or not data[f]]
    if missing:
        return jsonify({"error": "Missing required fields", "fields": missing}), 400

    # get data from the json
    subject = data.get("subject", "").strip()
    body = data.get("body", "").strip()
    receiver_email = data.get("receiver_email", "").strip()
    body_type = data.get("body_type", "").strip()

    # try to sent mail
    try:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        sender_email = os.getenv("EMAIL_USER")
        sender_pass = os.getenv("EMAIL_PASSWORD")

        if not all([smtp_host, smtp_port, sender_email, sender_pass]):
            return jsonify({"error": "Missing some Internal Credential Contact To The Authority"}), 500

        if body_type not in ("html", "text"):
            return jsonify({"error": "Body Type Not Allowed"}), 400

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email

        mime_subtype = "html" if body_type == "html" else "plain"
        msg.attach(MIMEText(body, mime_subtype, "utf-8"))

        with smtplib.SMTP_SSL(smtp_host, 465, timeout=10) as server:
            server.set_debuglevel(1)
            server.ehlo()
            server.login(sender_email, sender_pass)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        return jsonify({"sucess": "✅ Email sent successfully!"}), 200

    except Exception as e:
        # return jsonify({"error": "❌ Internal Error!"}), 500
        return jsonify({"error": f"❌ SMTP Error: {str(e)}"}), 500




if __name__ == "__main__":
    app.run()