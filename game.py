import pygame
import sys
import math
import random
import heapq

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
        self.isDrawable = True
        
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
        self.dir = Direcoes.DIREITA
        super().__init__(x, y)
        # Redefinicao
        self.isEnemy = True

    def move(self, dir):
        if(self.accumulator >= 1):
            self.accumulator = 0
            dx = 0
            dy = 0
            if(dir == Direcoes.DIREITA):
                dx += 1
            elif(dir == Direcoes.ESQUERDA):
                dx -= 1
            elif(dir == Direcoes.BAIXO):
                dy += 1
            else:
                dy -= 1
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

class GhostGulosa(Ghost):
    def __init__(self,pVelocidade,x,y,color):
        super().__init__(pVelocidade,x,y,color)
        
    def update(self,pacman_coluna,pacman_linha):
        self.accumulator += self.velocidade
            
        dx = pacman_coluna - self.posX
        dy = pacman_linha - self.posY
        
        if abs(dx) > abs(dy):
            nova_coluna = self.posX + math.copysign(1,dx)
            nova_linha = self.posY
        else:
            nova_coluna = self.posX
            nova_linha = self.posY + math.copysign(1,dy)
            
        if 0 <= nova_coluna < num_colunas and 0 <= nova_linha < num_linhas:
            if (self.posX - nova_coluna) < 0:
                self.dir = Direcoes.DIREITA
            elif (self.posX - nova_coluna) > 0:
                self.dir = Direcoes.ESQUERDA
            
            if (self.posY - nova_linha) > 0:
                self.dir = Direcoes.CIMA
            elif (self.posY - nova_linha) < 0:
                self.dir = Direcoes.BAIXO


