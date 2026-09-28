import networkx as nx
from ortools.linear_solver import pywraplp
import time
import random

def resolver_max_cut(num_vertices, num_arestas, nome_instancia, limite_tempo=60):
    print(f"\n{'-'*40}")
    print(f"Resolvendo Instância: {nome_instancia.upper()}")
    print(f"Vértices: {num_vertices} | Arestas: {num_arestas}")
    
    # 1. GERAR A INSTÂNCIA (Grafo aleatório com pesos)
    G = nx.gnm_random_graph(num_vertices, num_arestas)
    for u, v in G.edges():
        G[u][v]['weight'] = random.randint(1, 5)
        
    # Exportar os dados da instância para enviar no TP (O que enviar: Arquivos/Dados)
    nome_arquivo = f"instancia_{nome_instancia.lower()}.txt"
    nx.write_weighted_edgelist(G, nome_arquivo)
    print(f"[*] Arquivo de dados salvo: {nome_arquivo}")

    # 2. MODELAGEM MATEMÁTICA (OR-Tools com o solver SCIP)
    # O SCIP é um dos solvers exatos aceitos nas regras do seu trabalho
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        print("Solver SCIP não encontrado.")
        return

    # Definir limite de tempo em milissegundos
    solver.SetTimeLimit(limite_tempo * 1000)

    # Variável X_v: 0 se Sala 1, 1 se Sala 2
    x = {}
    for node in G.nodes():
        x[node] = solver.BoolVar(f'x_{node}')
    
    # Variável Y_ij: 1 se a aresta foi cortada, 0 caso contrário
    y = {}
    for u, v in G.edges():
        y[(u, v)] = solver.BoolVar(f'y_{u}_{v}')

    # Função Objetivo: Maximizar o somatório de W_ij * Y_ij
    objective = solver.Objective()
    for u, v in G.edges():
        objective.SetCoefficient(y[(u, v)], float(G[u][v]['weight']))
    objective.SetMaximization()

    # Quebra de Simetria (Otimização Elegante do slide 10)
    # Fixamos o primeiro vértice na Sala 1
    vertice_pivo = list(G.nodes())[0]
    solver.Add(x[vertice_pivo] == 0, "Quebra_de_Simetria")

    # Restrições de Corte (Painel de Diagnóstico do slide 9)
    for u, v in G.edges():
        solver.Add(y[(u, v)] <= x[u] + x[v], f"Restricao1_{u}_{v}")
        solver.Add(y[(u, v)] <= 2 - (x[u] + x[v]), f"Restricao2_{u}_{v}")

    # 3. RESOLUÇÃO
    inicio_tempo = time.time()
    status = solver.Solve()
    fim_tempo = time.time()

    tempo_execucao = fim_tempo - inicio_tempo
    
    # Coleta de métricas para a tabela de Análise Comparativa
    total_variaveis = solver.NumVariables()
    total_restricoes = solver.NumConstraints()

    # 4. IMPRESSÃO DOS RESULTADOS
    status_str = "Desconhecido"
    if status == pywraplp.Solver.OPTIMAL:
        status_str = "Ótimo (Optimal)"
        print(f"Valor do Corte Máximo: {objective.Value()}")
    elif status == pywraplp.Solver.FEASIBLE:
        status_str = "Subótimo (Timeout)"
        print(f"Timeout atingido. Melhor valor encontrado: {objective.Value()}")
    else:
        status_str = "Timeout/Sem solução"
        print("Timeout atingido antes de encontrar solução!")
    
    print(f"Status do Solver: {status_str}")
    print(f"Tempo de Processamento: {tempo_execucao:.4f} segundos")
    print(f"Total de Variáveis de Decisão (x + y): {total_variaveis}")
    print(f"Total de Restrições Geradas: {total_restricoes}")

    return {
        "instancia": nome_instancia,
        "variaveis": total_variaveis,
        "restricoes": total_restricoes,
        "tempo": tempo_execucao,
        "status": status_str.split(" ")[0]
    }

# =====================================================================
# EXECUÇÃO DAS 3 INSTÂNCIAS (Fácil, Média, Difícil) 
# =====================================================================
if __name__ == "__main__":
    print("Iniciando a bateria de testes do Trabalho Prático (TP-I)...")
    
    # Parâmetros baseados na Análise Comparativa de Complexidade (Slide 13)
    instancias = [
        ("Facil", 15, 30),
        ("Media", 50, 200),
        ("Dificil", 150, 1000)
    ]
    
    resultados = []
    
    for nome, v, e in instancias:
        # Passando um limite de tempo de 15 segundos na difícil para bater com a tabela
        limite = 15 if nome == "Dificil" else 60
        res = resolver_max_cut(v, e, nome, limite_tempo=limite)
        if res:
            resultados.append(res)
        
    print(f"\n{'='*40}")
    print("RESUMO PARA A TABELA DE ANÁLISE (SLIDE 13):")
    print(f"{'Instância':<10} | {'Variáveis':<10} | {'Restrições':<12} | {'Tempo (s)':<10} | {'Status'}")
    print("-" * 65)
    for r in resultados:
        print(f"{r['instancia']:<10} | {r['variaveis']:<10} | {r['restricoes']:<12} | {r['tempo']:<10.4f} | {r['status']}")