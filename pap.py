import pyttsx3
from datetime import datetime, timedelta
import threading
import time
import pygame
from pygame.locals import *
import requests
from googlesearch import search
from bs4 import BeautifulSoup
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import speech_recognition as sr
import feedparser

# Inicialização do objeto para conversão de texto em fala
conversor_texto_fala = pyttsx3.init(driverName='sapi5')

# Inicialização do Pygame
pygame.init()

# Configuração da janela
largura_janela = 800
altura_janela = 600
janela = pygame.display.set_mode((largura_janela, altura_janela))
pygame.display.set_caption("Animações")

# Definição da posição inicial da animação
pos_x = 0
pos_y = 0

# Animações
temperatura = pygame.image.load(r'c:\Users\alves\Desktop\PAP\Pap\tempo.jpg')
horas = pygame.image.load(r'c:\Users\alves\Desktop\PAP\Pap\horas.jpg')
fala = pygame.image.load(r'c:\Users\alves\Desktop\PAP\Pap\falar.jpg')
jornal = pygame.image.load(r'c:\Users\alves\Desktop\PAP\Pap\noticias.jpg')
pesquisar = pygame.image.load(r'c:\Users\alves\Desktop\PAP\Pap\pesquisar.jpg')

# Definições
DEPURAR = False
ESCUTANDO = True
LISTA_TAREFAS = []
itens_mercado = []

# Inicialização do reconhecimento de fala
reconhecedor = sr.Recognizer()

# Evento para suspender a escuta
evento_suspensao = threading.Event()

# Configurações do Spotify
SPOTIPY_CLIENT_ID = '801f4822c6dc4084bbad503e3bba3853'
SPOTIPY_CLIENT_SECRET = '444f5cf580984a958d3712cf84227f26'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri="http://localhost:8888/callback",
                                               scope="user-library-read user-read-playback-state user-modify-playback-state"))


# Função para falar
def falar(audio):
    voices = conversor_texto_fala.getProperty('voices')
    conversor_texto_fala.setProperty('voice', voices[1].id)
    conversor_texto_fala.say(audio)
    conversor_texto_fala.runAndWait()


# Função para reproduzir som do alarme
def reproduzir_som(caminho_do_som):
    pygame.mixer.init()
    pygame.mixer.music.load(caminho_do_som)
    pygame.mixer.music.play()


def parar_reproducao():
    pygame.mixer.music.stop()


def calcular():
    falar("Que operação matemática desejas realizar?")
    operacao = obter_operacao_por_voz()

    while operacao not in ["somar", "subtrair", "multiplicar", "dividir"]:
        falar("Operação inválida. Por favor, escolha uma operação válida.")
        operacao = obter_operacao_por_voz()

    falar("Diga o primeiro número:")
    num1 = obter_numero_por_voz()

    falar("Diga o segundo número:")
    num2 = obter_numero_por_voz()

    if operacao == "somar":
        resultado = num1 + num2
    elif operacao == "subtrair":
        resultado = num1 - num2
    elif operacao == "multiplicar":
        resultado = num1 * num2
    elif operacao == "dividir":
        if num2 == 0:
            resultado = "Não é possível dividir por zero."
        else:
            resultado = num1 / num2

    return resultado


def temporizador(segundos):
    falar(f"Temporizador definido para {segundos} segundos.")

    # Função para contar o tempo e lembrar após o término
    def contar_tempo():
        time.sleep(segundos)
        falar("O tempo acabou!")

    # Iniciando a contagem do tempo em uma thread separada
    thread_temporizador = threading.Thread(target=contar_tempo)
    thread_temporizador.start()


def obter_operacao_por_voz():
    with sr.Microphone() as source:
        reconhecedor.adjust_for_ambient_noise(source)
        falar("Diga a operação desejada.")
        print("Diga a operação desejada:")
        audio = reconhecedor.listen(source)

        try:
            operacao = reconhecedor.recognize_google(audio, language='pt-PT')
            print(f"Operação reconhecida: {operacao}")
            return operacao.lower()
        except sr.UnknownValueError:
            print("Não foi possível entender a operação. Por favor, tente novamente.")
            return obter_operacao_por_voz()
        except sr.RequestError as e:
            print(f"Erro na requisição ao Google: {e}")
            return obter_operacao_por_voz()


def obter_numero_por_voz():
    with sr.Microphone() as source:
        reconhecedor.adjust_for_ambient_noise(source)
        print("Diga o número:")
        audio = reconhecedor.listen(source)

        try:
            numero = float(reconhecedor.recognize_google(audio, language='pt-PT'))
            print(f"Número reconhecido: {numero}")
            return numero
        except sr.UnknownValueError:
            print("Não foi possível entender o número. Por favor, tente novamente.")
            return obter_numero_por_voz()
        except sr.RequestError as e:
            print(f"Erro na requisição ao Google: {e}")
            return obter_numero_por_voz()


