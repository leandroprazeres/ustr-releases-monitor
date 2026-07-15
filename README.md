# USTR Press Releases Monitor 🤖

Este robô monitora a página de comunicados de imprensa (Press Releases) do USTR ([https://ustr.gov/about-us/policy-offices/press-office/press-releases](https://ustr.gov/about-us/policy-offices/press-office/press-releases)). Quando um novo comunicado é publicado, ele extrai o título, link e gera um resumo do conteúdo, disparando notificações de forma imediata por E-mail, WhatsApp e Push Notification.

---

## Recursos e Integrações

- **Raspagem Eficiente**: Usa `requests` e `BeautifulSoup` para obter as informações de forma leve e rápida, sem precisar carregar navegadores pesados.
- **Resumo Inteligente**: Acessa a página do release para obter o resumo oficial gerado na tag meta-description ou o primeiro parágrafo do artigo.
- **Três Canais de Notificação**:
  1. **E-mail**: Disparo via SMTP padrão (Gmail, Office365, etc.).
  2. **WhatsApp**: Suporte gratuito via **CallMeBot** ou comercial via **Twilio**.
  3. **Push Notifications**: Notificações instantâneas no celular via **Telegram Bot**, **Pushover** ou **Pushbullet**.
- **Execução Híbrida**: Pode rodar como um serviço contínuo local/servidor ou de forma 100% autônoma e gratuita no **GitHub Actions** (rodando a cada 10 minutos e salvando estado).

---

## Configuração das Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto (use o `.env.example` como base) e preencha as variáveis correspondentes aos canais que deseja ativar:

### 1. E-mail (SMTP)
```env
EMAIL_SENDER=seu_email@gmail.com
EMAIL_PASSWORD=sua_senha_de_aplicativo_do_gmail   # Não é a senha comum, é uma senha de app criada na sua conta Google
EMAIL_RECEIVER=email_destinatario@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=465
```

### 2. WhatsApp (CallMeBot - Recomendado / Gratuito)
1. Adicione o número do CallMeBot nos contatos do seu celular.
2. Envie uma mensagem pelo WhatsApp para iniciar o cadastro e receber a API key (Instruções detalhadas em: [https://www.callmebot.com/blog/free-api-whatsapp-messages/](https://www.callmebot.com/blog/free-api-whatsapp-messages/)).
3. Preencha no `.env`:
```env
WHATSAPP_PROVIDER=callmebot
CALLMEBOT_PHONE=+5511999999999   # Seu número com DDI e DDD
CALLMEBOT_API_KEY=sua_chave_recebida
```

### 3. Push Notifications (Telegram - Recomendado / Gratuito)
1. Crie um Bot no Telegram conversando com o `@BotFather` e copie o Token.
2. Descubra o seu Chat ID conversando com o `@userinfobot`.
3. Preencha no `.env`:
```env
PUSH_PROVIDER=telegram
TELEGRAM_BOT_TOKEN=seu_token_aqui
TELEGRAM_CHAT_ID=seu_chat_id_aqui
```

---

## Como Rodar Localmente

1. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Crie e configure o seu arquivo `.env`.
3. Execute em modo de teste (dispara um alerta com o release mais recente para testar as conexões):
   ```bash
   python monitor.py --test-notify
   ```
4. Execute em modo único (roda uma vez e atualiza o estado):
   ```bash
   python monitor.py
   ```
5. Execute em modo contínuo (loop infinito com tempo de espera configurado em `LOOP_INTERVAL_SECONDS`):
   ```bash
   python monitor.py --loop
   ```

---

## Como Configurar no GitHub Actions (Nuvem Grátis)

Para rodar o robô diretamente na nuvem do GitHub de forma automática a cada 10 minutos, siga os passos abaixo:

1. Crie um repositório no seu GitHub chamado `ustr-releases-monitor`.
2. Vá nas configurações do repositório: **Settings > Secrets and variables > Actions**.
3. Adicione cada uma das configurações do seu `.env` como um **New repository secret**. Exemplos:
   - `EMAIL_SENDER`
   - `EMAIL_PASSWORD`
   - `EMAIL_RECEIVER`
   - `WHATSAPP_PROVIDER`
   - `CALLMEBOT_PHONE`
   - `CALLMEBOT_API_KEY`
   - `PUSH_PROVIDER`
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Dê permissão para o GitHub Actions fazer commits de volta (necessário para atualizar o arquivo `state.json` com os releases vistos):
   - Vá em **Settings > Actions > General**.
   - Role até a seção **Workflow permissions** e selecione **Read and write permissions**.
   - Clique em **Save**.
5. Faça o push do código para o repositório. O workflow iniciará automaticamente com base na agenda (cron) configurada em `.github/workflows/monitor.yml`.
