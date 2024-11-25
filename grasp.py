def ler_dados(arquivo):
    """
    Lê arquivo .sparse e retorna número de componentes e dicionário de pares
    - Ignora auto-loops (pares onde i == j)
    - Pares não listados são implicitamente zero
    """
    with open(arquivo, 'r') as f:
        n, m = map(int, f.readline().split())  # num. componentes, pares

        pares = {}
        adj = [[] for _ in range(n)]  # lista de n listas

        count_ignorados = 0
        for _ in range(m):
            i, j, valor = map(int, f.readline().split())  # componentes e valor da interação
            i, j = i - 1, j - 1  # ajusta índices

            # if i == j:  # ignora auto-loops
            #     count_ignorados += 1
            #     continue  # vai para o próximo ciclo do loop, sem adicionar os valores aos pares e adj abaixo

            pares[(i, j)] = valor  # dicionário com chave (i, j) e valor 'valor'
            adj[i].append((j, valor))
            adj[j].append((i, valor))

        print(f"- Ignorados {count_ignorados} auto-loops")
        print(f"- Total de {len(pares)} pares com interação não-nula")

    return n, pares, adj


def avalia_solucao(S, pares):
    """
    Avalia uma solução calculando a soma dos valores dos pares ativos
    """
    valor = 0
    for (i, j), v in pares.items():
        if S[i] == 1 and S[j] == 1:
            valor += v
    return valor


def calcula_delta(S, pos, adj):
    """
    Calcula o impacto de flipar o bit na posição pos usando lista de adjacência
    """
    delta = 0
    # Só precisa olhar os vizinhos da posição
    for j, valor in adj[pos]:
        if S[j] == 1:
            delta += valor if S[pos] == 0 else -valor
    return delta


def simple_local_search(S0, E, n, adj):
    """
    E = 0: primeira melhoria
    E = 1: melhor melhoria
    """
    S = S0.copy()
    melhorou = True

    while melhorou:
        melhorou = False

        if E == 0:  # primeira melhoria
            for pos in range(n):
                S_vizinho = S.copy()
                S_vizinho[pos] = 1 - S_vizinho[pos]  # flip
                delta = calcula_delta(S, pos, adj)
                if delta > 0:
                    S = S_vizinho.copy()
                    melhorou = True
                    break
        else:  # melhor melhoria
            vizinhos = []
            for pos in range(n):
                S_vizinho = S.copy()
                S_vizinho[pos] = 1 - S_vizinho[pos]
                delta = calcula_delta(S, pos, adj)
                vizinhos.append((S_vizinho, delta))

            # Procura melhor vizinho
            melhor_delta = 0
            melhor_viz = None
            for S_viz, delta in vizinhos:
                if delta > melhor_delta:
                    melhor_delta = delta
                    melhor_viz = S_viz

            if melhor_viz is not None:
                S = melhor_viz.copy()
                melhorou = True

    return S


def construcao(G, n, adj):
    """
    Construção semi-gulosa
    """
    import random

    S = [0] * n
    C = list(range(n))

    while C:
        avaliacoes = []
        for c in C:
            delta = calcula_delta(S, c, adj)
            avaliacoes.append((c, delta))

        avaliacoes = [av for av in avaliacoes if av[1] >= 0] # filtra mantendo só os pares onde o delta >= 0
        if not avaliacoes:
            break

        c_max = max(av[1] for av in avaliacoes)
        c_min = min(av[1] for av in avaliacoes) if len(avaliacoes) > 1 else c_max
        limite = c_max - G * (c_max - c_min)
        rcl = [c for c, v in avaliacoes if v >= limite]

        if rcl:
            c = random.choice(rcl)
            S[c] = 1
            C.remove(c) # remove até C ficar vazio

    return S


def grasp(G, E):
    """
    G - estratégia da construção (0.0 = guloso até 1.0 = aleatório)
    E - estratégia da busca local (0 = primeira melhoria, 1 = melhor melhoria)
    """
    S = construcao(G, n, adj)
    valor_S = avalia_solucao(S, pares)
    SI = S.copy()
    valor_SI = valor_S

    iteracoes = 0
    while iteracoes < max_iterations:
        S = construcao(G, n, adj)
        S = simple_local_search(S, E, n, adj)
        valor_S = avalia_solucao(S, pares)

        if valor_S > valor_SI:
            SI = S.copy()
            valor_SI = valor_S

        iteracoes += 1

    return SI, valor_SI


if __name__ == "__main__":
    import sys
    import time

    if len(sys.argv) != 2:
        print("Uso: python grasp.py <caminho_arquivo>")
        print("Exemplo: python grasp.py ./bancos-dados/bd1.sparse")
        sys.exit(1)

    arquivo = sys.argv[1]
    max_iter = 10  # número de replicações
    max_iterations = 1000  # critério de parada
    G = 0.3
    E = 0

    melhor_valor = float('-inf')
    soma_valores = 0
    tempo_total = 0

    print(f"Executando GRASP para {arquivo}")
    print(f"Parâmetros: G={G}, E={E}")

    for i in range(max_iter):
        print(f"\nReplicação {i + 1}/{max_iter}")

        t_inicio = time.time()
        n, pares, adj = ler_dados(arquivo)
        S, valor = grasp(G, E)
        t_final = time.time() - t_inicio

        soma_valores += valor
        tempo_total += t_final
        melhor_valor = max(melhor_valor, valor)

        print(f"Valor encontrado: {valor}")
        print(f"Tempo: {t_final:.2f}s")

    valor_medio = soma_valores / max_iter
    tempo_medio = tempo_total / max_iter

    print("\n=== Resultados Finais ===")
    print(f"Melhor valor: {melhor_valor}")
    print(f"Valor médio: {valor_medio:.2f}")
    print(f"Tempo médio: {tempo_medio:.2f}s")
    print(S)
