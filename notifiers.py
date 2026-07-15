import smtplib
import urllib.parse
from email.message import EmailMessage
import requests
import config

def send_email(subject, text_body, html_body):
    """Envia um e-mail utilizando as configurações SMTP carregadas de config.py."""
    if not all([config.EMAIL_SENDER, config.EMAIL_PASSWORD, config.EMAIL_RECEIVER]):
        print("[EMAIL] Pulado: Credenciais de e-mail não configuradas.")
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = config.EMAIL_SENDER
    msg['To'] = config.EMAIL_RECEIVER
    
    msg.set_content(text_body)
    msg.add_alternative(html_body, subtype='html')

    try:
        if config.SMTP_PORT == 465:
            # Usar conexão SSL padrão para Gmail (porta 465)
            with smtplib.SMTP_SSL(config.SMTP_SERVER, config.SMTP_PORT) as smtp:
                smtp.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
                smtp.send_message(msg)
        else:
            # Usar conexão TLS (geralmente porta 587)
            with smtplib.SMTP(config.SMTP_SERVER, config.SMTP_PORT) as smtp:
                smtp.starttls()
                smtp.login(config.EMAIL_SENDER, config.EMAIL_PASSWORD)
                smtp.send_message(msg)
        print("[EMAIL] E-mail enviado com sucesso!")
        return True
    except Exception as e:
        print(f"[EMAIL] Erro ao enviar e-mail: {e}")
        return False


def send_whatsapp(message):
    """Envia uma mensagem de WhatsApp de acordo com o provedor configurado."""
    provider = config.WHATSAPP_PROVIDER
    if provider == "none":
        return False
        
    if provider == "callmebot":
        return _send_whatsapp_callmebot(message)
    elif provider == "twilio":
        return _send_whatsapp_twilio(message)
    else:
        print(f"[WHATSAPP] Provedor inválido ou não suportado: {provider}")
        return False


