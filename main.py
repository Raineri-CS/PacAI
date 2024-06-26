import pygame
import sys
import math
import random
import heapq

from pygame.locals import *
from enum import Enum

# Inicialização do Pygame
pygame.init()
pygame.mixer.init()

# Configurações da tela
largura, altura = 810, 600
tela = pygame.display.set_mode((largura, altura))
pygame.display.set_caption("Pac-Man Clone")

# Tamanho de fonte global
FONT_SIZE = 48

# Criar uma fonte de texto (tamanho 48)
fonte = pygame.font.Font(None, FONT_SIZE)

# Criar as texturas a serem usadas
background = pygame.image.load("./resources/bg.png", "bg.png")
labyrinthWall = pygame.image.load("./resources/wall.png","wall.png")
orca = pygame.image.load("./resources/baleia_assassina.png","baleia_assassina.png")
babyShark = pygame.image.load("./resources/babyshark.png","babyshark.png")
perola = pygame.image.load("./resources/perola.png","perola.png")

# Define a musica a tocar
pygame.mixer.music.load("./resources/Aquatic-Ambience.ogg","Aquatic-Ambience.ogg")
# O -1 faz a musica tocar infitamente
pygame.mixer.music.play(-1)

# Cores
preto = (0, 0, 0)
amarelo = (255, 255, 0)
branco = (255, 255, 255)
azul = (0, 0, 255)
vermelho = (255, 0, 0)
rosa =  (255,182,193)
ciano = (0,255,255)
azEscuro = (0,0,200)
corShark = (124,194,230)
corShark2 = (43,127,191)

vermelho = (255, 0, 0)
laranja = (255, 165, 0)
amarelo = (255, 255, 0)
verde = (0, 128, 0)
azul = (0, 0, 255)
anil = (75, 0, 130)
violeta = (238, 130, 238)

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
    

class States(Enum):
    MAIN_MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSED = 4
    EXIT = 5
    
# Controlador de estados da aplicacao
GLOBAL_STATE = States.MAIN_MENU

# Usado para controlar os botoes clicaveis do menu principal
firstRun = True

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

    def draw(self, tela):
        x = self.x * tamanho_celula
        y = self.y * tamanho_celula
        tela.blit(pygame.transform.scale(orca,(tamanho_celula,tamanho_celula)), (x,y))
        # pygame.draw.circle(tela, amarelo, (x, y), self.raio)
        
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
        self.toKillPlayer = False
        
    def draw(self, tela):
        pass
    
    def collide(self, x, y):
        if(self.posX == x and self.posY == y):
            # Colisao
            return True
        return False

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
        self.origin = (0,0)
    
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

    def draw(self, tela):
        x = self.posX * tamanho_celula 
        y = self.posY * tamanho_celula
        localBabyShark = pygame.transform.scale(babyShark, (tamanho_celula , tamanho_celula ))
        toBlitBabyShark = pygame.PixelArray(localBabyShark)
        toBlitBabyShark.replace(corShark, self.color)
        toBlitBabyShark.replace(corShark, self.color)
        
        tela.blit(toBlitBabyShark.make_surface(), (x,y))
        del toBlitBabyShark
        # pygame.draw.circle(tela, self.color, (x, y), self.raio)
        
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
        self.superBallMultiplier = 0.01
        self.normalBallMultiplier = 0.001
        self.velocidadeBase = pVelocidade
    
    def update(self, pacman_coluna, pacman_linha, lab):
        # Pra diferenciar os ticks dos fantasmas
        self.accumulator += self.velocidade
        
        normalBallDiff = lab.totalBallAmount - lab.normalBallAmount
        superBallDiff = lab.totalSuperBallAmount - lab.superBallAmount
        if  normalBallDiff > 0 or superBallDiff > 0 :
            self.velocidade = self.velocidadeBase + (self.velocidadeBase * (superBallDiff * self.superBallMultiplier)) + (self.velocidadeBase * (normalBallDiff * self.normalBallMultiplier))
        
        if random.random() < 0.01:
            self.dir = random.choice(self.possibleMoveList)
        else:
            # Calcular o caminho usando o algoritmo A* e armazenar na lista de caminhos
            self.path = self.astar_search((self.posX, self.posY), (pacman_coluna, pacman_linha), lab)

            # Se o caminho encontrado não estiver vazio, definir a direção para o próximo passo
            if self.path:
                next_step = self.path.pop(0)
                self.dir = self.get_direction(self.posX, self.posY, next_step[0], next_step[1])
        
    
    def astar_search(self, start, goal, lab):
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
        # Posicao inicial do fantasma
        start = (self.posX, self.posY)  
        goal = (pacPosX, pacPosY)  
        
        if random.random() < 0.01:
            self.dir = random.choice(self.possibleMoveList)
        else:
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


