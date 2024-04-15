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

# Criar uma fonte de texto (tamanho 48)
fonte = pygame.font.Font(None, 48)

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
        # TODO isso aqui assume que o pacman nasce no meio da tela, fazer ser possivel ler isso do arquivo
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
    
    def setSpawnLoc(self, x,y):
        self.x = x
        self.y = y

class Entity:
    def __init__(self, pPosX, pPosY):
        self.posX = pPosX
        self.posY = pPosY
        self.isPickup = False
        self.isCollision = False
        self.isPower = False
        self.isEnemy = False
        self.isDrawable = True
        # NOTE esse atributo eh para que seja possivel desenhar os pickups no mesmo quadro em que sejam pegos, para que nao sejam deletados antes
        self.toBePicked = False
        
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
        self.possibleMoveList = []
    
    def genPossibleMoves(self, lab):
        # Limpa a lista de movimentos possiveis sem colisao
        self.possibleMoveList.clear()
        
        logicalLabShallowCopy = lab.getLogicalLab()
        # Se a proxima posicao em cada uma das 4 possibilidades nao estivar ocupada por um obstaculo, adicionar na lista
        if(not isinstance(logicalLabShallowCopy[self.posX + 1][self.posY],Obstacle)):
            self.possibleMoveList.append(Direcoes.DIREITA)
        if (not isinstance(logicalLabShallowCopy[self.posX - 1][self.posY],Obstacle)):
            self.possibleMoveList.append(Direcoes.ESQUERDA)
        if (not isinstance(logicalLabShallowCopy[self.posX][self.posY + 1],Obstacle)):
            self.possibleMoveList.append(Direcoes.BAIXO)
        if (not isinstance(logicalLabShallowCopy[self.posX][self.posY - 1],Obstacle)):
            self.possibleMoveList.append(Direcoes.CIMA)

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
        
    def translateDirectionsToCoords(self):
        res = []
        for entry in self.possibleMoveList:
            if entry == Direcoes.DIREITA:
                res.append((1,0))
            elif entry == Direcoes.ESQUERDA:
                res.append((-1,0))
            elif entry == Direcoes.BAIXO:
                res.append((0,1))
            elif entry == Direcoes.CIMA:
                res.append((0,-1))
                
    def update():
        # TODO calcula o prox movimento
        pass

class GhostGulosa(Ghost):
    def __init__(self,pVelocidade,x,y,color):
        super().__init__(pVelocidade,x,y,color)
    
    def update(self,pacman_coluna,pacman_linha, lab):
        self.accumulator += self.velocidade
            
        dx = pacman_coluna - self.posX
        dy = pacman_linha - self.posY
        
        # Adicionando entropia pra fazer o fantasma ser imprevisivel
        # NOTE explicar isso na apresentacao
        # 1% de chance do fantasma fazer o movimento "Errado"
        if random.random() < 0.01:
            self.dir = random.choice(self.possibleMoveList)
        else:
            if abs(dx) > abs(dy):
                nova_coluna = self.posX + math.copysign(1,dx)
                nova_linha = self.posY
            else:
                nova_coluna = self.posX
                nova_linha = self.posY + math.copysign(1,dy)

            # Pra nao precisar recalcular...
            nDx = self.posX - nova_coluna
            nDy = self.posY - nova_linha

            if 0 <= nova_coluna < num_colunas and 0 <= nova_linha < num_linhas:
                if nDx < 0 and Direcoes.DIREITA in self.possibleMoveList:
                    self.dir = Direcoes.DIREITA
                elif nDx > 0 and Direcoes.ESQUERDA in self.possibleMoveList:
                    self.dir = Direcoes.ESQUERDA

                if nDy > 0 and Direcoes.CIMA in self.possibleMoveList:
                    self.dir = Direcoes.CIMA
                elif nDy < 0 and Direcoes.BAIXO in self.possibleMoveList:
                    self.dir = Direcoes.BAIXO

            if self.dir not in self.possibleMoveList:
                self.dir = random.choice(self.possibleMoveList)


class GhostAStar(Ghost):
    def __init__(self, pVelocidade, x, y, color):
        super().__init__(pVelocidade, x, y, color)
        self.path = []
    
    def update(self, pacman_coluna, pacman_linha, lab):
        # Pra diferenciar os ticks dos fantasmas
        self.accumulator += self.velocidade
        
        # Calcular o caminho usando o algoritmo A* e armazenar na lista de caminhos
        self.path = self.astar_search((self.posX, self.posY), (pacman_coluna, pacman_linha))
        
        # Se o caminho encontrado não estiver vazio, definir a direção para o próximo passo
        if self.path:
            next_step = self.path.pop(0)
            self.dir = self.get_direction(self.posX, self.posY, next_step[0], next_step[1])
        
    
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
            
            for next in self.get_neighbors(current, lab):
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
    
    def get_neighbors(self, pos, lab):
        # Retornar posições vizinhas (cima, baixo, esquerda, direita)
        # Adicionar lógica para verificar se a posição é válida (dentro do grid)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        neighbors = []
        logicalLabShallowCopy = lab.getLogicalLab()
        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            # Verifica se na nova posiscao ha alguma colisao
                
            # Verifica se a nova posição está dentro do grid
            if 0 <= new_pos[0] < num_colunas and 0 <= new_pos[1] < num_linhas and not isinstance(logicalLabShallowCopy[new_pos[0]][new_pos[1]], Obstacle):
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