def _send_whatsapp_callmebot(message):
    """Envia WhatsApp via API do CallMeBot (Gratuito)."""
    if not all([config.CALLMEBOT_PHONE, config.CALLMEBOT_API_KEY]):
        print("[WHATSAPP-CallMeBot] Parâmetros ausentes no arquivo de configuração.")
        return False
        
    # URL-encode a mensagem
    encoded_message = urllib.parse.quote(message)
    url = f"https://api.callmebot.com/whatsapp.php?phone={config.CALLMEBOT_PHONE}&text={encoded_message}&apikey={config.CALLMEBOT_API_KEY}"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            print("[WHATSAPP-CallMeBot] Mensagem enviada com sucesso!")
            return True
        else:
            print(f"[WHATSAPP-CallMeBot] Erro no envio (Código {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"[WHATSAPP-CallMeBot] Erro ao conectar à API: {e}")
        return False


def _send_whatsapp_twilio(message):
    """Envia WhatsApp utilizando a API do Twilio (usando requests para evitar dependência externa)."""
    if not all([config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN, config.TWILIO_TO_WHATSAPP]):
        print("[WHATSAPP-Twilio] Parâmetros do Twilio ausentes na configuração.")
        return False
        
    url = f"https://api.twilio.com/2010-04-01/Accounts/{config.TWILIO_ACCOUNT_SID}/Messages.json"
    
    # Formatação do número: Twilio exige o prefixo "whatsapp:"
    to_number = config.TWILIO_TO_WHATSAPP
    if not to_number.startswith("whatsapp:"):
        to_number = f"whatsapp:{to_number}"
        
    from_number = config.TWILIO_FROM_WHATSAPP
    if not from_number.startswith("whatsapp:"):
        from_number = f"whatsapp:{from_number}"
        
    payload = {
        "From": from_number,
        "To": to_number,
        "Body": message
    }
    
    try:
        response = requests.post(
            url, 
            data=payload, 
            auth=(config.TWILIO_ACCOUNT_SID, config.TWILIO_AUTH_TOKEN),
            timeout=15
        )
        if response.status_code in [200, 201]:
            print("[WHATSAPP-Twilio] Mensagem enviada com sucesso!")
            return True
        else:
            print(f"[WHATSAPP-Twilio] Erro no envio (Código {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"[WHATSAPP-Twilio] Erro ao conectar ao Twilio: {e}")
        return False


def send_push(message):
    """Envia notificação push usando o provedor configurado."""
    provider = config.PUSH_PROVIDER
    if provider == "none":
        return False
        
    if provider == "telegram":
        return _send_push_telegram(message)
    elif provider == "pushover":
        return _send_push_pushover(message)
    elif provider == "pushbullet":
        return _send_push_pushbullet(message)
    else:
        print(f"[PUSH] Provedor inválido ou não suportado: {provider}")
        return False


def _send_push_telegram(message):
    """Envia notificação via Telegram Bot."""
    if not all([config.TELEGRAM_BOT_TOKEN, config.TELEGRAM_CHAT_ID]):
        print("[PUSH-Telegram] Token ou Chat ID ausente no arquivo de configuração.")
        return False
        
    url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": config.TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=15)
        if response.status_code == 200:
            print("[PUSH-Telegram] Notificação enviada via Telegram!")
            return True
        else:
            print(f"[PUSH-Telegram] Erro no envio (Código {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"[PUSH-Telegram] Erro ao conectar ao Telegram: {e}")
        return False


def _send_push_pushover(message):
    """Envia notificação via Pushover."""
    if not all([config.PUSHOVER_USER_KEY, config.PUSHOVER_API_TOKEN]):
        print("[PUSH-Pushover] Credenciais do Pushover ausentes no arquivo de configuração.")
        return False
        
    url = "https://api.pushover.net/1/messages.json"
    payload = {
        "token": config.PUSHOVER_API_TOKEN,
        "user": config.PUSHOVER_USER_KEY,
        "message": message,
        "title": "USTR Release Monitor"
    }
    
    try:
        response = requests.post(url, data=payload, timeout=15)
        if response.status_code == 200:
            print("[PUSH-Pushover] Notificação enviada via Pushover!")
            return True
        else:
            print(f"[PUSH-Pushover] Erro no envio (Código {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"[PUSH-Pushover] Erro ao conectar ao Pushover: {e}")
        return False


def _send_push_pushbullet(message):
    """Envia notificação via Pushbullet."""
    if not config.PUSHBULLET_ACCESS_TOKEN:
        print("[PUSH-Pushbullet] Token de acesso do Pushbullet ausente no arquivo de configuração.")
        return False
        
    url = "https://api.pushbullet.com/v2/pushes"
    headers = {
        "Access-Token": config.PUSHBULLET_ACCESS_TOKEN,
        "Content-Type": "application/json"
    }
    payload = {
        "type": "note",
        "title": "USTR Release Monitor",
        "body": message
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            print("[PUSH-Pushbullet] Notificação enviada via Pushbullet!")
            return True
        else:
            print(f"[PUSH-Pushbullet] Erro no envio (Código {response.status_code}): {response.text}")
            return False
    except Exception as e:
        print(f"[PUSH-Pushbullet] Erro ao conectar ao Pushbullet: {e}")
        return False


def send_all_notifications(title, summary, link):
    """Dispara a notificação por todos os canais configurados."""
    # Monta os corpos de texto
    subject = f"🚨 Novo Release USTR: {title}"
    
    text_body = (
        f"Alerta: Houve uma mudança no site do USTR e um novo release foi publicado!\n\n"
        f"Título: {title}\n\n"
        f"Resumo:\n{summary}\n\n"
        f"Link para o release:\n{link}\n\n"
        f"---\nRobô de Monitoramento do USTR"
    )
    
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2 style="color: #0b3c5d;">🚨 Novo Release USTR Detectado!</h2>
        <p>Houve uma mudança no site do USTR e um novo comunicado de imprensa foi publicado:</p>
        <div style="background-color: #f9f9f9; padding: 15px; border-left: 5px solid #0b3c5d; margin: 15px 0;">
          <h3 style="margin-top: 0; color: #333;">{title}</h3>
          <p><strong>Resumo:</strong></p>
          <p style="font-style: italic; color: #555;">{summary}</p>
        </div>
        <p>
          <a href="{link}" style="background-color: #0b3c5d; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; display: inline-block;">
            Ler Comunicado Completo
          </a>
        </p>
        <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
        <p style="font-size: 0.8em; color: #777;">Este e-mail foi enviado automaticamente pelo robô de monitoramento de releases.</p>
      </body>
    </html>
    """
    
    # 1. Enviar E-mail
    send_email(subject, text_body, html_body)
    
    # 2. Enviar WhatsApp (com texto simples)
    wa_msg = f"*🚨 Novo Release USTR:*\n{title}\n\n*Resumo:*\n{summary}\n\n*Link:*\n{link}"
    send_whatsapp(wa_msg)
    
    # 3. Enviar Push (com texto simplificado)
    push_msg = f"<b>🚨 Novo Release USTR:</b>\n{title}\n\n{link}"
    send_push(push_msg)