class Inky(Ghost):
    def __init__(self, pVelocidade, x, y, color):
        super(Inky, self).__init__(pVelocidade, x, y, color)
        
    def update(self, pacPosX, pacPosY, lab):
        self.accumulator += self.velocidade
        
        
        if random.random() < 0.01:
            self.dir = random.choice(self.possibleMoveList)
        else:
            if random.random() > 0.5:    
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
                
                # Se caminho nao vazio...
                if path:
                    next_step = path.pop(0)
                    self.dir = self.get_direction(self.posX, self.posY, next_step[0], next_step[1])
            else:
                # Calcular o caminho usando A* e armazenar na lista de caminhos
                self.path = self.astar_search((self.posX, self.posY), (pacPosX, pacPosY), lab)
                # Se o caminho encontrado não estiver vazio, definir dir para o prox passo
                if self.path:
                    next_step = self.path.pop(0)
                    self.dir = self.get_direction(self.posX, self.posY, next_step[0], next_step[1])
    
    def astar_search(self, start, goal, lab):
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

    def heuristic(self, goal, next):
        # Heurística de Manhattan
        return abs(goal[0] - next[0]) + abs(goal[1] - next[1])

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

class Clyde(Ghost):
    def __init__(self, pVelocidade, x, y, color):
        super(Clyde, self).__init__(pVelocidade, x, y, color)
    
    def update(self, pacPosX, pacPosY, lab):
        dist = math.sqrt(pow(pacPosX - self.posX, 2) + pow(pacPosY - self.posY, 2))
        self.accumulator += self.velocidade
        start = (self.posX, self.posY)  # Posição inicial do fantasma
        if dist > 3:
            goal = (pacPosX, pacPosY)  # Posição do Pac-Man (destino)
        else:
            goal = self.origin
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
    
    def draw(self, tela):
        x = (self.posX * tamanho_celula)
        y = (self.posY * tamanho_celula)
        
        tela.blit(pygame.transform.scale(labyrinthWall, (tamanho_celula , tamanho_celula )), (x,y))
        # pygame.draw.rect(tela, azul, pygame.Rect(x,y,tamanho_celula/2,tamanho_celula/2))
        pass
    
class SuperBall(Entity):
    def __init__(self, pPosX, pPosY, spriteType):
        super().__init__(pPosX, pPosY)
        self.isPickup = True
        self.isPower = True
    
    def draw(self, tela):
        x = (self.posX * tamanho_celula) + (tamanho_celula / 2)
        y = (self.posY * tamanho_celula) + (tamanho_celula / 2)
        pygame.draw.circle(tela, branco, (x,y), 10)
        pass
    
