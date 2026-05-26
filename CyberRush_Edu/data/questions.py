# data/questions.py
# Cybersecurity questions used to label obstacles.
#
# Each entry has:
#   "label"     : "phishing" (red — dodge it) or "safe" (green — collect it)
#   "category"  : one of CATEGORIES below — drives stats + review screen
#   "text"      : 1-2 lines shown on the block itself
#   "tip"       : one-line educational message (popup during play)
#   "deep"      : 2-3 line "WHY?" explanation shown on the forced pause
#                 after a hit. Plain English, no jargon.

CATEGORIES = {
    "typosquatting":      "Typosquatting",
    "urgency-pressure":   "Urgency pressure",
    "credential":         "Credential attacks",
    "malware-vector":     "Malware delivery",
    "social-engineering": "Social engineering",
    "system-hygiene":     "System hygiene",
    "network-safety":     "Network safety",
}

QUESTIONS = [

    # ── PHISHING ─────────────────────────────────────────
    {
        "label": "phishing", "category": "social-engineering",
        "text":  "FREE iPhone\nClick Now!",
        "tip":   "PHISHING: Prizes that seem too good to be true always are.",
        "deep":  "Scammers dangle prizes to trigger excitement and bypass "
                 "judgement. Legitimate giveaways never require a click on "
                 "an unsolicited message to claim them.",
    },
    {
        "label": "phishing", "category": "typosquatting",
        "text":  "support@\npaypa1.com",
        "tip":   "PHISHING: 'paypa1' uses a number 1 — fake sender address!",
        "deep":  "Typosquatting swaps letters for similar-looking characters "
                 "(l->1, o->0, rn->m). Always read the sender domain "
                 "character by character before trusting an email.",
    },
    {
        "label": "phishing", "category": "urgency-pressure",
        "text":  "URGENT!\nVerify NOW",
        "tip":   "PHISHING: Urgency pressure is a top scammer tactic.",
        "deep":  "Urgency short-circuits careful thinking. Real companies "
                 "give you time. If a message says ACT NOW or your account "
                 "closes in 24 hours, slow down and check independently.",
    },
    {
        "label": "phishing", "category": "urgency-pressure",
        "text":  "Your account\nSUSPENDED",
        "tip":   "PHISHING: Real banks never suspend via email links.",
        "deep":  "Account-suspension scares are a classic phishing hook. "
                 "Never click the link in the email. Go directly to the "
                 "bank's site by typing the URL or call the number on your "
                 "card.",
    },
    {
        "label": "phishing", "category": "credential",
        "text":  "Password:\n123456",
        "tip":   "UNSAFE: Never use simple passwords like 123456.",
        "deep":  "'123456', 'password' and 'qwerty' are the first guesses "
                 "any attacker tries. Modern hardware can test billions of "
                 "passwords per second — use long unique passphrases.",
    },
    {
        "label": "phishing", "category": "social-engineering",
        "text":  "Click this\nunknown link",
        "tip":   "PHISHING: Never click links from unknown senders.",
        "deep":  "Unknown links can install malware, harvest credentials, "
                 "or fingerprint your device. If you must check one, hover "
                 "to preview the URL or paste into a URL-safety checker.",
    },
    {
        "label": "phishing", "category": "social-engineering",
        "text":  "Win £500\nGift Card!",
        "tip":   "SCAM: Unsolicited prize offers are always scams.",
        "deep":  "Gift cards are popular for scams because they're like "
                 "cash and untraceable. No real company asks you to claim "
                 "a prize by entering your password or paying a fee.",
    },
    {
        "label": "phishing", "category": "credential",
        "text":  "Reuse same\npassword",
        "tip":   "UNSAFE: Reusing passwords lets hackers access everything.",
        "deep":  "Credential stuffing: when one site is breached, attackers "
                 "try the leaked password on hundreds of others. One reused "
                 "password can lose your email, bank and social accounts.",
    },
    {
        "label": "phishing", "category": "network-safety",
        "text":  "HTTP site\n(no lock)",
        "tip":   "UNSAFE: Always check for HTTPS and the padlock icon.",
        "deep":  "Plain HTTP is unencrypted — anyone on your network can "
                 "read your passwords and form data. The padlock means "
                 "HTTPS is on and your data is encrypted in transit.",
    },
    {
        "label": "phishing", "category": "credential",
        "text":  "Share your\nOTP code",
        "tip":   "PHISHING: Never share one-time passwords with anyone.",
        "deep":  "OTPs are the second factor protecting your account. No "
                 "legitimate company, bank or support agent will ever ask "
                 "for one. If they ask, they're trying to steal access.",
    },
    {
        "label": "phishing", "category": "typosquatting",
        "text":  "amaz0n.com\nlogin",
        "tip":   "PHISHING: Typosquatted domains swap letters for numbers.",
        "deep":  "Fake login pages on lookalike domains capture credentials "
                 "from anyone who doesn't look closely at the URL bar. "
                 "Bookmark login pages and use those rather than email links.",
    },
    {
        "label": "phishing", "category": "malware-vector",
        "text":  "Pay invoice\n.zip attached",
        "tip":   "PHISHING: Unexpected .zip attachments often hide malware.",
        "deep":  "Compressed attachments bypass many email scanners. If you "
                 "didn't expect an invoice from this sender, confirm by "
                 "phone before opening anything inside the zip.",
    },
    {
        "label": "phishing", "category": "social-engineering",
        "text":  "Boss needs\ngift cards",
        "tip":   "SCAM: Real bosses don't urgently ask for gift cards.",
        "deep":  "Business email compromise (BEC) impersonates executives "
                 "and pressures staff to buy gift cards. Always confirm in "
                 "person or via a known phone number before any urgent buy.",
    },
    {
        "label": "phishing", "category": "malware-vector",
        "text":  "Enable macros\nto view",
        "tip":   "PHISHING: Macros in office docs can install malware.",
        "deep":  "Office macros are mini programs that can run code on your "
                 "machine. A document that begs you to enable macros 'to "
                 "view content' is almost always installing malware.",
    },
    {
        "label": "phishing", "category": "social-engineering",
        "text":  "Tax refund\nclick here",
        "tip":   "SCAM: Tax agencies never request refunds via email links.",
        "deep":  "Tax authorities communicate via postal mail or their "
                 "official portal — and only when you initiate contact. An "
                 "email promising a refund is a phishing lure.",
    },
    {
        "label": "phishing", "category": "malware-vector",
        "text":  "Free USB\nin reception",
        "tip":   "UNSAFE: Found USB sticks may carry malware. Never plug in.",
        "deep":  "USB drop attacks plant infected sticks in offices, hoping "
                 "a curious employee plugs one in. Modern USBs can emulate "
                 "keyboards and execute commands instantly. Hand any found "
                 "drive to IT.",
    },
    {
        "label": "phishing", "category": "network-safety",
        "text":  "Public WiFi\n+ banking",
        "tip":   "UNSAFE: Open WiFi can let attackers intercept your login.",
        "deep":  "Open WiFi has no encryption between you and the access "
                 "point. Anyone nearby can sniff traffic, and rogue "
                 "hotspots can impersonate the real network. Use mobile "
                 "data or a trusted VPN for sensitive activity.",
    },
    {
        "label": "phishing", "category": "credential",
        "text":  "Save password\nin browser",
        "tip":   "RISKY: Browser passwords are easier to steal than a vault.",
        "deep":  "Browser password stores often unlock with no master "
                 "password and can be dumped by malware running as your "
                 "user. A dedicated password manager is far harder to "
                 "compromise.",
    },
    {
        "label": "phishing", "category": "malware-vector",
        "text":  "Photo from\nrandom DM",
        "tip":   "PHISHING: Image attachments from strangers may exploit your viewer.",
        "deep":  "Image and PDF viewers have parsing bugs attackers can "
                 "exploit by getting you to open the file. If you don't "
                 "recognise the sender, don't open the attachment — even "
                 "photos.",
    },
    {
        "label": "phishing", "category": "social-engineering",
        "text":  "Click to\nremove virus",
        "tip":   "SCAM: Pop-ups claiming you have a virus ARE the virus.",
        "deep":  "Scareware pop-ups (loud red banners with fake alarm "
                 "sounds) panic you into installing 'antivirus' that's "
                 "actually malware. Close the tab. Your real antivirus is "
                 "the one you chose.",
    },
    {
        "label": "phishing", "category": "malware-vector",
        "text":  "QR code\nfrom flyer",
        "tip":   "PHISHING: QR codes can hide malicious URLs — verify the link first.",
        "deep":  "QR codes are opaque — you can't see the URL until you "
                 "scan it. Quishing attacks paste fake QR stickers over "
                 "real ones in public places. Most cameras show the URL "
                 "before opening — read carefully.",
    },
    {
        "label": "phishing", "category": "system-hygiene",
        "text":  "Disable\nfirewall",
        "tip":   "UNSAFE: Disabling the firewall exposes your machine.",
        "deep":  "Your firewall blocks unsolicited connections from the "
                 "internet. Turning it off (often suggested by 'helpful' "
                 "tech-support scammers) lets attackers probe your machine "
                 "directly. Leave it on.",
    },

    # ── SAFE ─────────────────────────────────────────────
    {
        "label": "safe", "category": "network-safety",
        "text":  "HTTPS\nSecure Site",
        "tip":   "SAFE: HTTPS means the connection is encrypted.",
        "deep":  "HTTPS encrypts everything between your browser and the "
                 "site so nobody on the network can read it. Always check "
                 "for the padlock before entering passwords or payment.",
    },
    {
        "label": "safe", "category": "credential",
        "text":  "2FA\nEnabled",
        "tip":   "SAFE: Two-factor authentication adds a vital second lock.",
        "deep":  "Even if an attacker steals your password, 2FA stops them "
                 "logging in without a second proof (code, app prompt, "
                 "hardware key). It blocks most credential attacks.",
    },
    {
        "label": "safe", "category": "credential",
        "text":  "Strong\nPassword",
        "tip":   "SAFE: Mix uppercase, lowercase, numbers and symbols.",
        "deep":  "Length is the most important factor. A passphrase of "
                 "4-5 random unrelated words is strong and memorable. "
                 "Avoid personal info attackers can find on social media.",
    },
    {
        "label": "safe", "category": "social-engineering",
        "text":  "Verified\nSender",
        "tip":   "SAFE: Always check the full sender domain before clicking.",
        "deep":  "Read the part after the @ symbol carefully. Is it the "
                 "real company domain or a lookalike? Display names are "
                 "easy to fake — the actual sender address is what matters.",
    },
    {
        "label": "safe", "category": "system-hygiene",
        "text":  "Software\nUpdated",
        "tip":   "SAFE: Updates patch security vulnerabilities.",
        "deep":  "Most successful attacks exploit known bugs patched months "
                 "earlier. Keeping your OS, browser and apps up to date "
                 "closes those holes before attackers can use them.",
    },
    {
        "label": "safe", "category": "system-hygiene",
        "text":  "Antivirus\nActive",
        "tip":   "SAFE: Antivirus software blocks known malware.",
        "deep":  "Modern antivirus uses signatures and behaviour analysis "
                 "to catch most known threats. Not perfect, but combined "
                 "with safe habits it's a strong second line of defence.",
    },
    {
        "label": "safe", "category": "network-safety",
        "text":  "VPN\nConnected",
        "tip":   "SAFE: A VPN encrypts your internet traffic.",
        "deep":  "A trusted VPN wraps your traffic in an encrypted tunnel, "
                 "hiding it from anyone on the local network (cafés, "
                 "airports). Choose a reputable provider — a sketchy VPN "
                 "is worse than no VPN.",
    },
    {
        "label": "safe", "category": "system-hygiene",
        "text":  "Privacy\nSettings On",
        "tip":   "SAFE: Review app privacy settings regularly.",
        "deep":  "Default settings often share more than you'd choose. "
                 "Review what apps can see your location, contacts, photos "
                 "and microphone every few months. Deny what you don't use.",
    },
    {
        "label": "safe", "category": "system-hygiene",
        "text":  "Backup\nComplete",
        "tip":   "SAFE: Regular backups protect against ransomware.",
        "deep":  "Ransomware encrypts your files and demands payment. With "
                 "recent offline backups you can wipe the infection and "
                 "restore — making the attack worthless.",
    },
    {
        "label": "safe", "category": "system-hygiene",
        "text":  "Locked\nScreen",
        "tip":   "SAFE: Always lock your screen when stepping away.",
        "deep":  "An unlocked screen in an office, café or even at home "
                 "gives anyone walking past full access to your accounts, "
                 "files and email. Lock the moment you stand up.",
    },
    {
        "label": "safe", "category": "credential",
        "text":  "Password\nManager",
        "tip":   "SAFE: Password managers create unique strong passwords per site.",
        "deep":  "A password manager generates and stores a unique strong "
                 "password for every site, behind one master password you "
                 "memorise. Eliminates password reuse — the biggest single "
                 "win for personal security.",
    },
    {
        "label": "safe", "category": "typosquatting",
        "text":  "Verify URL\nbefore login",
        "tip":   "SAFE: Always check the address bar before entering credentials.",
        "deep":  "Most phishing lives or dies at the URL. Before typing a "
                 "password, glance at the address bar: is the domain "
                 "exactly what you expect? No extra letters, no lookalike "
                 "characters, real TLD.",
    },
    {
        "label": "safe", "category": "credential",
        "text":  "Hardware\nsecurity key",
        "tip":   "SAFE: Physical keys make phishing of your 2FA almost impossible.",
        "deep":  "Hardware keys (YubiKey, Titan, etc.) verify the site URL "
                 "cryptographically — so even a perfect-looking fake site "
                 "can't trick them. The gold standard for 2FA.",
    },
    {
        "label": "safe", "category": "social-engineering",
        "text":  "Report\nsuspicious email",
        "tip":   "SAFE: Reporting phish helps your whole organisation.",
        "deep":  "Use the 'Report Phishing' button in your mail client. "
                 "Your security team can warn others, block the sender "
                 "and improve filters — turning one spotted phish into "
                 "protection for everyone.",
    },
    {
        "label": "safe", "category": "system-hygiene",
        "text":  "Encrypted\nbackup",
        "tip":   "SAFE: Encrypted backups protect your data if the drive is stolen.",
        "deep":  "An unencrypted backup drive is a copy of your entire "
                 "digital life anyone can read. Always enable backup "
                 "encryption and store the password separately.",
    },
    {
        "label": "safe", "category": "credential",
        "text":  "Sign out on\nshared PC",
        "tip":   "SAFE: Always log out when using a public or shared computer.",
        "deep":  "Public computers (libraries, hotels, classrooms) may "
                 "keep your session active for the next user. Always sign "
                 "out, clear browsing data if you can, and prefer "
                 "private/incognito mode.",
    },
    {
        "label": "safe", "category": "social-engineering",
        "text":  "Verify caller\nID first",
        "tip":   "SAFE: Hang up and call back the official number to confirm.",
        "deep":  "Caller ID is easy to spoof. If someone claiming to be "
                 "from your bank asks for sensitive info, hang up and "
                 "call back using the number on your card or their "
                 "official website — not the number they gave you.",
    },
    {
        "label": "safe", "category": "credential",
        "text":  "Use unique\npasswords",
        "tip":   "SAFE: A unique password per site stops one breach from spreading.",
        "deep":  "When site X gets breached, attackers immediately try "
                 "the leaked password on email, banking and social sites. "
                 "Unique passwords contain the damage to just that site.",
    },
    {
        "label": "safe", "category": "social-engineering",
        "text":  "Check email\nheaders",
        "tip":   "SAFE: Email headers reveal the true sender behind a friendly name.",
        "deep":  "Most email clients let you view 'original' or 'full' "
                 "headers. The Return-Path and Received chain show where "
                 "the message really came from — often very different from "
                 "the friendly display name.",
    },
    {
        "label": "safe", "category": "credential",
        "text":  "Use SSO\nfor work",
        "tip":   "SAFE: Single sign-on with MFA reduces password reuse risk.",
        "deep":  "SSO means one strong monitored login covers many work "
                 "apps. Combined with MFA, it removes the temptation to "
                 "reuse weak passwords across internal tools.",
    },
    {
        "label": "safe", "category": "system-hygiene",
        "text":  "Auto-update\non",
        "tip":   "SAFE: Auto-updates close holes the moment they're patched.",
        "deep":  "The window between a vulnerability being announced and "
                 "attackers exploiting it can be hours. Auto-updates close "
                 "the gap without you needing to remember to install.",
    },
    {
        "label": "safe", "category": "system-hygiene",
        "text":  "Limit app\npermissions",
        "tip":   "SAFE: Grant apps only the permissions they actually need.",
        "deep":  "A calculator doesn't need your location. A game doesn't "
                 "need your contacts. The fewer permissions you grant, "
                 "the less damage any single compromised app can do.",
    },
]