class SPFGhost(Ghost):
    def __init__(self, pVelocidade, x, y, color):
        super(SPFGhost, self).__init__(pVelocidade, x, y, color)
    
    def update(self, pacPosX, pacPosY, lab):
        self.accumulator += self.velocidade
        start = (self.posX, self.posY)  # Posição inicial do fantasma
        goal = (pacPosX, pacPosY)  # Posição do Pac-Man (destino)
        
        # Estruturas de dados para Dijkstra
        frontier = []  # Fila de prioridade
        heapq.heappush(frontier, (0, start))  # (custo, posição)
        came_from = {}  # Rastrear caminho
        cost_so_far = {}  # Custos acumulados
        came_from[start] = None
        cost_so_far[start] = 0
        
        # Realiza busca
        while frontier:
            # Retira a posição com menor custo acumulado
            current_cost, current_pos = heapq.heappop(frontier)
            
            # Se alcançou o destino, pare
            if current_pos == goal:
                break
            
            # Para cada vizinho do nó atual
            for next_pos in self.get_neighbors(current_pos, lab):
                # Custo acumulado para o vizinho
                new_cost = cost_so_far[current_pos] + 1  # Custo unitário para cada movimento
                
                # Se for um custo menor ou o vizinho ainda não foi visitado
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost  # Prioridade é o custo acumulado
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current_pos
        
        # Reconstrói o caminho
        current = goal
        path = []
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        
        # Se o caminho não estiver vazio, defina a direção para o próximo passo
        if path:
            next_step = path.pop(0)
            self.dir = self.get_direction(self.posX, self.posY, next_step[0], next_step[1])
    
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

    def get_neighbors(self, pos, lab):
        # Retornar posições vizinhas (cima, baixo, esquerda, direita)
        # Adicionar lógica para verificar se a posição é válida (dentro do grid)
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        neighbors = []
        logicalLabShallowCopy = lab.getLogicalLab()
        for dx, dy in directions:
            new_pos = (pos[0] + dx, pos[1] + dy)
            # Verifica se na nova posiscao ha alguma colisao
                
            # Verifica se a nova posição está dentro do grid
            if 0 <= new_pos[0] < num_colunas and 0 <= new_pos[1] < num_linhas and not isinstance(logicalLabShallowCopy[new_pos[0]][new_pos[1]], Obstacle):
                neighbors.append(new_pos)
        return neighbors


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
        self.normalBallAmount = 0
        self.superBallAmount = 0

    def addBall(self, x, y):
        self.textLab[x][y] = 'o'
        self.logicalLab[x][y] = Ball(x, y, None)
        self.normalBallAmount += 1
        

    def addSuperBall(self, x, y):
        self.textLab[x][y] = 'O'
        self.logicalLab[x][y] = SuperBall(x, y, None)
        self.superBallAmount += 1

    def addGhost(self, x, y):
        self.textLab[x][y] = 'X'
        self.logicalLab[x][y] = Ghost(0.05, x, y, None)
    
    def addGhostGulosa(self, x, y):
        self.textLab[x][y] = 'G'
        self.logicalLab[x][y] = GhostGulosa(0.05, x, y, None)
        
    def addAStarGhost(self, x, y):
        self.textLab[x][y] = 'S'
        self.logicalLab[x][y] = GhostAStar(0.05, x, y, None)

    def addSPFGhost(self, x, y):
        self.textLab[x][y] = 'S'
        self.logicalLab[x][y] = SPFGhost(0.05, x, y, None)

    def addObstacle(self, x, y):
        self.textLab[x][y] = 'B'
        self.logicalLab[x][y] =  Obstacle(x, y, None)

    def print(self):
        for x in self.textLab:
            print(' '.join(x))
    
    def collideLookAhead(self, pacDir):
        if(pacDir == Direcoes.DIREITA):
            if isinstance(self.logicalLab[self.pacPosX + 1][self.pacPosY], Entity):
                if self.logicalLab[self.pacPosX + 1][self.pacPosY].isCollision:
                    return True
                elif self.logicalLab[self.pacPosX + 1][self.pacPosY].isEnemy:
                    #TODO resetar o labirinto (pacman e os fantasmas, voltar para o primerio labrinto) aqui
                    #TODO checar se o pacman esta super poderoso, se for o caso, mandar o fantasma de volta a origem
                    pass
                elif self.logicalLab[self.pacPosX + 1][self.pacPosY].isPickup:
                    # TODO incrementar o score aqui
                    self.logicalLab[self.pacPosX + 1][self.pacPosY].toBePicked = True
                
            return False
        elif(pacDir == Direcoes.ESQUERDA):
            if isinstance(self.logicalLab[self.pacPosX - 1][self.pacPosY], Entity):
                if self.logicalLab[self.pacPosX - 1][self.pacPosY].isCollision:
                    return True
                elif self.logicalLab[self.pacPosX - 1][self.pacPosY].isEnemy:
                    pass
                elif self.logicalLab[self.pacPosX - 1][self.pacPosY].isPickup:
                    self.logicalLab[self.pacPosX - 1][self.pacPosY].toBePicked = True
            return False
        elif(pacDir == Direcoes.BAIXO):
            if isinstance(self.logicalLab[self.pacPosX][self.pacPosY + 1], Entity):
                if self.logicalLab[self.pacPosX][self.pacPosY + 1].isCollision:
                    return True
                elif self.logicalLab[self.pacPosX][self.pacPosY + 1].isEnemy:
                    pass
                elif self.logicalLab[self.pacPosX][self.pacPosY + 1].isPickup:
                    self.logicalLab[self.pacPosX][self.pacPosY + 1].toBePicked = True
            return False
        else:
            if isinstance(self.logicalLab[self.pacPosX][self.pacPosY -1], Entity):
                if self.logicalLab[self.pacPosX][self.pacPosY - 1].isCollision:
                    return True
                elif self.logicalLab[self.pacPosX][self.pacPosY - 1].isEnemy:
                    pass
                elif self.logicalLab[self.pacPosX][self.pacPosY - 1].isPickup:
                    self.logicalLab[self.pacPosX][self.pacPosY - 1].toBePicked = True
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
    
    def convertTextLabIntoLogicalLab(self, pac):
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
                    self.addGhostGulosa(i, j)   
                elif symbol == 'S':
                    self.addAStarGhost(i, j)
                elif symbol == 'P':
                    pac.setSpawnLoc(i, j)
                elif symbol == 'F':
                    self.addSPFGhost(i, j)
                elif symbol == ' ':
                    self.logicalLab[i][j] = ' '
                    
    def readLabFromFile(self):
        f = open(f'{lab_index}.txt', 'r')

        data = f.readlines()

        for i, line in enumerate(data):
            for j, char in enumerate(line):
                if i < num_colunas and j < num_linhas:
                    self.textLab[i][j] = char

    def getLogicalLab(self):
        return self.logicalLab
    
    def reset(self):
        self.__init__()


