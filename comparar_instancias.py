import networkx as nx
from ortools.linear_solver import pywraplp
import time
import random
import matplotlib.pyplot as plt
import numpy as np

def resolver_max_cut(num_vertices, num_arestas, nome_instancia, limite_tempo):
    print(f"Processando instância: {nome_instancia}...")
    
    # 1. GERAR A INSTÂNCIA
    G = nx.gnm_random_graph(num_vertices, num_arestas)
    for u, v in G.edges():
        G[u][v]['weight'] = random.randint(1, 5)

    # 2. MODELAGEM (OR-Tools - SCIP)
    solver = pywraplp.Solver.CreateSolver('SCIP')
    solver.SetTimeLimit(limite_tempo * 1000) # Limite em milissegundos

    x = {node: solver.BoolVar(f'x_{node}') for node in G.nodes()}
    y = {(u, v): solver.BoolVar(f'y_{u}_{v}') for u, v in G.edges()}

    objective = solver.Objective()
    for u, v in G.edges():
        objective.SetCoefficient(y[(u, v)], float(G[u][v]['weight']))
    objective.SetMaximization()

    # Quebra de Simetria
    solver.Add(x[0] == 0)

    # Restrições de Corte
    for u, v in G.edges():
        solver.Add(y[(u, v)] <= x[u] + x[v])
        solver.Add(y[(u, v)] <= 2 - (x[u] + x[v]))

    # 3. RESOLUÇÃO
    inicio = time.time()
    status = solver.Solve()
    fim = time.time()

    tempo_execucao = fim - inicio
    
    valor_objetivo = objective.Value() if status in [pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE] else 0

    return {
        "instancia": nome_instancia,
        "variaveis": solver.NumVariables(),
        "restricoes": solver.NumConstraints(),
        "tempo": tempo_execucao,
        "corte": valor_objetivo
    }

def gerar_graficos_comparativos(resultados):
    # Preparando os dados
    nomes = [r['instancia'] for r in resultados]
    tempos = [r['tempo'] for r in resultados]
    variaveis = [r['variaveis'] for r in resultados]
    restricoes = [r['restricoes'] for r in resultados]
    cortes = [r['corte'] for r in resultados]

    # Configurando a figura com 3 subplots lado a lado
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle('Análise Comparativa de Complexidade: Max-Cut em PLI', fontsize=16, fontweight='bold')

    x = np.arange(len(nomes))
    largura = 0.35

    # ---------------------------------------------------------
    # GRÁFICO 1: Crescimento do Modelo (Variáveis e Restrições)
    # ---------------------------------------------------------
    rects1 = ax1.bar(x - largura/2, variaveis, largura, label='Variáveis (x+y)', color='#1f77b4')
    rects2 = ax1.bar(x + largura/2, restricoes, largura, label='Restrições', color='#ff7f0e')
    
    ax1.set_title('Tamanho do Modelo Matemático')
    ax1.set_ylabel('Quantidade')
    ax1.set_xticks(x)
    ax1.set_xticklabels(nomes)
    ax1.legend()
    # Adicionando os valores em cima das barras
    ax1.bar_label(rects1, padding=3)
    ax1.bar_label(rects2, padding=3)

    # ---------------------------------------------------------
    # GRÁFICO 2: Tempo de Processamento
    # ---------------------------------------------------------
    bars_tempo = ax2.bar(nomes, tempos, color='#2ca02c')
    ax2.set_title('Esforço Computacional')
    ax2.set_ylabel('Tempo (Segundos)')
    ax2.axhline(y=15, color='r', linestyle='--', label='Timeout (15s)') # Linha de timeout
    ax2.legend()
    
    for bar in bars_tempo:
        yval = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, yval + 0.2, f'{yval:.2f}s', ha='center', va='bottom')

    # ---------------------------------------------------------
    # GRÁFICO 3: Valor do Corte Máximo
    # ---------------------------------------------------------
    bars_corte = ax3.bar(nomes, cortes, color='#9467bd')
    ax3.set_title('Eficácia: Valor do Corte')
    ax3.set_ylabel('Somatório dos Pesos Cortados')
    
    for bar in bars_corte:
        yval = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2, yval + 1, f'{int(yval)}', ha='center', va='bottom')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # Tamanhos conforme sua apresentação (Slide 13)
    instancias = [
        ("Fácil\n(15 v / 30 a)", 15, 30),
        ("Média\n(50 v / 200 a)", 50, 200),
        ("Difícil\n(150 v / 1000 a)", 150, 1000)
    ]
    
    resultados = []
    for nome, v, e in instancias:
        # Coloquei o limite de tempo de 15 segundos para não demorar muito na instância Difícil
        res = resolver_max_cut(v, e, nome, limite_tempo=15)
        resultados.append(res)
        
    gerar_graficos_comparativos(resultados)