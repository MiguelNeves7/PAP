import pygame
from pygame.locals import *
import requests

# Inicialização do Pygame
pygame.init()

# Configurações da janela Pygame
largura_janela = 800
altura_janela = 600
janela = pygame.display.set_mode((largura_janela, altura_janela))
pygame.display.set_caption("Animação de Temperatura")

# Carrega as imagens da animação da temperatura (substitua pelas suas próprias imagens)
# As imagens 'sol.png' e 'nuvem.png' devem ser substituídas pelas imagens reais da sua animação
nuvem = pygame.image.load(r'c:\Users\alves\Desktop\PAP\Pap\tempo.jpg')




# Define a posição inicial da animação
pos_x = 0
pos_y = 0

# Função para obter a temperatura de uma cidade da API OpenWeatherMap
def obter_temperatura(cidade):
    api_key = '81100e467b5b9ca05b0477784f56cd84'
    url = f'http://api.openweathermap.org/data/2.5/weather?q={cidade}&appid={api_key}&units=metric'

    response = requests.get(url)
    dados_clima = response.json()

    if response.status_code == 200:
        temperatura = dados_clima['main']['temp']
        return temperatura
    else:
        return None

# Loop principal
executando = True
while executando:
    for evento in pygame.event.get():
        if evento.type == QUIT:
            executando = False

    # Obtém a temperatura da cidade desejada
    cidade = 'Lisbon'  # Substitua 'Lisbon' pela cidade desejada
    temperatura = obter_temperatura(cidade)

    # Lógica de exibição da animação com base na temperatura
    if temperatura is not None:
        if temperatura > 25:
            imagem_atual = nuvem  # Usar imagem de sol se a temperatura for maior que 25°C
        else:
            imagem_atual = nuvem  # Usar imagem de nuvem se a temperatura for menor ou igual a 25°C

        # Limpa a tela
        janela.fill((255, 255, 255))

        # Desenha a animação na tela
        janela.blit(imagem_atual, (pos_x, pos_y))

        # Atualiza a tela
        pygame.display.flip()

# Encerra o Pygame
pygame.quit()
