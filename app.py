from flask import Flask, render_template, jsonify, request, send_file
import sqlite3
import io
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

app = Flask(__name__)
DB_NAME = "database.db"

# Database initialization
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS attempts (
            id TEXT PRIMARY KEY,
            student_name TEXT,
            college_name TEXT,
            score INTEGER,
            total INTEGER,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Simulated Fraud Scenarios
SCENARIOS = [
    {
        "id": "elec_01",
        "title": "Bijli Bill Disconnection Notice",
        "type": "sms",
        "sender": "+91 98765 43210",
        "body": "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM because previous month bill not updated. Immediately contact our officer: 9876543210.",
        "category": "Fear & Urgency (SMS)",
        "fakeUrl": "None (Direct Call Trap)",
        "realDomain": "Official Discom Portal / Helpline 1912",
        "urgencyTrigger": "Disconnection threat within 2 hours",
        "explanation": "Discoms kabhi 10-digit mobile number se threat nahi bhejte. Call karne par ye AnyDesk/TeamViewer install karwate hain.",
        "goldenRule": "Bijli helpline hamesha 1912 hoti hai. SMS ke number par kabhi call na karein.",
        "isScam": True
    },
    {
        "id": "upi_02",
        "title": "₹1,250 Cashback Reward",
        "type": "upi",
        "sender": "Rewards Department",
        "body": "Congratulations! You won ₹1,250 Cashback on Google Pay. Scan QR code and ENTER YOUR UPI PIN to claim reward directly into your bank.",
        "category": "UPI Fraud",
        "fakeUrl": "gpay-cashback.top/claim",
        "realDomain": "In-app rewards only",
        "urgencyTrigger": "Reward expires in 10 mins",
        "explanation": "Scammers fake QR bhejte hain aur PIN mangte hain. Jaise hi PIN enter kiya, paise cut ho jate hain.",
        "goldenRule": "UPI PIN sirf paise BHEJNE ke liye hota hai, PANE (receive) ke liye KABHI PIN nahi lagta.",
        "isScam": True
    },
    {
        "id": "kyc_03",
        "title": "SBI Account Suspended",
        "type": "sms",
        "sender": "VK-SBISMS",
        "body": "Dear SBI User, your NetBanking access is suspended due to expired KYC. Update PAN immediately here: http://sbi-kyc-update.top",
        "category": "Phishing Link",
        "fakeUrl": "sbi-kyc-update.top",
        "realDomain": "onlinesbi.sbi",
        "urgencyTrigger": "Immediate suspension",
        "explanation": "Domain dekhein: '.top' ek sasta fraudulent domain hai. Bank SMS mein kabhi direct credentials update link nahi bhejta.",
        "goldenRule": "SMS ke links par click karke kabhi password, PAN ya OTP na dalein.",
        "isScam": True
    },
    {
        "id": "job_04",
        "title": "Part-Time YouTube Like Job",
        "type": "whatsapp",
        "sender": "HR Global Hiring",
        "body": "Earn ₹3,000 to ₹5,000 daily from home! Just like YouTube videos & review hotels. Daily payout via UPI. Tap link to join Telegram VIP group.",
        "category": "Task / Prepaid Scam",
        "fakeUrl": "t.me/daily_task_vip",
        "realDomain": "No legitimate hiring platform",
        "urgencyTrigger": "Only 3 slots available",
        "explanation": "Starting ke 2 tasks par ₹150 dekar trust jeette hain, fir 'VIP deposit' ke naam par lakho rupaye loot lete hain.",
        "goldenRule": "Video like karne ke hazaro rupaye koi nahi deta. Har prepaid task job fraud hota hai.",
        "isScam": True
    }
]

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/scenarios", methods=["GET"])
def get_scenarios():
    return jsonify(SCENARIOS)

@app.route("/api/submit", methods=["POST"])
def submit_attempt():
    data = request.json
    attempt_id = "CEP-" + uuid.uuid4().hex[:8].upper()
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(
        "INSERT INTO attempts VALUES (?, ?, ?, ?, ?, ?)",
        (attempt_id, data.get("name"), data.get("college"), data.get("score"), len(SCENARIOS), datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True, "verificationId": attempt_id})

@app.route("/api/certificate", methods=["GET"])
def download_certificate():
    name = request.args.get("name", "Student Participant")
    college = request.args.get("college", "Engineering & Poly College")
    score = request.args.get("score", "100")
    cert_id = request.args.get("id", "CEP-VERIFIED")

    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Background Navy Frame
    p.setFillColor(colors.HexColor("#0B132B"))
    p.rect(0, 0, width, height, fill=True, stroke=False)

    # Inner Gold Border
    p.setStrokeColor(colors.HexColor("#F39C12"))
    p.setLineWidth(4)
    p.rect(0.4 * inch, 0.4 * inch, width - 0.8 * inch, height - 0.8 * inch, stroke=True, fill=False)

    # Inner Accent Card
    p.setFillColor(colors.HexColor("#1C2541"))
    p.roundRect(0.6 * inch, 0.6 * inch, width - 1.2 * inch, height - 1.2 * inch, 12, fill=True, stroke=False)

    # Header
    p.setFillColor(colors.HexColor("#F39C12"))
    p.setFont("Helvetica-Bold", 14)
    p.drawCentredString(width / 2.0, height - 1.2 * inch, "COMMUNITY ENGAGEMENT PROGRAM (CEP) - PROBLEM 07")

    p.setFillColor(colors.white)
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width / 2.0, height - 1.7 * inch, "CERTIFICATE OF DIGITAL SAFETY & VIGILANCE")

    p.setFont("Helvetica", 12)
    p.setFillColor(colors.HexColor("#A0AEC0"))
    p.drawCentredString(width / 2.0, height - 2.2 * inch, "This is proudly presented to certify that")

    # Candidate Name
    p.setFont("Helvetica-Bold", 26)
    p.setFillColor(colors.HexColor("#48BB78"))
    p.drawCentredString(width / 2.0, height - 2.8 * inch, name.upper())

    p.setFont("Helvetica", 12)
    p.setFillColor(colors.white)
    p.drawCentredString(width / 2.0, height - 3.2 * inch, f"of {college}")

    # Description
    p.setFont("Helvetica", 11)
    p.setFillColor(colors.HexColor("#CBD5E0"))
    desc = f"has demonstrated cyber vigilance by scoring {score}% on simulated Indian fraud scenarios"
    p.drawCentredString(width / 2.0, height - 3.7 * inch, desc)
    p.drawCentredString(width / 2.0, height - 4.0 * inch, "(UPI Frauds, Phishing SMS, Call Traps & Task Scams).")

    # Footer Info
    p.setFont("Helvetica-Bold", 10)
    p.setFillColor(colors.HexColor("#F39C12"))
    p.drawString(1.0 * inch, 1.2 * inch, f"VERIFICATION ID: {cert_id}")
    p.drawString(1.0 * inch, 0.9 * inch, f"ISSUED DATE: {datetime.now().strftime('%d %B %Y')}")

    p.drawRightString(width - 1.0 * inch, 1.2 * inch, "CEP CYBER SAFETY CELL")
    p.drawRightString(width - 1.0 * inch, 0.9 * inch, "National Online Safety Initiative")

    p.showPage()
    p.save()
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"{name}_CEP_Certificate.pdf", mimetype='application/pdf')

if __name__ == "__main__":
    app.run(debug=True, port=5000)