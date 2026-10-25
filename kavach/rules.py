"""Deterministic red-flag checker. No AI here: plain regex, same answer every time.

Why have this at all if we have Gemma?
1. It catches the "never negotiable" signals (asking for OTP/PIN, AnyDesk, digital arrest)
   even if the small model misses them.
2. It gives evidence the judges can audit: every flag points to the exact text that fired it.
3. Its hits are fed to the model as hints, which makes the model more consistent.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from urllib.parse import urlparse

# ---------- entity extraction ----------

URL_RE = re.compile(r"\b((?:https?://|www\.)[^\s<>\"']+|[a-z0-9-]+\.(?:ly|gd|me|top|xyz|click|online|site|info|live|shop|icu|apk)/[^\s<>\"']*)", re.I)
UPI_RE = re.compile(r"\b[a-z0-9][a-z0-9.\-_]{1,255}@[a-z]{2,64}\b", re.I)
PHONE_RE = re.compile(r"(?:\+91[\s-]?|\b0)?\b[6-9]\d{4}[\s-]?\d{5}\b")
AMOUNT_RE = re.compile(r"(?:₹|rs\.?|inr)\s?[\d,]+(?:\.\d+)?", re.I)

SHORTENERS = {"bit.ly", "tinyurl.com", "cutt.ly", "is.gd", "t.ly", "rb.gy", "shorturl.at", "tiny.cc", "goo.su", "ow.ly"}
RISKY_TLDS = (".top", ".xyz", ".click", ".online", ".site", ".info", ".live", ".shop", ".icu", ".buzz", ".rest")
BRAND_WORDS = ("sbi", "hdfc", "icici", "axis", "kotak", "paytm", "phonepe", "gpay", "npci", "uidai", "aadhaar",
               "incometax", "epfo", "bses", "jvvnl", "electricity", "bijli", "indiapost", "bluedart", "fedex", "amazon", "flipkart")
OFFICIAL_SUFFIXES = (".gov.in", ".nic.in", "sbi.co.in", "onlinesbi.sbi", "hdfcbank.com", "icicibank.com", "axisbank.com",
                     "kotak.com", "paytm.com", "phonepe.com", "npci.org.in", "uidai.gov.in", "amazon.in", "flipkart.com",
                     "indiapost.gov.in", "bluedart.com", "fedex.com", "irctc.co.in")


@dataclass
class Flag:
    id: str
    label_en: str
    label_hi: str
    weight: int
    evidence: str = ""
    critical: bool = False  # critical flags force at least a "scam"-level score


@dataclass
class RuleReport:
    flags: list[Flag] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)
    upi_ids: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    amounts: list[str] = field(default_factory=list)

    @property
    def score(self) -> int:
        return min(100, sum(f.weight for f in self.flags))

    @property
    def has_critical(self) -> bool:
        return any(f.critical for f in self.flags)

    def lines_for_prompt(self) -> list[str]:
        return [f"{f.label_en}" + (f": {f.evidence}" if f.evidence else "") for f in self.flags]

    def to_dict(self) -> dict:
        d = asdict(self)
        d["score"] = self.score
        d["has_critical"] = self.has_critical
        return d


# ---------- helpers ----------

def _find(pattern: str, text: str) -> str:
    m = re.search(pattern, text, re.I)
    return m.group(0) if m else ""


def _host(url: str) -> str:
    u = url if url.lower().startswith(("http://", "https://")) else "http://" + url
    return (urlparse(u).hostname or "").lower().removeprefix("www.")


def _is_official(host: str) -> bool:
    return any(host == s.lstrip(".") or host.endswith(s if s.startswith(".") else "." + s) or host == s
               for s in OFFICIAL_SUFFIXES)


# ---------- the rules ----------
# Each rule: (id, english label, hindi label, weight, critical, test-function)
# The test returns evidence text ("" means the rule did not fire).

NEGATION = r"(do not|don'?t|never|kabhi bhi|kisi ko (bhi )?(na|mat)|mat (batayen|batao|share))\s*(share|disclose|tell|batayen|batao)?"
ASK_VERB = r"(share|send|tell|forward|provide|enter|batao|batayen|bhejo|bhej do|daalo|daal do|bata do)"
SECRET = r"(otp|one[- ]time password|upi ?pin|\bpin\b|cvv|password|mpin)"


def r_asks_secret(t: str) -> str:
    near = re.search(rf"{ASK_VERB}[^.\n]{{0,40}}{SECRET}|{SECRET}[^.\n]{{0,40}}{ASK_VERB}", t, re.I)
    if not near:
        return ""
    if re.search(NEGATION, t, re.I) and not re.search(r"(executive|agent|officer|caller|us)\b[^.\n]{0,30}" + SECRET, t, re.I):
        return ""  # e.g. "Do not share your OTP with anyone" is the bank's own warning
    return near.group(0)


def r_receive_needs_pin(t: str) -> str:
    recv = r"(receive|refund|cashback|reward|prize|credited to you|paise (aa|mil)|milenge|claim)"
    act = r"(enter (your )?(upi )?pin|scan (the )?qr|approve (the )?request|accept (the )?request|pin daal)"
    if re.search(recv, t, re.I) and re.search(act, t, re.I):
        return _find(act, t)
    return ""


AUTHORITY = (r"(\bcbi\b|\bed\b|enforcement directorate|narcotics|\bncb\b|\bcustoms\b|cyber ?cell|crime branch|\bpolice\b|\bfir\b|"
             r"arrest warrant|\bcourt\b|\btrai\b|money laundering|digital arrest)")
COERCION = r"(video call|skype|stay on (the )?call|do not (tell|inform)|don'?t tell|confidential|kisi ko mat|arrest|warrant|case (will be|is) (filed|registered)|freeze)"


def r_digital_arrest(t: str) -> str:
    a = _find(AUTHORITY, t)
    if a and re.search(COERCION, t, re.I):
        return a + " + " + _find(COERCION, t)
    return ""


def r_authority_mention(t: str) -> str:
    return "" if r_digital_arrest(t) else _find(AUTHORITY, t)


def r_urgency(t: str) -> str:
    return _find(r"(urgent(ly)?|immediately|within \d+ ?(hours?|hrs|minutes?|mins)|today only|last (chance|warning|reminder)|"
                 r"tonight|turant|abhi ke abhi|jaldi|will be (blocked|suspended|deactivated|disconnected)|band ho jayega|"
                 r"\b24 ?hrs?\b)", t)


def r_kyc_block(t: str) -> str:
    return _find(r"(kyc|pan (card )?(update|link)|aadhaa?r (update|link)|account (will be |is )?(blocked|suspended|frozen)|"
                 r"sim (will be )?(blocked|deactivated)|re-?verify your account)", t)


def r_remote_access(t: str) -> str:
    return _find(r"(anydesk|teamviewer|quick ?support|rustdesk|screen ?share|screen sharing|airdroid)", t)


def r_lottery(t: str) -> str:
    return _find(r"(lottery|lucky draw|lucky winner|you (have )?won|kbc|kaun banega|jackpot|inaam|prize money|gift voucher worth)", t)


def r_job_task(t: str) -> str:
    job = _find(r"(part[- ]?time|work from home|ghar baithe|daily (income|earning)|earn ₹?\d|per task|like (youtube )?videos|"
                r"rate (hotels|products)|telegram (task|group)|prepaid task)", t)
    return job


def r_investment(t: str) -> str:
    return _find(r"(guaranteed (return|profit)|double your money|\d+% (daily|per day|weekly)|trading tips|stock tips|"
                 r"ipo allotment|crypto (profit|investment)|vip group|paisa double)", t)


def r_electricity(t: str) -> str:
    if re.search(r"(electricity|bijli|power|light) ", t, re.I) and re.search(r"(disconnect|cut|kaat|katega|tonight|9:?30)", t, re.I):
        return _find(r"(disconnect\w*|cut|katega|tonight)", t)
    return ""


def r_parcel(t: str) -> str:
    if re.search(r"(parcel|courier|package|consignment|shipment)", t, re.I) and \
       re.search(r"(drugs|illegal|seized|held|customs (duty|fee)|passport|narcotic|redeliver fee|address incomplete)", t, re.I):
        return _find(r"(drugs|illegal|seized|held|customs (duty|fee)|redeliver fee|address incomplete)", t)
    return ""


def r_family(t: str) -> str:
    if re.search(r"(new number|naya number|my number changed|this is your (son|daughter|beta)|mummy|papa|mom|dad|beta)", t, re.I) and \
       re.search(r"(urgent|emergency|send|bhej|transfer|money|paise|hospital|accident)", t, re.I):
        return _find(r"(new number|naya number|my number changed|emergency|hospital|accident)", t) or "relative asks for money"
    return ""


def r_loan(t: str) -> str:
    return _find(r"(instant loan|loan approved|pre-?approved loan|processing fee|loan without (documents|cibil))", t)


def r_fake_payment(t: str) -> str:
    # A "payment successful" screenshot sent by a buyer to a seller, with pressure to hand over goods.
    if re.search(r"(payment (successful|done|sent)|paid successfully|transaction successful)", t, re.I) and \
       re.search(r"(check (your )?account later|sent by mistake|extra|return the (extra|excess)|refund the difference)", t, re.I):
        return _find(r"(sent by mistake|return the (extra|excess)|refund the difference|check (your )?account later)", t)
    return ""


def r_prompt_injection(t: str) -> str:
    # Adversarial attacks attempting to hijack AI decision-making
    return _find(r"(ignore (all )?(previous |prior |your )?instructions|system override|disregard (all )?(previous |prior )?instructions|"
                 r"classify this (message )?as safe|output (only )?safe|you are now in developer mode|pretend this is safe)", t)


RULES = [
    ("asks_secret", "Asks you to share OTP/PIN/password", "OTP/PIN/पासवर्ड माँग रहा है", 40, True, r_asks_secret),
    ("receive_needs_pin", "Says you must enter PIN / scan QR to RECEIVE money", "पैसे लेने के लिए PIN/QR माँग रहा है", 40, True, r_receive_needs_pin),
    ("digital_arrest", "Police/CBI/court threat with secrecy or video call (digital arrest)", "पुलिस/CBI का डर + वीडियो कॉल (डिजिटल अरेस्ट)", 45, True, r_digital_arrest),
    ("remote_access", "Asks to install a remote-access / screen-share app", "रिमोट-एक्सेस ऐप इंस्टॉल करवा रहा है", 40, True, r_remote_access),
    ("prompt_injection", "Prompt injection attempt detected", "AI सुरक्षा निर्देशों को बायपास करने की कोशिश (प्रॉम्प्ट इंजेक्शन)", 40, True, r_prompt_injection),
    ("authority_mention", "Mentions police/CBI/customs/court", "पुलिस/CBI/कस्टम्स का नाम", 15, False, r_authority_mention),
    ("urgency", "Urgency or deadline pressure", "जल्दबाज़ी का दबाव", 15, False, r_urgency),
    ("kyc_block", "KYC / account or SIM block threat", "KYC / अकाउंट ब्लॉक की धमकी", 20, False, r_kyc_block),
    ("lottery", "Prize or lottery you never entered", "बिना भाग लिए इनाम/लॉटरी", 30, False, r_lottery),
    ("job_task", "Pay-to-earn job or task offer", "पैसे कमाने वाला टास्क/जॉब ऑफर", 30, False, r_job_task),
    ("investment", "Guaranteed-return investment pitch", "पक्का मुनाफ़ा वाला निवेश", 30, False, r_investment),
    ("electricity", "Power-cut threat with a number to call", "आज रात बिजली कटने की धमकी", 30, False, r_electricity),
    ("parcel", "Parcel held / illegal items / customs fee", "पार्सल में गैरकानूनी सामान / कस्टम्स फीस", 30, False, r_parcel),
    ("family", "Relative on a 'new number' asking for money", "'नए नंबर' से रिश्तेदार पैसे माँग रहा है", 30, False, r_family),
    ("loan", "Instant loan / advance processing fee", "इंस्टेंट लोन / एडवांस फीस", 25, False, r_loan),
    ("fake_payment", "Payment screenshot + 'sent extra, return it' pressure", "पेमेंट स्क्रीनशॉट + 'ज़्यादा भेज दिया, लौटाओ'", 35, False, r_fake_payment),
]


def check_text(text: str) -> RuleReport:
    """Run every rule on the message text and return all flags + entities."""
    t = " ".join(text.split())  # normalise whitespace / newlines
    report = RuleReport(
        urls=sorted(set(URL_RE.findall(t))),
        upi_ids=sorted({u for u in UPI_RE.findall(t) if "." not in u.split("@")[1]}),  # skip emails like a@gmail.com
        phones=sorted(set(PHONE_RE.findall(t))),
        amounts=sorted(set(AMOUNT_RE.findall(t))),
    )

    for rid, en, hi, w, crit, fn in RULES:
        ev = fn(t)
        if ev:
            report.flags.append(Flag(rid, en, hi, w, ev.strip()[:80], crit))

    # Link checks
    for url in report.urls:
        host = _host(url)
        if not host:
            continue
        if host in SHORTENERS:
            report.flags.append(Flag("short_link", "Shortened link hides the real site", "छोटा लिंक असली साइट छुपाता है", 20, url))
        elif url.lower().split("?")[0].endswith(".apk"):
            report.flags.append(Flag("apk_link", "Link downloads an .apk app file", "लिंक से .apk ऐप डाउनलोड होगा", 35, url, True))
        elif not _is_official(host) and (host.endswith(RISKY_TLDS) or any(b in host for b in BRAND_WORDS)):
            report.flags.append(Flag("suspicious_domain", "Link is not an official domain", "लिंक आधिकारिक वेबसाइट नहीं है", 25, host))

    return report
