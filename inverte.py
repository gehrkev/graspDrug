def inverte_valores_arquivo(arquivo_entrada, arquivo_saida):
    """
    Lê um arquivo .sparse e cria um novo arquivo com os valores invertidos
    """
    with open(arquivo_entrada, 'r') as f:
        # Lê primeira linha (n, m)
        primeira_linha = f.readline()
        linhas = f.readlines()

    with open(arquivo_saida, 'w') as f:
        # Escreve primeira linha igual
        f.write(primeira_linha)

        # Inverte valores das demais linhas
        for linha in linhas:
            i, j, valor = map(int, linha.split())
            f.write(f"{i} {j} {-valor}\n")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Uso: python inverte.py <arquivo_entrada> <arquivo_saida>")
        print("Exemplo: python inverte.py bd1.sparse bd1_invertido.sparse")
        sys.exit(1)

    arquivo_entrada = sys.argv[1]
    arquivo_saida = sys.argv[2]

    inverte_valores_arquivo(arquivo_entrada, arquivo_saida)
    print(f"Arquivo invertido criado: {arquivo_saida}")