import pygame
import sys
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

# Tamanho do grid (ajuste conforme necessário)
tamanho_celula = 20
num_colunas = largura // tamanho_celula
num_linhas = altura // tamanho_celula

class Direcoes(Enum):
    """Docstring for Directions."""
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
        self.velocidade = 2  # Reduzimos a velocidade

    def mover(self, dx, dy):
        nova_coluna = self.coluna + dx
        nova_linha = self.linha + dy

        # Verifica se a nova posição está dentro do grid
        if 0 <= nova_coluna < num_colunas and 0 <= nova_linha < num_linhas:
            self.coluna = nova_coluna
            self.linha = nova_linha

    def desenhar(self):
        x = self.coluna * tamanho_celula + self.raio
        y = self.linha * tamanho_celula + self.raio
        pygame.draw.circle(tela, amarelo, (x, y), self.raio)

# Instância do Pac-Man
pacman = Pacman()

dirAtual = Direcoes.DIREITA

# Loop principal
while True:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Lógica do movimento (use as teclas de seta)
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
        

    # Desenhar na tela
    tela.fill(preto)
    pacman.desenhar()
    pygame.display.flip()

    # Controle de FPS
    pygame.time.Clock().tick(15)  # Reduzimos a taxa de quadros por segundo
