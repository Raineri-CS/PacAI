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
branco = (255, 255, 255)
azul = (0, 0, 255)

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
        self.x = num_colunas // 2
        self.y = num_linhas // 2
        self.raio = tamanho_celula // 2
        self.velocidade = 0.2 # A 0.2 de velocidade, o pacman anda uma vez a cada 5 ticks
        self.isSuper = False # Estado que controla se o pacman pode comer fantasmas ou nao
        self.accumulator = 0

    def move(self, dx, dy):
        if(self.accumulator >= 1):
            self.accumulator = 0
            nova_coluna = self.x + dx
            nova_linha = self.y + dy
            # Verifica se a nova posição está dentro do grid
            if 0 <= nova_coluna < num_colunas and 0 <= nova_linha < num_linhas:
                self.x = nova_coluna
                self.y = nova_linha
        else:
            self.accumulator += self.velocidade

    def draw(self):
        x = self.x * tamanho_celula + self.raio
        y = self.y * tamanho_celula + self.raio
        pygame.draw.circle(tela, amarelo, (x, y), self.raio)
        
    def getPosX(self):
        return self.x
    
    def getPosY(self):
        return self.y

# Classe base do fantasma TODO
class Ghost:
    def __init__(self, pVelocidade):
        self.coluna = num_colunas // 2
        self.linha = num_linhas // 2
        self.raio = tamanho_celula // 2
        self.velocidade = pVelocidade
        self.accumulator = 0

    def move(self, dx, dy):
        if(self.accumulator >= 1):
            self.accumulator = 0
            nova_coluna = self.coluna + dx
            nova_linha = self.linha + dy
            # Verifica se a nova posição está dentro do grid
            if 0 <= nova_coluna < num_colunas and 0 <= nova_linha < num_linhas:
                self.coluna = nova_coluna
                self.linha = nova_linha

    def draw(self):
        # TODO arrumar o desenho do fantasma aqui
        # TODO talvez deixar esse metodo vazio pois a classe derivada que vai se auto definir o desenho
        x = self.coluna * tamanho_celula + self.raio
        y = self.linha * tamanho_celula + self.raio
        pygame.draw.circle(tela, amarelo, (x, y), self.raio)

# TODO Classes derivadas dos fantasmas

class Entity:
    def __init__(self, pPosX, pPosY):
        self.posX = pPosX
        self.posY = pPosY
        self.isPickup = False
        self.isCollision = False
        self.isPower = False
        
    def draw(self):
        pass
    
    def collide(self, x, y):
        if(self.posX == x and self.posY == y):
            # Colisao
            return True
        return False

class Obstacle(Entity):
    def __init__(self, pPosX, pPosY, spriteType):
        super().__init__(pPosX, pPosY)
        self.isCollision = True
        # TODO definir aqui qual tipo de spirte vai ser usada, por exemplo | - + 
        # self.sprite = 
    
    def draw(self):
        # TODO desenhar na posicao desejada
        # FIXME
        x = (self.posX * tamanho_celula) + (tamanho_celula / 4)
        y = (self.posY * tamanho_celula) + (tamanho_celula / 4)
        pygame.draw.rect(tela, azul, pygame.Rect(x,y,tamanho_celula/2,tamanho_celula/2))
        pass
    
class SuperBall(Entity):
    def __init__(self, pPosX, pPosY, spriteType):
        super().__init__(pPosX, pPosY)
        self.isPickup = True
        self.isPower = True
    
    def draw(self):
        x = (self.posX * tamanho_celula) + (tamanho_celula / 2)
        y = (self.posY * tamanho_celula) + (tamanho_celula / 2)
        pygame.draw.circle(tela, branco, (x,y), 10)
        pass
    
class Ball(Entity):
    def __init__(self, pPosX, pPosY, spriteType):
        super().__init__(pPosX, pPosY)
        self.isPickup = True
    
    def draw(self):
        x = (self.posX * tamanho_celula) + (tamanho_celula / 2)
        y = (self.posY * tamanho_celula) + (tamanho_celula / 2)
        pygame.draw.circle(tela, branco, (x,y), 5)
        pass

class Labyrinth:
    def __init__(self):
        self.num_linhas = num_linhas
        self.num_colunas = num_colunas
        self.textLab = [[' ' for _ in range(num_colunas)] for _ in range(num_linhas)]
        self.logicalLab = [[' ' for _ in range(num_colunas)] for _ in range(num_linhas)]
        self.pacPosX = 0
        self.pacPosY = 0

    def addBall(self, x, y):
        self.textLab[x][y] = 'o'
        self.logicalLab = Ball(x, y, None)

    def addSuperBall(self, x, y):
        self.textLab[x][y] = 'O'
        self.logicalLab = SuperBall(x, y, None)

    def addGhost(self, x, y):
        self.textLab[x][y] = 'X'
        # TODO
        # self.logicalLab = Ball(x, y, None)

    def addObstacle(self, x, y):
        self.textLab[x][y] = 'B'
        self.logicalLab = Obstacle(x, y, None)

    def print(self):
        for x in self.textLab:
            print(' '.join(x))
    
    def collideLookAhead(self, pacDir):
        if(pacDir == Direcoes.DIREITA):
            if isinstance(self.logicalLab[pacPosX + 1][pacPosY], Entity):
                if self.logicalLab[pacPosX + 1][pacPosY].isCollision:
                    return True
                
            return False
        elif(pacDir == Direcoes.ESQUERDA):
            if isinstance(self.logicalLab[pacPosX - 1][pacPosY], Entity):
                if self.logicalLab[pacPosX + 1][pacPosY].isCollision:
                    return True
            return False
        elif(pacDir == Direcoes.BAIXO):
            if isinstance(self.logicalLab[pacPosX][pacPosY + 1], Entity):
                if self.logicalLab[pacPosX + 1][pacPosY].isCollision:
                    return True
            return False
        else:
            if isinstance(self.logicalLab[pacPosX][pacPosY -1], Entity):
                if self.logicalLab[pacPosX + 1][pacPosY].isCollision:
                    return True
            return False

pacman = Pacman()
dirAtual = Direcoes.DIREITA

# TODO fazer com que essas variaveis sejam arrays
# NOTE ou, alternativamente, criar uma casse labirynth que contem essas infos, podendo ser trocado o labirinto a partir de um arquivo 
obstacles = []

# FIXME remover depois, somente para teste!!!
for i in range(0,num_colunas):
    for j in range(0, num_linhas):
        if(i == 0 or j == 0 or i+1 == num_colunas or j+1 == num_linhas):
            obstacles.append(Obstacle(i, j, None))

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
    
    # TODO talvez mudar isso? Fiz por eficiencia em testar    
    pacPosX = pacman.getPosX()
    pacPosY = pacman.getPosY()
    
    if(dirAtual == Direcoes.DIREITA):
        # if not TODO
        pacman.move(1,0)
    elif(dirAtual == Direcoes.ESQUERDA):
        pacman.move(-1,0)
    elif(dirAtual == Direcoes.BAIXO):
        pacman.move(0,1)
    else:
        pacman.move(0,-1)
    
    # Logica das entidades (Fantasmas)
    # TODO

    # Desenhar na tela
    tela.fill(preto)
    pacman.draw()
    pygame.display.flip()

    # Controle de FPS
    pygame.time.Clock().tick(60)  