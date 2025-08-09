import tkinter as tk  # biblioteca para ter uma interface
import agente  # arquivo agente 

# Criar janela para a interface
janela = tk.Tk()
janela.title("Agente Caçador de Tesouros")

# Criar canvas para desenhar o mapa da interface
canvas = tk.Canvas(
    janela,
    width=agente.M * agente.TAMANHO_CASA,
    height=agente.N * agente.TAMANHO_CASA
)
canvas.pack()

# Criar agente explorador
agente_explorador = agente.AgenteExplorador(canvas)
agente_explorador.Desenhar()

# Iniciar movimentação
janela.after(500, agente_explorador.Mover)

# Loop principal da interface
janela.mainloop()
