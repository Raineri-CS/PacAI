import pygame
import sys

from pygame.locals import *
from enum import Enum


# Inicialização do Pygame
pygame.init()

# Configurações da tela
largura, altura = 810, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Pac-Man Clone")

# Cores
preto = (0, 0, 0)
amarelo = (255, 255, 0)
branco = (255, 255, 255)
azul = (0, 0, 255)
vermelho = (255, 0, 0)

#TODO fazer a funcao de reset

# Indice do laboratorio, incrementa conforme os niveis sobem
lab_index = 1

# Tamanho do grid 
tamanho_celula = 30

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
        self.velocidade = 0.12 # A 0.2 de velocidade, o pacman anda uma vez a cada 5 ticks
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

class Entity:
    def __init__(self, pPosX, pPosY):
        self.posX = pPosX
        self.posY = pPosY
        self.isPickup = False
        self.isCollision = False
        self.isPower = False
        self.isEnemy = False
        
    def draw(self):
        pass
    
    def collide(self, x, y):
        if(self.posX == x and self.posY == y):
            # Colisao
            return True
        return False

# TODO Classes derivadas dos fantasmas
# Classe base do fantasma TODO
class Ghost(Entity):
    def __init__(self, pVelocidade, x, y, color):
        self.raio = tamanho_celula // 2
        self.velocidade = pVelocidade
        self.accumulator = 0
        self.color = color
        super().__init__(x, y)
        # Redefinicao
        self.isEnemy = True

    def move(self, dx, dy):
        if(self.accumulator >= 1):
            self.accumulator = 0
            nova_coluna = self.posX + dx
            nova_linha = self.posY + dy
            # Verifica se a nova posição está dentro do grid
            if 0 <= nova_coluna < num_colunas and 0 <= nova_linha < num_linhas:
                self.posX = nova_coluna
                self.posY = nova_linha

    def draw(self):
        # TODO arrumar o desenho do fantasma aqui
        # TODO talvez deixar esse metodo vazio pois a classe derivada que vai se auto definir o desenho
        x = self.posX * tamanho_celula + self.raio
        y = self.posY * tamanho_celula + self.raio
        pygame.draw.circle(tela, vermelho, (x, y), self.raio)
        
    def update():
        # TODO calcula o prox movimento
        pass


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
        self.textLab = [[' ' for _ in range(num_linhas)] for _ in range(num_colunas)]
        self.logicalLab = [[' ' for _ in range(num_linhas)] for _ in range(num_colunas)]
        self.pacPosX = 0
        self.pacPosY = 0

    def addBall(self, x, y):
        self.textLab[x][y] = 'o'
        self.logicalLab[x][y] = Ball(x, y, None)

    def addSuperBall(self, x, y):
        self.textLab[x][y] = 'O'
        self.logicalLab[x][y] = SuperBall(x, y, None)

    def addGhost(self, x, y):
        self.textLab[x][y] = 'X'
        # TODO
        self.logicalLab[x][y] = Ghost(0.05, x, y, None)

    def addObstacle(self, x, y):
        self.textLab[x][y] = 'B'
        self.logicalLab[x][y] =  Obstacle(x, y, None)

    def print(self):
        for x in self.textLab:
            print(' '.join(x))
    
    def collideLookAhead(self, pacDir):
        if(pacDir == Direcoes.DIREITA):
            if isinstance(self.logicalLab[pacPosX + 1][pacPosY], Entity):
                if self.logicalLab[pacPosX + 1][pacPosY].isCollision:
                    return True
                elif self.logicalLab[pacPosX + 1][pacPosY].isEnemy:
                    #TODO resetar o labirinto (pacman e os fantasmas, voltar para o primerio labrinto) aqui
                    #TODO checar se o pacman esta super poderoso, se for o caso, mandar o fantasma de volta a origem
                    pass
                
            return False
        elif(pacDir == Direcoes.ESQUERDA):
            if isinstance(self.logicalLab[pacPosX - 1][pacPosY], Entity):
                if self.logicalLab[pacPosX - 1][pacPosY].isCollision:
                    return True
            return False
        elif(pacDir == Direcoes.BAIXO):
            if isinstance(self.logicalLab[pacPosX][pacPosY + 1], Entity):
                if self.logicalLab[pacPosX][pacPosY + 1].isCollision:
                    return True
            return False
        else:
            if isinstance(self.logicalLab[pacPosX][pacPosY -1], Entity):
                if self.logicalLab[pacPosX][pacPosY - 1].isCollision:
                    return True
            return False
    
    def convertTextLabIntoLogicalLab(self):
        for i, line in enumerate(self.textLab):
            for j, symbol in enumerate(line):
                if symbol == 'o':
                    self.addBall(i,j)
                elif symbol == 'O':
                    self.addSuperBall(i,j)
                elif symbol == 'B':
                    self.addObstacle(i,j)
                elif symbol == 'X':
                    self.addGhost(i,j)
                    pass
                
    def readLabFromFile(self):
        f = open(f'{lab_index}.txt', 'r')

        data = f.readlines()

        for i, line in enumerate(data):
            for j, char in enumerate(line):
                if i < num_colunas and j < num_linhas:
                    self.textLab[i][j] = char



pacman = Pacman()
dirAtual = Direcoes.DIREITA
lab = Labyrinth()

lab.readLabFromFile()
lab.convertTextLabIntoLogicalLab()

lab.addGhost(4,4)

# FIXME remover depois, somente para teste!!!
# for i in range(0,(num_colunas)):
#     for j in range(0, (num_linhas)):
#         if(i == 0 or j == 0 or i+1 == num_colunas or j+1 == num_linhas):
#             lab.addObstacle(i, j)

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
        if not lab.collideLookAhead(dirAtual):   
            pacman.move(1,0)
    elif(dirAtual == Direcoes.ESQUERDA):
        if not lab.collideLookAhead(dirAtual):   
            pacman.move(-1,0)
    elif(dirAtual == Direcoes.BAIXO):
        if not lab.collideLookAhead(dirAtual):   
            pacman.move(0,1)
    else:
        if not lab.collideLookAhead(dirAtual):   
            pacman.move(0,-1)
    
    # Logica das entidades (Fantasmas)
    # TODO

    # Desenhar na tela
    tela.fill(preto)
    pacman.draw()

    for line in lab.logicalLab:
        for entity in line:
            if(isinstance(entity, Entity) or isinstance(entity, Ghost)):
                entity.draw()
            
    pygame.display.flip()

    # Controle de FPS
    pygame.time.Clock().tick(60)  