pacman = Pacman()
dirAtual = Direcoes.DIREITA
lab = Labyrinth()

lab.readLabFromFile()
lab.convertTextLabIntoLogicalLab(pacman)


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
            elif(evento.key == K_1):
                lab.reset()
                lab_index = 1
                lab.readLabFromFile()
                lab.convertTextLabIntoLogicalLab(pacman)
            elif(evento.key == K_2):
                lab.reset()
                lab_index = 2
                lab.readLabFromFile()
                lab.convertTextLabIntoLogicalLab(pacman)
            elif(evento.key == K_3):
                lab.reset()
                lab_index = 3
                lab.readLabFromFile()
                lab.convertTextLabIntoLogicalLab(pacman)

            

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

        pacMove = False

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

        # Se o acumulador virou zero, quer dizer que se mexeu
        if(pacman.accumulator == 0):
            pacMove = True
    
        # Desenhar na tela
        tela.fill(preto)
        pacman.draw()

        if pacMove:
            lab.pacPosX = pacman.x
            lab.pacPosY = pacman.y

        for line in lab.logicalLab:
            for entity in line:
                if(isinstance(entity, Entity) or isinstance(entity, Ghost)):
                    if isinstance(entity, Ghost):
                        entity.genPossibleMoves(lab)
                        entity.update(pacman.x, pacman.y, lab)
                        # NOTE mecanismo de unstuck
                        while(lab.ghostCollideLookAhead(entity)):
                            entity.dir = random.choice(list(Direcoes))
                        entity.move(entity.dir)
                    if entity.isDrawable:
                        entity.draw()
                        if entity.toBePicked and pacMove:
                            if pacman.x == entity.posX and pacman.y == entity.posY:
                                if isinstance(entity, Ball):
                                    lab.normalBallAmount -= 1
                                elif isinstance(entity, SuperBall):
                                    lab.superBallAmount -= 1
                                entity.isDrawable = False
                            entity.toBePicked = False
    else:
        s = pygame.Surface((largura, altura))
        s.set_alpha(2)
        s.fill((30,30,30))
        tela.blit(s,(0,0))
        text_surface = fonte.render("PAUSE", True, branco)
        tela.blit(text_surface,((largura - text_surface.get_width()) // 2, (altura - text_surface.get_height()) // 2))
        
        
    pygame.display.flip()

    # Controle de FPS
    pygame.time.Clock().tick(60)
