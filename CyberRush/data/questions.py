# data/questions.py
# All cyber-security question content used to label obstacles.
# Each entry has:
#   "label"    : "phishing" (red obstacle — dodge it)
#                "safe"     (green collectible — collect it)
#   "text"     : short label shown ON the obstacle block
#   "tip"      : one-line educational message shown when collected/hit

QUESTIONS = [

    # ── PHISHING (dodge these) ──────────────────────────
    {
        "label": "phishing",
        "text":  "FREE iPhone\nClick Now!",
        "tip":   "PHISHING: Prizes that seem too good to be true always are.",
    },
    {
        "label": "phishing",
        "text":  "support@\npaypa1.com",
        "tip":   "PHISHING: 'paypa1' uses a number 1 — fake sender address!",
    },
    {
        "label": "phishing",
        "text":  "URGENT!\nVerify NOW",
        "tip":   "PHISHING: Urgency pressure is a top scammer tactic.",
    },
    {
        "label": "phishing",
        "text":  "Your account\nSUSPENDED",
        "tip":   "PHISHING: Real banks never suspend via email links.",
    },
    {
        "label": "phishing",
        "text":  "Password:\n123456",
        "tip":   "UNSAFE: Never use simple passwords like 123456.",
    },
    {
        "label": "phishing",
        "text":  "Click this\nunknown link",
        "tip":   "PHISHING: Never click links from unknown senders.",
    },
    {
        "label": "phishing",
        "text":  "Win £500\nGift Card!",
        "tip":   "SCAM: Unsolicited prize offers are always scams.",
    },
    {
        "label": "phishing",
        "text":  "Reuse same\npassword",
        "tip":   "UNSAFE: Reusing passwords lets hackers access everything.",
    },
    {
        "label": "phishing",
        "text":  "HTTP site\n(no lock)",
        "tip":   "UNSAFE: Always check for HTTPS and the padlock icon.",
    },
    {
        "label": "phishing",
        "text":  "Share your\nOTP code",
        "tip":   "PHISHING: Never share one-time passwords with anyone.",
    },

    # ── SAFE (collect these) ────────────────────────────
    {
        "label": "safe",
        "text":  "HTTPS\nSecure Site",
        "tip":   "SAFE: HTTPS means the connection is encrypted.",
    },
    {
        "label": "safe",
        "text":  "2FA\nEnabled",
        "tip":   "SAFE: Two-factor authentication adds a vital second lock.",
    },
    {
        "label": "safe",
        "text":  "Strong\nPassword",
        "tip":   "SAFE: Mix uppercase, lowercase, numbers and symbols.",
    },
    {
        "label": "safe",
        "text":  "Verified\nSender",
        "tip":   "SAFE: Always check the full sender domain before clicking.",
    },
    {
        "label": "safe",
        "text":  "Software\nUpdated",
        "tip":   "SAFE: Updates patch security vulnerabilities.",
    },
    {
        "label": "safe",
        "text":  "Antivirus\nActive",
        "tip":   "SAFE: Antivirus software blocks known malware.",
    },
    {
        "label": "safe",
        "text":  "VPN\nConnected",
        "tip":   "SAFE: A VPN encrypts your internet traffic.",
    },
    {
        "label": "safe",
        "text":  "Privacy\nSettings On",
        "tip":   "SAFE: Review app privacy settings regularly.",
    },
    {
        "label": "safe",
        "text":  "Backup\nComplete",
        "tip":   "SAFE: Regular backups protect against ransomware.",
    },
    {
        "label": "safe",
        "text":  "Locked\nScreen",
        "tip":   "SAFE: Always lock your screen when stepping away.",
    },
]