class Ball(Entity):
    def __init__(self, pPosX, pPosY, spriteType):
        super().__init__(pPosX, pPosY)
        self.isPickup = True
    
    def draw(self, tela):
        x = (self.posX * tamanho_celula) + tamanho_celula/4
        y = (self.posY * tamanho_celula) + tamanho_celula/4
        
        tela.blit(pygame.transform.scale(perola, (tamanho_celula/2, tamanho_celula/2)), (x,y))
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
        self.totalBallAmount = 0
        self.superBallAmount = 0
        self.totalSuperBallAmount =0

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
        self.logicalLab[x][y].origin = (x, y)
        
    def addGhostGulosa(self, x, y):
        self.textLab[x][y] = 'G'
        self.logicalLab[x][y] = GhostGulosa(0.05, x, y, None)
        self.logicalLab[x][y].origin = (x, y)
        
    def addAStarGhost(self, x, y):
        self.textLab[x][y] = 'S'
        self.logicalLab[x][y] = GhostAStar(0.05, x, y, vermelho)
        self.logicalLab[x][y].origin = (x, y)

    def addSPFGhost(self, x, y):
        self.textLab[x][y] = 'L'
        self.logicalLab[x][y] = SPFGhost(0.06, x, y, rosa)
        self.logicalLab[x][y].origin = (x, y)
    
    def addInky(self, x, y):
        self.textLab[x][y] = 'I'
        self.logicalLab[x][y] = Inky(0.07, x, y, ciano)
        self.logicalLab[x][y].origin = (x, y)
        
    def addClyde(self, x, y):
        self.textLab[x][y] = 'C'
        self.logicalLab[x][y] = Clyde(0.1, x, y, azEscuro)
        self.logicalLab[x][y].origin = (x, y)

    def addObstacle(self, x, y):
        self.textLab[x][y] = 'B'
        self.logicalLab[x][y] =  Obstacle(x, y, None)
        

    def print(self):
        for x in self.textLab:
            print(' '.join(x))
    
    def collideLookAhead(self, pacDir):
        dx, dy = 0, 0
        if pacDir == Direcoes.DIREITA:
            dx = 1
        elif pacDir == Direcoes.ESQUERDA:
            dx = -1
        elif pacDir == Direcoes.BAIXO:
            dy = 1
        else:
            dy = -1

        next_entity = self.logicalLab[self.pacPosX + dx][self.pacPosY + dy]
        if isinstance(next_entity, Entity):
            if next_entity.isCollision:
                return True
            elif next_entity.isEnemy:
                next_entity.toKillPlayer = True
            elif next_entity.isPickup:
                next_entity.toBePicked = True
        return False
    
    def ghostCollideLookAhead(self, ghost):
        dx, dy = 0, 0
        if ghost.dir == Direcoes.DIREITA:
            dx = 1
        elif ghost.dir == Direcoes.ESQUERDA:
            dx = -1
        elif ghost.dir == Direcoes.BAIXO:
            dy = 1
        else:
            dy = -1
    
        next_entity = self.logicalLab[ghost.posX + dx][ghost.posY + dy]
        if isinstance(next_entity, Entity) and next_entity.isCollision:
            return True
        elif isinstance(next_entity, Pacman):
            self.toKillPlayer = True
    
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
                elif symbol == 'L':
                    self.addSPFGhost(i, j)
                elif symbol == 'I':
                    self.addInky(i, j)
                elif symbol == 'C':
                    self.addClyde(i, j)
                elif symbol == ' ':
                    self.logicalLab[i][j] = ' '
                    
    def readLabFromFile(self, lab_index):
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


