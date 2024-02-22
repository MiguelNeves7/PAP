import pyttsx3
from datetime import datetime, timedelta
import speech_recognition as sr
import wikipediaapi
from urllib.parse import quote
from googlesearch import search
import threading
import time
import pyaudio
import pygame
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os

# Inicializa o objeto de texto para fala
texto_fala = pyttsx3.init()

alarme_ativo = False
hora_alarme = None
escutando = True
r = sr.Recognizer()

lista_tarefas = []

# Configuração das credenciais do Spotify
SPOTIPY_CLIENT_ID = '801f4822c6dc4084bbad503e3bba3853'
SPOTIPY_CLIENT_SECRET = '444f5cf580984a958d3712cf84227f26'

# Inicializa o objeto spotipy
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri="http://localhost:8888/callback",
                                               scope="user-library-read user-read-playback-state user-modify-playback-state"))

# Adicionado evento para suspender escuta
evento_suspensao = threading.Event()

def imprimir_vozes_disponiveis():
    voices = texto_fala.getProperty('voices')
    for i, voice in enumerate(voices):
        print(f"Voz {i + 4}: {voice.name}")

# Chame essa função antes de qualquer tentativa de fala
imprimir_vozes_disponiveis()

def falar(audio):
    voices = texto_fala.getProperty('voices')
    texto_fala.setProperty('voice', voices[1].id)
    texto_fala.say(audio)
    texto_fala.runAndWait()

def tocar_alarme(caminho_do_som):
    pygame.mixer.init()
    pygame.mixer.music.load(caminho_do_som)
    pygame.mixer.music.play()

def config_alarme(hora_alarme, caminho_do_som):
    while True:
        agora = datetime.now()
        if agora.hour == hora_alarme.hour and agora.minute == hora_alarme.minute:
            tocar_alarme(caminho_do_som)
            break
        time.sleep(60)

def definir_tarefa():
    falar("O que você gostaria de adicionar à sua lista de tarefas?")
    tarefa = microfone().lower()
    lista_tarefas.append(tarefa)
    falar(f"Tarefa adicionada: {tarefa}")

def verificar_tarefas():
    while True:
        agora = datetime.now()
        if agora.hour == 21 and agora.minute == 0:
            falar("Já concluiu as tarefas pendentes?")
            resposta = microfone().lower()
            if 'sim' in resposta:
                lista_tarefas.clear()
                falar("Ótimo! Todas as tarefas foram concluídas.")
            else:
                falar("Aqui estão as tarefas pendentes:")
                for i, tarefa in enumerate(lista_tarefas, start=1):
                    falar(f"Tarefa {i}: {tarefa}")
        time.sleep(60)

def lembrar_tarefas():
    while True:
        agora = datetime.now()
        for tarefa in lista_tarefas:
            horario_tarefa = agora.replace(second=0, microsecond=0) + timedelta(hours=1)
            if agora < horario_tarefa <= agora + timedelta(minutes=15):
                falar(f"Lembrete: Você tem a tarefa {tarefa} em 15 minutos.")
        time.sleep(60)

def tocar_musica_spotify(musica, artista):
    results = sp.search(q=f"{musica} {artista}", limit=1, type='track')
    if results['tracks']['items']:
        track_uri = results['tracks']['items'][0]['uri']
        sp.start_playback(uris=[track_uri])
        falar(f"Reproduzindo {musica} de {artista} no Spotify.")
    else:
        falar(f"Desculpe, não foi possível encontrar a música. Tente novamente.")


def suspender_escuta():
    global escutando
    escutando = False
    evento_suspensao.set()
    print("Escuta suspensa.")

def ativar_escuta():
    global escutando
    escutando = True
    evento_suspensao.clear()
    print("Aguardando comando...")

def pesquisar_internet():
    falar("O que você gostaria de pesquisar na web?")
    termo_pesquisa = microfone().lower()

    if "wikipedia" in termo_pesquisa:
        termo_pesquisa = termo_pesquisa.replace("wikipedia", "").strip()
        wiki_wiki = wikipediaapi.Wikipedia("pt")
        page_py = wiki_wiki.page(termo_pesquisa)

        if page_py.exists():
            # Obtém informações detalhadas da Wikipedia
            resposta = f"{termo_pesquisa}: {page_py.text[:500]}"
            falar(resposta)
        else:
            falar(f"Desculpe, não encontrei informações sobre {termo_pesquisa} na Wikipedia.")
    else:
        termo_pesquisa_url = quote(termo_pesquisa)
        resultado_pesquisa_web = list(search(termo_pesquisa_url, num_results=1))

        if resultado_pesquisa_web:
            link = resultado_pesquisa_web[0]
            falar(f"Aqui está o que encontrei: {link}")
        else:
            falar("Desculpe, não consegui encontrar informações para essa pergunta na web.")