class GhostAStar(Ghost):
    def __init__(self, pVelocidade, x, y, color):
        super().__init__(pVelocidade, x, y, color)
        self.path = []
    
    def update(self, pacman_coluna, pacman_linha):
        # Calcular o caminho usando o algoritmo A* e armazenar na lista de caminhos
        self.path = self.astar_search((self.posX, self.posY), (pacman_coluna, pacman_linha))
        
        # Se o caminho encontrado não estiver vazio, definir a direção para o próximo passo
        if self.path:
            next_step = self.path.pop(0)
            self.dir = self.get_direction(self.posX, self.posY, next_step[0], next_step[1])
        
        # Atualizar a movimentação
        self.accumulator += self.velocidade
        if self.accumulator >= 1:
            self.accumulator = 0
            self.move(self.dir)
    
    def astar_search(self, start, goal):
        # Implementação do algoritmo A* aqui
        
        # Exemplo de estrutura de dados para a busca A*
        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0
        
        while frontier:
            current = heapq.heappop(frontier)[1]
            
            if current == goal:
                break
            
            for next in self.get_neighbors(current):
                new_cost = cost_so_far[current] + 1  # Custo pode ser 1 para cada passo
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.heuristic(goal, next)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current
        
        # Reconstruir o caminho
        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path
    
    def get_neighbors(self, pos):
        # Retornar posições vizinhas (cima, baixo, esquerda, direita)
        # Adicionar lógica para verificar se a posição é válida (dentro do grid)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        neighbors = []
        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            # Verifica se a nova posição está dentro do grid
            if 0 <= new_pos[0] < num_colunas and 0 <= new_pos[1] < num_linhas:
                neighbors.append(new_pos)
        return neighbors
    
    def heuristic(self, goal, next):
        # Heurística de Manhattan
        return abs(goal[0] - next[0]) + abs(goal[1] - next[1])
    
    def get_direction(self, current_x, current_y, next_x, next_y):
        # Retorna a direção com base nas coordenadas atuais e próximas
        if next_x > current_x:
            return Direcoes.DIREITA
        elif next_x < current_x:
            return Direcoes.ESQUERDA
        elif next_y > current_y:
            return Direcoes.BAIXO
        elif next_y < current_y:
            return Direcoes.CIMA
        return Direcoes.DIREITA


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
        self.logicalLab[x][y] = Ghost(0.05, x, y, None)
    
    def addGhostGulosa(self, x, y):
        self.textLab[x][y] = 'G'
        self.logicalLab[x][y] = GhostGulosa(0.05, x, y, None)
        
    def addAStarGhost(self, x, y):
        self.textLab[x][y] = 'S'
        self.logicalLab[x][y] = GhostGulosa(0.05, x, y, None)

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
                elif self.logicalLab[pacPosX + 1][pacPosY].isPickup:
                    # TODO incrementar o score aqui
                    self.logicalLab[pacPosX + 1][pacPosY].isDrawable = False
                
            return False
        elif(pacDir == Direcoes.ESQUERDA):
            if isinstance(self.logicalLab[pacPosX - 1][pacPosY], Entity):
                if self.logicalLab[pacPosX - 1][pacPosY].isCollision:
                    return True
                elif self.logicalLab[pacPosX - 1][pacPosY].isEnemy:
                    pass
                elif self.logicalLab[pacPosX - 1][pacPosY].isPickup:
                    self.logicalLab[pacPosX - 1][pacPosY].isDrawable = False
            return False
        elif(pacDir == Direcoes.BAIXO):
            if isinstance(self.logicalLab[pacPosX][pacPosY + 1], Entity):
                if self.logicalLab[pacPosX][pacPosY + 1].isCollision:
                    return True
                elif self.logicalLab[pacPosX][pacPosY + 1].isEnemy:
                    pass
                elif self.logicalLab[pacPosX][pacPosY + 1].isPickup:
                    self.logicalLab[pacPosX][pacPosY + 1].isDrawable = False
            return False
        else:
            if isinstance(self.logicalLab[pacPosX][pacPosY -1], Entity):
                if self.logicalLab[pacPosX][pacPosY - 1].isCollision:
                    return True
                elif self.logicalLab[pacPosX][pacPosY - 1].isEnemy:
                    pass
                elif self.logicalLab[pacPosX][pacPosY - 1].isPickup:
                    self.logicalLab[pacPosX][pacPosY - 1].isDrawable = False
            return False
    
    def ghostCollideLookAhead(self, ghost):
        if(ghost.dir == Direcoes.DIREITA):
            if isinstance(self.logicalLab[ghost.posX + 1][ghost.posY], Entity):
                if self.logicalLab[ghost.posX + 1][ghost.posY].isCollision:
                    return True
            return False
        elif(ghost.dir == Direcoes.ESQUERDA):
            if isinstance(self.logicalLab[ghost.posX - 1][ghost.posY], Entity):
                if self.logicalLab[ghost.posX - 1][ghost.posY].isCollision:
                    return True
            return False
        elif(ghost.dir == Direcoes.BAIXO):
            if isinstance(self.logicalLab[ghost.posX][ghost.posY + 1], Entity):
                if self.logicalLab[ghost.posX][ghost.posY + 1].isCollision:
                    return True
            return False
        else:
            if isinstance(self.logicalLab[ghost.posX][ghost.posY -1], Entity):
                if self.logicalLab[ghost.posX][ghost.posY - 1].isCollision:
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
                elif symbol == 'G':
                    self.addGhostGulosa(i,j)   
                    
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

lab.addAStarGhost(10,10)

paused = False
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
            elif(evento.key == K_SPACE):
                paused = not paused
            
    if not paused:
        
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

    
        # Desenhar na tela
        tela.fill(preto)
        pacman.draw()

        for line in lab.logicalLab:
            for entity in line:
                if(isinstance(entity, Entity) or isinstance(entity, Ghost)):
                    if isinstance(entity, Ghost):
                        entity.update(pacPosX, pacPosY)
                        while(lab.ghostCollideLookAhead(entity)):
                            entity.dir = random.choice(list(Direcoes))
                        entity.move(entity.dir)
                    if entity.isDrawable:
                        entity.draw()
    else:
        tela.fill(vermelho)
        
    pygame.display.flip()

    # Controle de FPS
    pygame.time.Clock().tick(60)
