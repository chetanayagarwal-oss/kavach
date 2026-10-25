"""Fixed advice templates. The model NEVER writes helpline numbers or steps itself,
so it cannot hallucinate a wrong number. (Same idea judges praised in Project Rosie.)"""

HELP_EN = [
    "Do not pay, do not share OTP / UPI PIN, do not click the link.",
    "Lost money already? Call 1930 (National Cyber Crime Helpline) immediately and report at cybercrime.gov.in.",
    "Report the fraud number/SMS on Sanchar Saathi (sancharsaathi.gov.in → Chakshu).",
]
HELP_HI = [
    "पैसे मत भेजिए, OTP / UPI PIN किसी को मत बताइए, लिंक पर क्लिक मत कीजिए।",
    "पैसे कट गए? तुरंत 1930 (साइबर क्राइम हेल्पलाइन) पर कॉल करें और cybercrime.gov.in पर शिकायत करें।",
    "फ्रॉड नंबर/SMS की शिकायत संचार साथी (sancharsaathi.gov.in → चक्षु) पर करें।",
]

TYPE_TIP = {
    "digital_arrest": ("No police or agency does 'digital arrest' on a video call. Cut the call and tell your family.",
                       "कोई भी पुलिस या एजेंसी वीडियो कॉल पर 'डिजिटल अरेस्ट' नहीं करती। कॉल काटिए और परिवार को बताइए।"),
    "upi_collect_request": ("You never need a PIN or QR scan to receive money. Decline the request.",
                            "पैसे लेने के लिए PIN या QR स्कैन की ज़रूरत कभी नहीं होती। रिक्वेस्ट डिक्लाइन करें।"),
    "fake_payment_screenshot": ("Check your bank app balance, not the screenshot, before handing over anything.",
                                "सामान देने से पहले स्क्रीनशॉट नहीं, अपने बैंक ऐप का बैलेंस देखें।"),
    "kyc_update": ("Banks never ask KYC via SMS links. Visit the branch or the official app.",
                   "बैंक SMS लिंक से KYC नहीं माँगते। ब्रांच या आधिकारिक ऐप से ही करें।"),
    "otp_or_pin_request": ("Your OTP/PIN is only for you. No bank employee will ever ask for it.",
                           "OTP/PIN सिर्फ़ आपके लिए है। कोई बैंक कर्मचारी इसे कभी नहीं माँगेगा।"),
    "phishing_link": ("Type the official website yourself instead of opening this link.",
                      "यह लिंक खोलने की बजाय आधिकारिक वेबसाइट ख़ुद टाइप करें।"),
    "job_task_scam": ("Real jobs never ask you to pay first. Leave the group.",
                      "असली नौकरी में पहले पैसे नहीं देने पड़ते। ग्रुप छोड़ दें।"),
    "investment_trading": ("Guaranteed high returns do not exist. Use only SEBI-registered platforms.",
                           "पक्का मोटा मुनाफ़ा नहीं होता। सिर्फ़ SEBI-रजिस्टर्ड प्लेटफ़ॉर्म इस्तेमाल करें।"),
    "lottery_prize": ("You cannot win a lottery you never entered. Never pay a 'tax' to claim a prize.",
                      "जिस लॉटरी में भाग नहीं लिया, वो जीत नहीं सकते। इनाम के लिए 'टैक्स' न भरें।"),
    "parcel_customs": ("Courier companies don't threaten arrest. Check status on the official site.",
                       "कूरियर कंपनी गिरफ़्तारी की धमकी नहीं देती। आधिकारिक साइट पर स्टेटस देखें।"),
    "electricity_bill": ("Check your bill on the official electricity board app. Don't call the number in the SMS.",
                         "बिल बिजली विभाग के आधिकारिक ऐप पर देखें। SMS वाले नंबर पर कॉल न करें।"),
    "loan_app": ("Use only RBI-registered lenders. Never pay a fee before getting a loan.",
                 "सिर्फ़ RBI-रजिस्टर्ड लेंडर से लोन लें। लोन से पहले कोई फ़ीस न दें।"),
    "family_impersonation": ("Call the relative on their OLD number before sending anything.",
                             "पैसे भेजने से पहले रिश्तेदार को उनके पुराने नंबर पर कॉल करें।"),
    "remote_access": ("Never install screen-sharing apps on a stranger's request. Uninstall it now.",
                      "किसी अनजान के कहने पर स्क्रीन-शेयरिंग ऐप इंस्टॉल न करें। अभी अनइंस्टॉल करें।"),
}

SAFE_EN = "Looks like a normal message. Still, verify anything about money inside the official app."
SAFE_HI = "यह सामान्य मैसेज लगता है। फिर भी पैसों से जुड़ी बात आधिकारिक ऐप में ही जाँचें।"


def build_advice(verdict: str, scam_type: str) -> dict:
    if verdict == "safe":
        return {"en": [SAFE_EN], "hi": [SAFE_HI]}
    tip_en, tip_hi = TYPE_TIP.get(scam_type, ("Treat this message as risky.", "इस मैसेज को जोखिम भरा मानें।"))
    return {"en": [tip_en, *HELP_EN], "hi": [tip_hi, *HELP_HI]}
