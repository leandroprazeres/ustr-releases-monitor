import os
import json
import time
import argparse
import requests
from bs4 import BeautifulSoup

import config
import notifiers

def load_state():
    """Carrega o estado dos releases já vistos."""
    if os.path.exists(config.STATE_FILE):
        try:
            with open(config.STATE_FILE, "r", encoding="utf-8") as f:
                state = json.load(f)
                # Garante que temos a lista de URLs vistas
                if "seen_urls" in state:
                    return state
        except Exception as e:
            print(f"[MONITOR] Erro ao carregar arquivo de estado: {e}. Criando novo estado.")
    
    return {"seen_urls": []}


def save_state(state):
    """Salva o estado no arquivo JSON."""
    try:
        with open(config.STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
        print("[MONITOR] Estado atualizado com sucesso.")
    except Exception as e:
        print(f"[MONITOR] Erro ao salvar estado: {e}")


def fetch_release_summary(url):
    """Acessa a página de detalhes do release para extrair um resumo."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    try:
        print(f"[MONITOR] Buscando resumo em: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Estratégia 1: Tentar a tag meta description (muito precisa no site do USTR)
        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            summary = meta_desc.get("content").strip()
            if len(summary) > 20:
                return summary
                
        # Estratégia 2: Extrair o primeiro parágrafo relevante da div de conteúdo
        body_div = soup.find("div", class_="field--name-body")
        if body_div:
            paragraphs = body_div.find_all("p")
            for p in paragraphs:
                text = p.get_text().strip()
                # Ignora parágrafos vazios, muito curtos ou que apenas contêm datas
                if text and len(text) > 40 and not text.replace(" ", "").replace(",", "").isdigit():
                    return text
                    
        # Fallback se nada funcionar
        return "Resumo não disponível. Acesse o link para ler o comunicado completo."
        
    except Exception as e:
        print(f"[MONITOR] Erro ao buscar resumo detalhado de {url}: {e}")
        return "Erro ao carregar o resumo automático. Clique no link para ver o original."


def scrape_releases():
    """Acessa a listagem do USTR e extrai os releases mais recentes."""
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
    }
    
    print(f"[MONITOR] Acessando listagem de releases: {config.TARGET_URL}")
    response = requests.get(config.TARGET_URL, headers=headers, timeout=15)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, "html.parser")
    releases = []
    
    # Encontra todas as linhas da lista de visualização
    rows = soup.find_all("div", class_="views-row")
    
    for row in rows:
        title_field = row.find("div", class_="views-field-title")
        if not title_field:
            continue
            
        link_tag = title_field.find("a")
        if not link_tag:
            continue
            
        title = link_tag.get_text().strip()
        relative_link = link_tag.get("href")
        
        # Constrói o link completo
        full_link = relative_link
        if relative_link.startswith("/"):
            full_link = f"https://ustr.gov{relative_link}"
            
        # Tenta obter a data se existir
        date_field = row.find("div", class_="views-field-field-date")
        date_str = ""
        if date_field:
            time_tag = date_field.find("time")
            if time_tag:
                date_str = time_tag.get_text().strip()
                
        releases.append({
            "title": title,
            "link": full_link,
            "date": date_str
        })
        
    return releases


def check_for_updates(test_notify=False):
    """Executa a verificação principal de novos releases."""
    try:
        warnings = config.validate_config()
        for w in warnings:
            print(w)
            
        releases = scrape_releases()
        if not releases:
            print("[MONITOR] Nenhum release encontrado na página.")
            return
            
        print(f"[MONITOR] {len(releases)} releases encontrados na listagem.")
        
        # Carrega o estado anterior
        state = load_state()
        seen_urls = state["seen_urls"]
        
        # Se for a primeira execução e o estado estiver vazio
        if not seen_urls and not test_notify:
            print("[MONITOR] Primeiro run do monitor. Salvando releases históricos...")
            state["seen_urls"] = [r["link"] for r in releases]
            save_state(state)
            
            # Envia e-mail opcional avisando que o monitor iniciou
            notifiers.send_email(
                subject="✅ Monitor de Releases do USTR Ativado!",
                text_body=f"O robô de monitoramento de novos releases do USTR foi iniciado com sucesso!\nURL monitorada: {config.TARGET_URL}",
                html_body=f"<html><body><h2>✅ Monitor USTR Ativado!</h2><p>O monitoramento automático foi iniciado para a página: <a href='{config.TARGET_URL}'>{config.TARGET_URL}</a></p></body></html>"
            )
            return

        # Para fins de teste forçado
        if test_notify:
            print("[MONITOR] Modo de teste ativado. Forçando notificação do release mais recente.")
            latest = releases[0]
            summary = fetch_release_summary(latest["link"])
            print(f"\n--- [DEBUG] INFO DO RELEASE MAIS RECENTE ---")
            print(f"Título: {latest['title']}")
            print(f"Link: {latest['link']}")
            print(f"Data: {latest['date']}")
            print(f"Resumo Extraído: {summary}\n--------------------------------------------\n")
            notifiers.send_all_notifications(
                title=f"[TESTE] {latest['title']}",
                summary=summary,
                link=latest["link"]
            )
            return

        # Identifica novos releases (da listagem, em ordem cronológica reversa, processamos do mais antigo para o mais novo)
        new_releases = []
        for r in releases:
            if r["link"] not in seen_urls:
                new_releases.append(r)
                
        # Inverte para notificar do mais antigo para o mais recente
        new_releases.reverse()
        
        if new_releases:
            print(f"[MONITOR] Detectado(s) {len(new_releases)} novo(s) release(s)!")
            for r in new_releases:
                print(f"[MONITOR] Novo release encontrado: {r['title']}")
                summary = fetch_release_summary(r["link"])
                
                # Envia notificações por todos os canais configurados
                notifiers.send_all_notifications(
                    title=r["title"],
                    summary=summary,
                    link=r["link"]
                )
                
                # Adiciona ao estado
                seen_urls.append(r["link"])
                
            # Limita a lista de vistos para evitar crescimento infinito
            if len(seen_urls) > 100:
                seen_urls = seen_urls[-100:]
                
            state["seen_urls"] = seen_urls
            save_state(state)
        else:
            print("[MONITOR] Nenhuma novidade encontrada.")
            
    except Exception as e:
        print(f"[MONITOR] Ocorreu um erro durante a verificação: {e}")
        import traceback
        traceback.print_exc()


def main():
    parser = argparse.ArgumentParser(description="Monitor de Releases do USTR")
    parser.add_argument(
        "--loop", 
        action="store_true", 
        help="Executa o monitor em um loop contínuo"
    )
    parser.add_argument(
        "--test-notify", 
        action="store_true", 
        help="Dispara uma notificação de teste com o release mais recente"
    )
    args = parser.parse_args()
    
    if args.test_notify:
        check_for_updates(test_notify=True)
    elif args.loop:
        print(f"[MONITOR] Iniciando em modo contínuo. Intervalo: {config.LOOP_INTERVAL_SECONDS} segundos.")
        while True:
            print(f"\n--- Verificação iniciada em {time.strftime('%Y-%m-%d %H:%M:%S')} ---")
            check_for_updates()
            time.sleep(config.LOOP_INTERVAL_SECONDS)
    else:
        print("[MONITOR] Executando verificação única.")
        check_for_updates()


if __name__ == "__main__":
    main()
