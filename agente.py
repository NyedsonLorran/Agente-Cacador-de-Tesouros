import random    # biblioteca para gerar valores aleatorios 
import tkinter as tk  # biblioteca para ter uma interface
from collections import deque #  estrutura de dados para busca em largura 

# Configurações do mapa
N = 8           # linhas
M = 8           # colunas
TAMANHO_CASA = 50  # tamanho de cada casa/quadado do mapa

# Símbolos no mapa
LIVRE = "."
OBST = "X"
POCO = "P"
TESOURO = "T"
DICA_TESOURO = "+"
DICA_POCO = "-"
DESCONHECIDO = "?"

class AgenteExplorador:
    def __init__(self, canvas):
        self.canvas = canvas
        
        self.mapa_real, self.pos, self.pos_tesouro = self.CriarMapaComChegada() 
        self.limite_tics = 100  # limite máximo de tics/passos
        self.tic = 0            # contador de tics/passos

   # caregamento das imagens de cada casa da interface 
        self.img_livre = tk.PhotoImage(file="icons/caminho.gif")
        self.img_obst = tk.PhotoImage(file="icons/obstaculo.gif")
        self.img_poco = tk.PhotoImage(file="icons/poco.gif")
        self.img_tesouro = tk.PhotoImage(file="icons/tesouro.gif")
        self.img_dica_ouro = tk.PhotoImage(file="icons/caminho.gif") # a ideia é não ficar visivel na interface a dica do tesouro 
        self.img_dica_poco = tk.PhotoImage(file="icons/caminho.gif") # não ficara visivel tambem a dica de pocos 
        self.img_agente = tk.PhotoImage(file="icons/agente.gif")

        self.mapa_parcial = [[DESCONHECIDO for _ in range(M)] for _ in range(N)] #criação do mapa parcialmente conhecido na visão do agente
        self.mapa_parcial[self.pos[0]][self.pos[1]] = LIVRE

    
    def CriarMapaComChegada(self): #gera o mapa e com a certeza de que possiu forma de chegar ao tesouro 
        while True:
            mapa = [[LIVRE for _ in range(M)] for _ in range(N)]

            # Coloca os 10 obstáculos no mapa
            for _ in range(10):
                x, y = random.randint(0, N-1), random.randint(0, M-1)
                mapa[x][y] = OBST

            # Coloca os 5 poços sem a posibilidade de colocar onde já existe os 10 obstaculos 
            pos_pocos = []
            for _ in range(5):
                while True:
                    x, y = random.randint(0, N-1), random.randint(0, M-1)
                    if mapa[x][y] == LIVRE:
                        mapa[x][y] = POCO
                        pos_pocos.append((x,y))
                        break

            pos_inicial = (N-1, 0)

            # Coloca o tesouro em uma posição livre
            while True:
                x, y = random.randint(0, N-1), random.randint(0, M-1)
                if mapa[x][y] == LIVRE:
                    mapa[x][y] = TESOURO
                    pos_tesouro = (x, y)
                    break

            # Testa se existe caminho do agente até o tesouro para não ter risco de não ter como chegar até ele
            if self.ExisteCaminho(mapa, pos_inicial, pos_tesouro):

                # Adiciona pistas de tesouro ao redor (+)
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = pos_tesouro[0]+dx, pos_tesouro[1]+dy
                    if 0 <= nx < N and 0 <= ny < M:
                        if mapa[nx][ny] == LIVRE: # antes de colocar verifica se não possui um outro 'objeto' no espaço evitando erros
                            mapa[nx][ny] = DICA_TESOURO

                # Adiciona pistas de poço ao redor (-)
                for (px, py) in pos_pocos:
                    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                        nx, ny = px+dx, py+dy
                        if 0 <= nx < N and 0 <= ny < M:
                            if mapa[nx][ny] == LIVRE: # antes de colocar verifica se não possui um outro 'objeto' no espaço evitando erros
                                mapa[nx][ny] = DICA_POCO

                return mapa, pos_inicial, pos_tesouro

    def PodeAndar(self, celula): # evita obstaculos e o poço
        return celula not in [OBST, POCO]

    # garante que existe posibilidade de ir até o tesouro 
    def ExisteCaminho(self, mapa, start, destino):
        visitados = set()
        fila = deque([start]) # usa a busca em largura para verificar se há um caminho entre os pontos
        visitados.add(start)

        while fila:
            x, y = fila.popleft()
            if (x,y) == destino:
                return True
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = x+dx, y+dy
                if 0 <= nx < N and 0 <= ny < M:
                    if (nx, ny) not in visitados and self.PodeAndar(mapa[nx][ny]):
                        visitados.add((nx, ny))
                        fila.append((nx, ny))
        return False
    
    # mostra as posições vizinhas
    def Vizinhos(self, pos): 
        x, y = pos
        viz = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < N and 0 <= ny < M:
                viz.append((nx, ny))
        return viz
    
    # Atualiza o mapa do agente com as informações das casas vizinhas.
    def AtualizarMapaParcial(self):
        for nx, ny in self.Vizinhos(self.pos):
            if 0 <= nx < N and 0 <= ny < M:
                self.mapa_parcial[nx][ny] = self.mapa_real[nx][ny]

    # usa a busca em largura para procurar uma casa desconhecida ou ate o tesouro 
    def EscolherProximoMovimento(self):
        visitados = set()
        fila = deque()
        fila.append((self.pos, [self.pos]))
        visitados.add(self.pos)

        while fila:
            (x, y), caminho = fila.popleft()

            if self.mapa_parcial[x][y] == TESOURO and (x,y) != self.pos:
                return caminho[1]

            if self.mapa_parcial[x][y] == DESCONHECIDO and (x,y) != self.pos:
                return caminho[1]

            for nx, ny in self.Vizinhos((x,y)):
                if (nx, ny) not in visitados:
                    celula = self.mapa_parcial[nx][ny]
                    if celula in [LIVRE, TESOURO, DESCONHECIDO, DICA_TESOURO, DICA_POCO]:
                        visitados.add((nx, ny))
                        fila.append(((nx, ny), caminho + [(nx, ny)]))

        return None

    def Mover(self):
        self.tic += 1  # Incrementa +1 tic/passo
        print(f"Tic/Passo {self.tic}: Agente na posição {self.pos}")

        if self.tic > self.limite_tics:
            print(f"Limite de tics/passos ({self.limite_tics}) atingido. Parando a execução.")
            return

       
        # percebe e atualiza 
        self.AtualizarMapaParcial()

        # escolhe a decisão
        prox = self.EscolherProximoMovimento()

        # e faz o movimento 
        if prox is None: #caso não exita movimento possivel para fazer 
            print("Nenhum movimento possível para explorar. Parando.")
            self.Desenhar()
            return
        self.pos = prox
        self.Desenhar() 

         #Verifica se o agente encontrou o tesouro
        if self.mapa_parcial[self.pos[0]][self.pos[1]] == TESOURO: 
            print("Tesouro encontrado! 🏆")
            return

        self.canvas.after(500, self.Mover)

    def Desenhar(self):
        self.canvas.delete("all") #rezeta o mapa anterior 
        for i in range(N):
            for j in range(M):
                x1 = j * TAMANHO_CASA
                y1 = (N - 1 - i) * TAMANHO_CASA

                casa = self.mapa_real[i][j]

                # Escolhe a imagem certa para cada casa do mapa
                if (i, j) == self.pos:
                    img = self.img_agente
                elif casa == OBST:
                    img = self.img_obst
                elif casa == POCO:
                    img = self.img_poco
                elif casa == TESOURO:
                    img = self.img_tesouro
                elif casa == DICA_TESOURO:
                    img = self.img_dica_ouro
                elif casa == DICA_POCO:
                    img = self.img_dica_poco
                else:
                    img = self.img_livre  

                self.canvas.create_image(x1, y1, anchor="nw", image=img)