def main():
    # Variaveis globais
    global GLOBAL_STATE
    global firstRun
    # Indice do laboratorio, incrementa conforme os niveis sobem
    lab_index = 1
    clickCoord = (0, 0)
    buttonLocations = []
    pacman = Pacman()
    dirAtual = Direcoes.DIREITA
    lab = Labyrinth()

    title = "Labirinto das pérolas"
    titleRainbow = [vermelho,laranja,amarelo,verde,azul,anil,violeta]
    
    lab.readLabFromFile(lab_index)
    lab.convertTextLabIntoLogicalLab(pacman)
    lab.totalBallAmount = lab.normalBallAmount
    lab.totalSuperBallAmount = lab.superBallAmount

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
                    if GLOBAL_STATE != States.MAIN_MENU:
                        if(GLOBAL_STATE == States.PAUSED):
                            GLOBAL_STATE = States.PLAYING
                        elif(GLOBAL_STATE == States.GAME_OVER):
                            # Volta para o primeiro nivel
                            lab.reset()
                            lab_index = 1
                            lab.readLabFromFile(lab_index)
                            lab.convertTextLabIntoLogicalLab(pacman)
                            lab.totalBallAmount = lab.normalBallAmount
                            lab.totalSuperBallAmount = lab.superBallAmount
                            lab.pacPosX = pacman.x
                            lab.pacPosY = pacman.y
                            GLOBAL_STATE = States.PLAYING
                        else:
                            GLOBAL_STATE = States.PAUSED
                elif(evento.key == K_LEFT):
                    dirAtual = Direcoes.ESQUERDA
                elif(evento.key == K_RIGHT):
                    dirAtual = Direcoes.DIREITA
                elif(evento.key == K_DOWN):
                    dirAtual = Direcoes.BAIXO
                elif(evento.key == K_UP):
                    dirAtual = Direcoes.CIMA
                else:
                    print("Pressed key = " + str(evento.key))
            elif evento.type == MOUSEBUTTONDOWN:
                clickCoord = pygame.mouse.get_pos()
                print(clickCoord)
                for button, representedState in buttonLocations:
                    if button.collidepoint(clickCoord):
                        GLOBAL_STATE = representedState

        if GLOBAL_STATE == States.MAIN_MENU:
            # Fazer o menu
            tela.blit(pygame.transform.scale(background, (largura, altura)), (0,0))
            text_surface = fonte.render("JOGAR", True, branco)
            text_pos = ((largura - text_surface.get_width()) // 2, (altura - text_surface.get_height()) // 1.5)
            tela.blit(text_surface, text_pos)

            text_surface2 = fonte.render("SAIR", True, branco)
            text_pos2 = ((largura - text_surface2.get_width()) // 2, (altura - text_surface2.get_height()) // 1.3)
            tela.blit(text_surface2, text_pos2)

            # Offset
            i = 0
            index_cor = 0  # Índice para acompanhar a cor atual do arco-íris
            largura_letra = fonte.render("E", True, branco).get_width()
            largura_total = largura_letra * len(title)  # Calcula a largura total do título
            for letra in title:
                # Renderiza cada letra com a cor correspondente do arco-íris
                text_srf = fonte.render(letra, True, titleRainbow[index_cor % len(titleRainbow)])
                # Calcula a posição x de cada letra para centralizar o título
                text_pos_x = (largura - largura_total) // 2 + i * largura_letra
                # A posição y permanece a mesma, centralizada verticalmente
                text_pos_y = (altura - text_srf.get_height()) // 5
                # Atualiza a posição onde o texto será renderizado
                text_pos3 = (text_pos_x, text_pos_y)
                tela.blit(text_srf, text_pos3)
                i += 1
                index_cor += 1  # Incrementa o índice para a próxima cor




            if firstRun:
                button_rect = text_surface.get_rect(topleft=text_pos)
                button_rect2 = text_surface2.get_rect(topleft=text_pos2)
                buttonLocations.append((button_rect2, States.EXIT))
                buttonLocations.append((button_rect, States.PLAYING))
                firstRun = False


        elif GLOBAL_STATE == States.PAUSED:
            s = pygame.Surface((largura, altura))
            s.set_alpha(2)
            s.fill((30,30,30))
            tela.blit(s,(0,0))
            text_surface = fonte.render("PAUSE", True, branco)
            tela.blit(text_surface,((largura - text_surface.get_width()) // 2, (altura - text_surface.get_height()) // 2))
            pass

        elif GLOBAL_STATE == States.PLAYING:
            # Troca o nivel se acabou as pellets
            if lab.totalBallAmount <= 0:
                lab.reset()
                if lab_index == 3:
                    lab_index = 1
                lab_index += 1
                lab.readLabFromFile(lab_index)
                lab.convertTextLabIntoLogicalLab(pacman)
                lab.totalBallAmount = lab.normalBallAmount
                lab.totalSuperBallAmount = lab.superBallAmount
                lab.pacPosX = pacman.x
                lab.pacPosY = pacman.y
            
            # Pensando em turnos, o "jogador" vai ser calculado antes das entidades dos fantasmas

            pacMove = False
            ghostMove = False
            
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
                lab.pacPosX = pacman.x
                lab.pacPosY = pacman.y
        
            # Desenhar na tela
            
            tela.blit(pygame.transform.scale(background, (largura, altura)), (0,0))
            pacman.draw(tela)
            priorityDrawList = []
            for line in lab.logicalLab:
                for entity in line:
                    if isinstance(entity, Ghost):
                        entity.genPossibleMoves(lab)
                        entity.update(pacman.x, pacman.y, lab)
                        # NOTE mecanismo de unstuck
                        while(lab.ghostCollideLookAhead(entity)):
                            entity.dir = random.choice(list(Direcoes))
                        entity.move(entity.dir)
                        ghostMove = entity.accumulator == 0

                    if isinstance(entity, Entity) and entity.isDrawable:
                        if isinstance(entity, Ghost):
                            priorityDrawList.append(entity)
                        else:
                            entity.draw(tela)

                        if entity.toBePicked or entity.toKillPlayer or ghostMove or pacMove:
                            if pacman.x == entity.posX and pacman.y == entity.posY:
                                if isinstance(entity, Ball):
                                    lab.totalBallAmount -= 1
                                elif isinstance(entity, SuperBall):
                                    lab.totalBallAmount -= 1
                                elif isinstance(entity, Ghost):
                                    ghostMove = False
                                    GLOBAL_STATE = States.GAME_OVER
                                entity.isDrawable = False
                            entity.toBePicked = False

            for entity in priorityDrawList:
                entity.draw(tela)
            pass
        elif GLOBAL_STATE == States.GAME_OVER:
            s = pygame.Surface((largura, altura))
            s.set_alpha(2)
            s.fill((30,30,30))
            tela.blit(s,(0,0))
            text_surface = fonte.render("MORREU", True, branco)
            tela.blit(text_surface,((largura - text_surface.get_width()) // 2, (altura - text_surface.get_height()) // 2))
        elif GLOBAL_STATE == States.EXIT:
            pygame.quit()
            sys.exit()
        
        pygame.display.flip()

        # Controle de FPS
        pygame.time.Clock().tick(60)
        
if __name__ == '__main__':
    main()