def tempo():
    agora = datetime.now()
    hora_atual = agora.strftime("%I:%M")
    falar(f"A hora atual é: {hora_atual}")

def data():
    ano = str(datetime.now().year)
    mes = str(datetime.now().month)
    dia = str(datetime.now().day)

    data = f"Dia {dia} do Mês de {mes} de {ano}"
    falar(data)

def obter_temperatura(cidade):
    api_key = '81100e467b5b9ca05b0477784f56cd84'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric'

    response = requests.get(url)
    dados_clima = response.json()

    if response.status_code == 200:
        temperatura = dados_clima['main']['temp']
        falar(f"A temperatura em {cidade} é de {temperatura} graus Celsius.")
    else:
        falar("Desculpe, não foi possível obter a temperatura no momento.")

def microfone():
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        print("Diga algo...")
        try:
            audio = r.listen(source, timeout=5)
            print("Reconhecendo...")
            comando = r.recognize_google(audio, language='pt-PT')
            print(comando)
            return comando.lower()
        except sr.UnknownValueError:
            print("Não foi possível entender o áudio. Por favor, tente novamente.")
            return "None"
        except sr.RequestError as e:
            print(f"Erro na requisição ao Google: {e}")
            return "None"

def bem_vindo():
    falar("Olá Miguel. Bem-vindo!")

    agora = datetime.now()
    hora = agora.hour

    tempo()
    data()

    if 6 <= hora < 12:
        falar("Bom dia Miguel!")
    elif 12 <= hora < 18:
        falar("Boa tarde Miguel!")
    elif 18 <= hora <= 24:
        falar("Boa noite Miguel!")
    else:
        falar("Bom dia!")

    falar("Elektra a sua disposição! Diga-me como posso ajudá-lo")

# Thread para verificar tarefas e lembretes
thread_tarefas = threading.Thread(target=verificar_tarefas, daemon=True)
thread_tarefas.start()

thread_lembrar_tarefas = threading.Thread(target=lembrar_tarefas, daemon=True)
thread_lembrar_tarefas.start()


if __name__ == "__main__":
    bem_vindo()

    hora_alarme = datetime.now() + timedelta(minutes=1)
    caminho_do_som = "caminho_para_seu_arquivo_de_alarme.mp3"

    thread_alarme = threading.Thread(target=config_alarme, args=(hora_alarme, caminho_do_som), daemon=True)
    thread_alarme.start()

    while True:
        print("Escutando...")

        comando = microfone()

        if 'como estás?' in comando:
            falar("Estou bem! Obrigado por perguntar. O que posso fazer para ajudá-lo, Miguel?")
        elif 'que dia é hoje' in comando:
            data()
        elif 'hora' in comando:
            tempo()
        elif 'pesquisa' in comando:
            pesquisar_internet()
        elif 'definir alarme' in comando:
            falar("Em que hora quer definir o alarme?")
            hora_definida = microfone()
            try:
                hora_alarme = datetime.strptime(hora_definida, "%H:%M")
                thread_alarme = threading.Thread(target=config_alarme, args=(hora_alarme, caminho_do_som), daemon=True)
                thread_alarme.start()
            except ValueError:
                falar("Desculpe, não entendi a hora. Por favor, tente novamente.")
        elif 'voltei' in comando:
            ativar_escuta()
        elif 'até já' in comando:
            suspender_escuta()
            print("Aguardando reativação...")  # Adicionado para indicar que está esperando reativação
        elif 'definir tarefa' in comando:
            definir_tarefa()
        elif 'temperatura' in comando:
            falar("De qual cidade?")
            cidade = microfone()
            obter_temperatura(cidade)
        elif 'reproduzir música' in comando:
            falar("Qual música e qual artista você deseja ouvir?")
            musica_artista = microfone()
            partes = musica_artista.split(" e ")
            if len(partes) == 2:
                musica, artista = partes
                tocar_musica_spotify(musica, artista)  # Modificado para usar a função correta
            else:
                falar("Por favor, forneça tanto o nome da música quanto do artista.")
        elif 'desligar' in comando:
            falar("Programa encerrado. Até logo!")
            break