# Função para pesquisar no Google
def pesquisar_google(query):
    resultados = list(search(query, num=1, stop=1, pause=2, lang='pt-PT'))
    return resultados


# Função para extrair conteúdo da página
def extrair_conteudo_pagina(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        informacao = soup.get_text()
        return informacao
    except Exception as e:
        return f"Erro ao obter conteúdo da página: {str(e)}"


# Função para pesquisar e ler conteúdo
def pesquisar_e_ler_conteudo(query):
    query = query.strip()
    resultados_pesquisa = pesquisar_google(query)

    for resultado in resultados_pesquisa:
        informacao_encontrada = extrair_conteudo_pagina(resultado)
        print(f"Link do site: {resultado}")  # Adiciona o link do site nos resultados
        falar(informacao_encontrada)


def tocar_alarme(caminho_do_som):
    reproduzir_som(caminho_do_som)


def configurar_e_iniciar_alarme(hora_alarme, caminho_do_som):
    def alarme_thread():
        while True:
            agora = datetime.now()
            if agora.hour == hora_alarme.hour and agora.minute == hora_alarme.minute:
                tocar_alarme(caminho_do_som)
                break
            time.sleep(60)

    thread_alarme = threading.Thread(target=alarme_thread, daemon=True)
    thread_alarme.start()
    return thread_alarme


def adicionar_tarefa():
    falar("O que gostarias de adicionar à tua lista de tarefas?")
    tarefa = microfone().lower()
    LISTA_TAREFAS.append(tarefa)
    falar(f"Tarefa adicionada: {tarefa}")


def verificar_e_executar_tarefas():
    while True:
        agora = datetime.now()
        if agora.hour == 21 and agora.minute == 0:
            falar("Já concluíste as tarefas pendentes?")
            resposta = microfone().lower()
            if 'sim' in resposta:
                LISTA_TAREFAS.clear()
                falar("Ótimo! Todas as tarefas foram concluídas.")
            else:
                falar("Aqui estão as tarefas pendentes:")
                for i, tarefa in enumerate(LISTA_TAREFAS, start=1):
                    falar(f"Tarefa {i}: {tarefa}")
        time.sleep(60)


def lembrar_tarefas():
    while True:
        agora = datetime.now()
        for tarefa in LISTA_TAREFAS:
            horario_tarefa = agora.replace(second=0, microsecond=0) + timedelta(hours=1)
            if agora < horario_tarefa <= agora + timedelta(minutes=15):
                falar(f"Lembrete: Tens a tarefa {tarefa} em 15 minutos.")
        time.sleep(60)


def tocar_musica_spotify_atualizado():
    falar("Qual música e qual artista queres ouvir?")
    resposta_usuario = microfone().lower()
    partes = resposta_usuario.split(" e ")

    if len(partes) == 2:
        musica, artista = partes
        falar(f"A procurar por {musica} de {artista} no Spotify...")
        results = sp.search(q=f"{musica} {artista}", limit=1, type='track')

        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            sp.start_playback(uris=[track_uri])
            falar(f"A reproduzir {musica} de {artista} no Spotify.")
        else:
            falar("Desculpa, não foi possível encontrar a música. Tenta novamente.")
    else:
        falar("Por favor, fornece tanto o nome da música quanto do artista.")


def consultar_noticias(portal):
    if portal == 'publico':
        feed_url = 'https://www.publico.pt/rss'
    elif portal == 'observador':
        feed_url = 'https://feeds.feedburner.com/PublicoRSS'
    else:
        return "Desculpa, não reconheço esse portal de notícias."

    feed = feedparser.parse(feed_url)

    noticias = []
    for entry in feed.entries[:5]:
        noticias.append(entry.title)

    return noticias


def adicionar_item_mercado(item):
    itens_mercado.append(item)


def lembrar_compras():
    if itens_mercado:
        falar("Lembrar de compras: ")
        for item in itens_mercado:
            falar(f"Não te esqueças de comprar {item}.")
        falar("Não te esqueças de ir às compras!")
    else:
        falar("Não há itens na lista")
    time.sleep(86400)


def suspender_escuta():
    global ESCUTANDO
    ESCUTANDO = False
    evento_suspensao.set()
    print("Escuta suspensa.")


def ativar_escuta():
    global ESCUTANDO
    ESCUTANDO = True
    evento_suspensao.clear()
    print("A aguardar comando...")


def tempo():
    agora = datetime.now()
    hora_atual = agora.strftime("%H:%M")
    falar(f"A hora atual é: {hora_atual}")


def data():
    agora = datetime.now()
    data_atual = agora.strftime("Dia %d do Mês de %m de %Y")
    falar(data_atual)


def obter_temperatura(cidade):
    api_key = '81100e467b5b9ca05b0477784f56cd84'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric'

    response = requests.get(url)
    dados_clima = response.json()

    if response.status_code == 200:
        temperatura = dados_clima['main']['temp']
        falar(f"A temperatura em {cidade} é de {temperatura} graus Celsius.")
    else:
        falar("Desculpa, não foi possível obter a temperatura neste momento.")


def microfone():
    with sr.Microphone() as source:
        reconhecedor.adjust_for_ambient_noise(source)
        print("Diz algo...")
        try:
            audio = reconhecedor.listen(source, timeout=30)
            print("A reconhecer...")
            comando = reconhecedor.recognize_google(audio, language='pt-PT')
            print(comando)
            return comando.lower()
        except sr.UnknownValueError:
            print("Não foi possível entender o áudio. Por favor, tenta novamente.")
            return "None"
        except sr.RequestError as e:
            print(f"Erro na requisição ao Google: {e}")
            return "None"


def bem_vindo():
    falar("Olá Miguel. Bem-vindo!")

    agora = datetime.now()
    hora = agora.hour

    if 6 <= hora < 12:
        falar("Bom dia Miguel!")
    elif 12 <= hora < 18:
        falar("Boa tarde Miguel!")
    elif 18 <= hora <= 24:
        falar("Boa noite Miguel!")
    else:
        falar("Bom dia!")


def fazer_beatbox_natural():
    falar("Agora, vou tentar um pouco de beatbox para ti. Preparado?")

    # Sons de beatbox ajustados para uma execução mais natural
    sons_beatbox = ["bts", "cats", "bts", "cats", "bts", "cats", "bts", "cats"]

    for som in sons_beatbox:
        falar(som)
        time.sleep(0.2)


class Personagem:
    def __init__(self, nome, gif_path):
        self.nome = nome
        self.gif_path = gif_path

    def exibir(self, tela):
        # Exibe o GIF do personagem na tela
        # Adicione aqui o código para exibir o GIF na janela
        pass

    def falar(self, texto):
        # Adicione aqui o código para mostrar o texto na janela e sincronizá-lo com a boca do personagem no GIF
        pass


if __name__ == "__main__":
    falar("Bem-vindo!")
    hora_alarme = datetime.now() + timedelta(minutes=1)
    caminho_do_som = ""

    thread_alarme = threading.Thread(target=configurar_e_iniciar_alarme, args=(hora_alarme, caminho_do_som), daemon=True)
    thread_alarme.start()

    while ESCUTANDO:
        print("Escutando...")

        comando = microfone()

        if comando != "None":
            if 'como estás?' in comando:
                print("Estou bem! Obrigado por perguntares. Em que posso ajudar?")
                falar("Estou bem! Obrigado por perguntares.")
            elif 'que dia é hoje' in comando:
                data()
            elif 'que horas são?' in comando:
                tempo()
            elif 'pesquisar na internet' in comando:
                falar("O que gostarias de pesquisar na internet?")
                consulta = microfone()
                resultados_pesquisa = pesquisar_google(consulta)
                for i, resultado in enumerate(resultados_pesquisa, start=1):
                    print(f"Resultado {i}: {resultado}")
                    falar(f"Resultado {i}: {resultado}")
            elif 'calcular' in comando:
                resultado = calcular()
                print("Resultado do calculo efetuado: ", resultado)
                falar(resultado)           
            elif 'definir alarme' in comando:
                falar("A que horas queres definir o alarme?")
                hora_definida = microfone()
                try:
                    hora_alarme = datetime.strptime(hora_definida, "%H:%M")
                    thread_alarme = threading.Thread(target=configurar_e_iniciar_alarme,
                                                      args=(hora_alarme, caminho_do_som), daemon=True)
                    thread_alarme.start()
                except ValueError:
                    falar("Desculpa, não percebi a hora. Por favor, tenta novamente.")
            elif 'voltei' in comando:
                ativar_escuta()
            elif 'até já' in comando:
                suspender_escuta()
                print("A aguardar reativação...")
            elif 'definir tarefa' in comando:
                adicionar_tarefa()
            elif 'temperatura' in comando:
                print("De qual cidade?")
                falar("De qual cidade?")
                cidade = microfone()
                print("A temperatura é de: " + cidade)
                obter_temperatura(cidade)
            elif 'faz um beatbox' in comando:
                fazer_beatbox_natural()
            elif 'reproduzir música' in comando:
                tocar_musica_spotify_atualizado()
            elif 'últimas noticias' in comando:
                falar("Qual portal? Público ou Observador")
                portal = microfone().lower()
                noticias = consultar_noticias(portal)
                for i, noticia in enumerate(noticias, start=1):
                    falar(f"Notícia {i}: {noticia}")
            elif 'compras' in comando:
                falar("Que item queres adicionar à lista de compras?")
                item = microfone()
                adicionar_item_mercado(item)
                print("Item adicionado: " + item)
                falar("Item adicionado!")
            elif 'desligar' in comando:
                print("Programa encerrado. Até logo!")
                falar("Programa encerrado. Até logo!")
                ESCUTANDO = False  # Encerrar o loop
