import os
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env local, se existir
load_dotenv()

# --- CONFIGURAÇÕES DO MONITOR ---
TARGET_URL = os.environ.get(
    "TARGET_URL", 
    "https://ustr.gov/about-us/policy-offices/press-office/press-releases"
)
STATE_FILE = os.environ.get("STATE_FILE", "state.json")
LOOP_INTERVAL_SECONDS = int(os.environ.get("LOOP_INTERVAL_SECONDS", 60))
MAX_NEW_RELEASES_PER_RUN = int(os.environ.get("MAX_NEW_RELEASES_PER_RUN", 5))

# --- CONFIGURAÇÕES DE E-MAIL (SMTP) ---
EMAIL_SENDER = (
    os.environ.get("EMAIL_SENDER")
    or os.environ.get("MAIL_FROM")
    or os.environ.get("SMTP_USER")
)
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD") or os.environ.get("SMTP_PASSWORD")
EMAIL_RECEIVER = os.environ.get("EMAIL_RECEIVER") or os.environ.get("MAIL_TO")
SMTP_SERVER = os.environ.get("SMTP_SERVER") or os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 465))

# --- CONFIGURAÇÕES DE WHATSAPP ---
WHATSAPP_PROVIDER = os.environ.get("WHATSAPP_PROVIDER", "").lower() # 'auto', 'callmebot', 'twilio', 'none'
# CallMeBot
CALLMEBOT_PHONE = os.environ.get("CALLMEBOT_PHONE")
CALLMEBOT_API_KEY = os.environ.get("CALLMEBOT_API_KEY")
# Twilio
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_FROM_WHATSAPP = os.environ.get("TWILIO_FROM_WHATSAPP", "whatsapp:+14155238886")
TWILIO_TO_WHATSAPP = os.environ.get("TWILIO_TO_WHATSAPP")
if WHATSAPP_PROVIDER in ("", "auto"):
    if all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_TO_WHATSAPP]):
        WHATSAPP_PROVIDER = "twilio"
    elif all([CALLMEBOT_PHONE, CALLMEBOT_API_KEY]):
        WHATSAPP_PROVIDER = "callmebot"
    else:
        WHATSAPP_PROVIDER = "none"

# --- CONFIGURAÇÕES DE PUSH ---
PUSH_PROVIDER = os.environ.get("PUSH_PROVIDER", "none").lower() # 'telegram', 'pushover', 'pushbullet', 'none'
# Telegram
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
# Pushover
PUSHOVER_USER_KEY = os.environ.get("PUSHOVER_USER_KEY")
PUSHOVER_API_TOKEN = os.environ.get("PUSHOVER_API_TOKEN")
# Pushbullet
PUSHBULLET_ACCESS_TOKEN = os.environ.get("PUSHBULLET_ACCESS_TOKEN")

def validate_config():
    """Garante que as configurações essenciais foram fornecidas."""
    warnings = []
    
    # E-mail é essencial para o robô funcionar conforme requisitos
    if not all([EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER]):
        warnings.append(
            "⚠️ Configurações de e-mail incompletas. Notificações de e-mail serão desativadas.\n"
            "Preencha EMAIL_SENDER, EMAIL_PASSWORD e EMAIL_RECEIVER."
        )
        
    # Validação do WhatsApp
    if WHATSAPP_PROVIDER == "callmebot":
        if not all([CALLMEBOT_PHONE, CALLMEBOT_API_KEY]):
            warnings.append("⚠️ CallMeBot configurado, mas CALLMEBOT_PHONE ou CALLMEBOT_API_KEY está ausente.")
    elif WHATSAPP_PROVIDER == "twilio":
        if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_TO_WHATSAPP]):
            warnings.append("⚠️ Twilio configurado, mas TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN ou TWILIO_TO_WHATSAPP está ausente.")
            
    # Validação de Push
    if PUSH_PROVIDER == "telegram":
        if not all([TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID]):
            warnings.append("⚠️ Telegram configurado, mas TELEGRAM_BOT_TOKEN ou TELEGRAM_CHAT_ID está ausente.")
    elif PUSH_PROVIDER == "pushover":
        if not all([PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN]):
            warnings.append("⚠️ Pushover configurado, mas PUSHOVER_USER_KEY ou PUSHOVER_API_TOKEN está ausente.")
    elif PUSH_PROVIDER == "pushbullet":
        if not PUSHBULLET_ACCESS_TOKEN:
            warnings.append("⚠️ Pushbullet configurado, mas PUSHBULLET_ACCESS_TOKEN está ausente.")
            
    return warnings
