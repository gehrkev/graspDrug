def ler_dados(arquivo):
    """
    Lê arquivo .sparse e retorna número de componentes, dicionário de pares
        e lista de componentes adjacentes junto ao valor da interação entre eles.
    - Pares não listados tem implicitamente valor zero
    - Pares onde componente i = componente j apontam que o componente
        sozinho produz algum valor à solução
    """
    with open(arquivo, 'r') as f:
        n, m = map(int, f.readline().split())  # num. componentes, pares

        pares = {}
        adj = [[] for _ in range(n)]

        for _ in range(m):
            i, j, valor = map(int, f.readline().split())  # componentes e valor da interação
            i, j = i - 1, j - 1  # ajusta índices

            pares[(i, j)] = valor  # dicionário com chave (i, j) e valor 'valor'
            adj[i].append((j, valor))
            adj[j].append((i, valor))

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
    Trata auto-loops (valor intrínseco do componente) separadamente das interações
    """
    delta = 0
    for j, valor in adj[pos]:
        if j == pos:  # auto-loop
            delta += valor if S[pos] == 0 else -valor
        elif S[j] == 1:  # interação com outro componente
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

        melhor_delta = float('-inf')
        melhor_pos = -1

        if E == 0:  # primeira melhoria
            for pos in range(n):
                delta = calcula_delta(S, pos, adj)
                if delta > 0:
                    S[pos] = 1 - S[pos]  # flip
                    melhorou = True
                    break
        else:  # melhor melhoria
            for pos in range(n):
                delta = calcula_delta(S, pos, adj)
                if delta > melhor_delta:
                    melhor_delta = delta
                    melhor_pos = pos
            if melhor_delta > 0:
                S[melhor_pos] = 1 - S[melhor_pos]
                melhorou = True
                break

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

        # filtra mantendo só os pares onde o delta >= 0
        avaliacoes = [av for av in avaliacoes if av[1] >= 0]
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
    G = 0.3 # (0.0 = guloso até 1.0 = aleatório)
    E = 1 # (0 = primeira melhoria, 1 = melhor melhoria)

    # Mede tempo de leitura
    t_leitura = time.time()
    n, pares, adj = ler_dados(arquivo)
    tempo_leitura = time.time() - t_leitura

    melhor_valor = float('-inf')
    soma_valores = 0
    tempo_total = tempo_leitura  # inicia com o tempo de leitura

    print(f"Executando GRASP para {arquivo}")
    print(f"Parâmetros: G={G}, E={E}")

    for i in range(max_iter):
        print(f"\nReplicação {i + 1}/{max_iter}")

        t_inicio = time.time()
        S, valor = grasp(G, E)
        t_final = time.time() - t_inicio

        soma_valores += valor
        tempo_total += t_final
        melhor_valor = max(melhor_valor, valor)

        print(f"Valor encontrado: {valor}")
        print(f"Tempo GRASP: {t_final:.2f}s")

    valor_medio = soma_valores / max_iter
    tempo_medio = tempo_total / max_iter

    print("\n=== Resultados Finais ===")
    print(f"Melhor valor: {melhor_valor}")
    print(f"Valor médio: {valor_medio:.2f}")
    print(f"Tempo médio: {tempo_medio:.2f}s")
    print(f"Tempo total: {tempo_total:.2f}s")