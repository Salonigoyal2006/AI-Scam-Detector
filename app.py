from flask import Flask, render_template, request
import os
import easyocr

app = Flask(__name__)

# ==========================================
# UPLOAD FOLDER
# ==========================================

UPLOAD_FOLDER = "uploads"

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ==========================================
# OCR READER
# ==========================================

reader = easyocr.Reader(['en'])

# ==========================================
# SCAM DATABASE
# ==========================================

scam_database = {

    "Banking Scam": [
        "otp",
        "verify",
        "bank account",
        "account suspended",
        "blocked",
        "urgent",
        "immediately"
    ],

    "UPI Scam": [
        "upi",
        "upi pin",
        "refund",
        "payment failed",
        "transfer"
    ],

    "Lottery Scam": [
        "winner",
        "lottery",
        "claim prize",
        "reward",
        "congratulations",
        "won",
        "cash prize",
        "lucky draw"
    ],

    "KYC Scam": [
        "kyc",
        "update account",
        "verify account"
    ]
}

# ==========================================
# AI SCAM DETECTION FUNCTION
# ==========================================

def detect_scam(text):

    text = text.lower()

    score = 0

    found_words = []

    categories = []

    keyword_scores = {

        "otp": 25,
        "upi": 25,
        "upi pin": 30,

        "verify": 15,
        "bank account": 20,
        "account suspended": 30,
        "blocked": 20,

        "refund": 20,
        "payment failed": 20,
        "transfer": 20,

        "winner": 35,
        "lottery": 35,
        "claim prize": 35,
        "reward": 20,
        "congratulations": 20,
        "won": 35,
        "cash prize": 35,
        "lucky draw": 35,

        "kyc": 25,
        "update account": 20,
        "verify account": 20,

        "urgent": 15,
        "immediately": 15,
        "click link": 20
    }

    for category, keywords in scam_database.items():

        category_found = False

        for word in keywords:

            if word in text:

                score += keyword_scores.get(word, 10)

                found_words.append(word)

                category_found = True

        if category_found:
            categories.append(category)

    # ======================================
    # BONUS AI RULES
    # ======================================

    if "otp" in found_words and "upi" in found_words:
        score += 20

    if "winner" in found_words or "lottery" in found_words:
        score += 20

    if "click link" in text:
        score += 15

    score = min(score, 100)

    # ======================================
    # CLASSIFICATION
    # ======================================

    if score >= 70:
        result = "SCAM"

    elif score >= 40:
        result = "SUSPICIOUS"

    else:
        result = "SAFE"

    return result, score, found_words, categories


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# CHAT ANALYZER
# ==========================================

@app.route("/analyze", methods=["GET", "POST"])
def analyze():

    if request.method == "POST":

        chat = request.form.get("chat", "")

        result, score, found_words, categories = detect_scam(chat)

        return render_template(
            "result.html",
            result=result,
            score=score,
            found_words=found_words,
            categories=categories,
            chat=chat
        )

    return render_template("analyze.html")


# ==========================================
# SCREENSHOT OCR SCAN
# ==========================================

@app.route("/screenshot", methods=["GET", "POST"])
def screenshot():

    if request.method == "POST":

        image = request.files["image"]

        filepath = os.path.join(
            UPLOAD_FOLDER,
            image.filename
        )

        image.save(filepath)

        results = reader.readtext(filepath)

        extracted_text = ""

        for item in results:
            extracted_text += item[1] + " "

        result, score, found_words, categories = detect_scam(
            extracted_text
        )

        return render_template(
            "result.html",
            result=result,
            score=score,
            found_words=found_words,
            categories=categories,
            chat=extracted_text
        )

    return render_template("screenshot.html")


# ==========================================
# VOICE SCAN PAGE
# ==========================================

@app.route("/voice")
def voice():
    return render_template("voice.html")


# ==========================================
# AWARENESS PAGE
# ==========================================

@app.route("/awareness")
def awareness():
    return render_template("awareness.html")


# ==========================================
# ABOUT PAGE
# ==========================================

@app.route("/about")
def about():
    return render_template("about.html")


# ==========================================
# RUN APP
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
    