import pygame
import sys

from pygame.locals import *
from enum import Enum


# Inicialização do Pygame
pygame.init()

# Configurações da tela
largura, altura = 800, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Pac-Man Clone")

# Cores
preto = (0, 0, 0)
amarelo = (255, 255, 0)

# Tamanho do grid 
tamanho_celula = 40

num_colunas = largura // tamanho_celula 
num_linhas = altura // tamanho_celula 

# Enum de direcoes para a moviemntacao
class Direcoes(Enum):
    CIMA = 1
    BAIXO = 2
    ESQUERDA = 3
    DIREITA = 4
    
# Classe para o Pac-Man
class Pacman:

    def __init__(self):
        self.coluna = num_colunas // 2
        self.linha = num_linhas // 2
        self.raio = tamanho_celula // 2
        self.velocidade = 0.2 # A 0.2 de velocidade, o pacman anda uma vez a cada 5 ticks
        self.isSuper = False # Estado que controla se o pacman pode comer fantasmas ou nao
        self.accumulator = 0

    def mover(self, dx, dy):
        if(self.accumulator >= 1):
            self.accumulator = 0
            nova_coluna = self.coluna + dx
            nova_linha = self.linha + dy
            # Verifica se a nova posição está dentro do grid
            if 0 <= nova_coluna < num_colunas and 0 <= nova_linha < num_linhas:
                self.coluna = nova_coluna
                self.linha = nova_linha
        else:
            self.accumulator += self.velocidade

    def desenhar(self):
        x = self.coluna * tamanho_celula + self.raio
        y = self.linha * tamanho_celula + self.raio
        pygame.draw.circle(tela, amarelo, (x, y), self.raio)

# Classe base do fantasma TODO
class Ghost:
    def __init__(self, pVelocidade):
        self.coluna = num_colunas // 2
        self.linha = num_linhas // 2
        self.raio = tamanho_celula // 2
        self.velocidade = pVelocidade
        self.accumulator = 0

    def mover(self, dx, dy):
        if(self.accumulator >= 1):
            self.accumulator = 0
            nova_coluna = self.coluna + dx
            nova_linha = self.linha + dy
            # Verifica se a nova posição está dentro do grid
            if 0 <= nova_coluna < num_colunas and 0 <= nova_linha < num_linhas:
                self.coluna = nova_coluna
                self.linha = nova_linha

    def desenhar(self):
        # TODO arrumar o desenho do fantasma aqui
        # TODO talvez deixar esse metodo vazio pois a classe derivada que vai se auto definir o desenho
        x = self.coluna * tamanho_celula + self.raio
        y = self.linha * tamanho_celula + self.raio
        pygame.draw.circle(tela, amarelo, (x, y), self.raio)

# TODO Classes derivadas dos fantasmas

# Classe base de pickups TODO
# Classe base dos obstaculos TODO

class Entity:
    def __init__(self, pPosX, pPosY):
        self.posX = pPosX
        self.posY = pPosY
        
    def desenhar(self):
        pass

class Obstacle(Entity):
    def __init__(self, pPosX, pPosY, spriteType):
        super(pPosX, pPosY)
        self.isCollision = True
        # TODO definir aqui qual tipo de spirte vai ser usada, por exemplo | - + 
        # self.sprite = 
    
    def desenhar(self):
        # TODO desenhar na posicao desejada
        pass
# Instanciacoes
pacman = Pacman()

dirAtual = Direcoes.DIREITA

# Loop principal
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evento.type == KEYDOWN:
            if(evento.key == K_q or evento.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

    # TODO para todo fantasma, verificar se o pacman ocupa a mesma posicao que o mesmo, checando se esta no estado "super"

    # TODO fazer um look ahead para que se veja se o pacman vai colidir com alguma coisa na proxima "andada", se sim, settar uma variavel?
    # NOTE ideia : checar SOMENTE o primeiro bloco na frente da direcao em que o pacman esta se movendo
    
    # Pensando em turnos, o "jogador" vai ser calculado antes das entidades dos fantasmas
    # Logica do player (pacman)
    teclas = pygame.key.get_pressed()
    
    # Usando essa varaivel pois o pacman se move sozinho
    if(teclas[pygame.K_RIGHT]):
        dirAtual = Direcoes.DIREITA
    elif(teclas[pygame.K_LEFT]):
        dirAtual = Direcoes.ESQUERDA
    elif(teclas[pygame.K_DOWN]):
        dirAtual = Direcoes.BAIXO
    elif(teclas[pygame.K_UP]):
        dirAtual = Direcoes.CIMA
        
    if(dirAtual == Direcoes.DIREITA):
        pacman.mover(1,0)
    elif(dirAtual == Direcoes.ESQUERDA):
        pacman.mover(-1,0)
    elif(dirAtual == Direcoes.BAIXO):
        pacman.mover(0,1)
    else:
        pacman.mover(0,-1)
        
        
    # Logica das entidades (Fantasmas)
    # TODO

    # Desenhar na tela
    tela.fill(preto)
    pacman.desenhar()
    pygame.display.flip()

    # Controle de FPS
    pygame.time.Clock().tick(60)  