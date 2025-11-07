from collections import deque


class AFD:
    def __init__(self, estados, alfabeto, transicoes, estado_inicial, estados_finais):
        self.estados = estados
        self.alfabeto = alfabeto
        self.transicoes = transicoes
        self.estado_inicial = estado_inicial
        self.estados_finais = estados_finais

    def transitar(self, estado, simbolo):
        return self.transicoes.get((estado, simbolo))

    def ehFinal(self, estado):
        return estado in self.estados_finais

    def reconhecer(self, cadeia):
        estado_atual = self.estado_inicial
        for simbolo in cadeia:
            if simbolo not in self.alfabeto:
                return False
            proximo = self.transitar(estado_atual, simbolo)
            if proximo is None:
                return False
            estado_atual = proximo
        return self.ehFinal(estado_atual)


class MinimizadorAFD:
    def removerEstadosInalcancaveis(self, afd):
        alcancaveis = set()
        fila = deque([afd.estado_inicial])

        while fila:
            estado = fila.popleft()
            if estado in alcancaveis:
                continue
            alcancaveis.add(estado)

            for simbolo in afd.alfabeto:
                proximo = afd.transitar(estado, simbolo)
                if proximo and proximo not in alcancaveis:
                    fila.append(proximo)

        novos_estados = alcancaveis
        novas_transicoes = {}
        for (e, s), d in afd.transicoes.items():
            if e in alcancaveis and d in alcancaveis:
                novas_transicoes[(e, s)] = d

        novos_finais = set()
        for estado in afd.estados_finais:
            if estado in alcancaveis:
                novos_finais.add(estado)

        return AFD(novos_estados, afd.alfabeto, novas_transicoes,
                   afd.estado_inicial, novos_finais)

    def minimizar(self, afd):
        afd = self.removerEstadosInalcancaveis(afd)

        nao_finais = afd.estados - afd.estados_finais
        particao = []
        if afd.estados_finais:
            particao.append(afd.estados_finais)
        if nao_finais:
            particao.append(nao_finais)

        print("Particao inicial:", particao)

        iteracao = 1
        while True:
            print("Iteracao", iteracao)
            nova_particao = []

            for grupo in particao:
                if len(grupo) == 1:
                    nova_particao.append(grupo)
                    print("Grupo", grupo, "mantido")
                    continue

                assinaturas = {}

                for estado in grupo:
                    assinatura = []
                    for simbolo in sorted(afd.alfabeto):
                        destino = afd.transitar(estado, simbolo)
                        if destino:
                            encontrou = False
                            for i, g in enumerate(particao):
                                if destino in g:
                                    assinatura.append(i)
                                    encontrou = True
                                    break
                            if not encontrou:
                                assinatura.append(-1)
                        else:
                            assinatura.append(-1)

                    assinatura_tupla = tuple(assinatura)

                    if assinatura_tupla not in assinaturas:
                        assinaturas[assinatura_tupla] = set()
                    assinaturas[assinatura_tupla].add(estado)

                print("Grupo", grupo, "dividido em", list(assinaturas.values()))
                for subgrupo in assinaturas.values():
                    nova_particao.append(subgrupo)

            print("Nova particao:", nova_particao)

            if len(nova_particao) == len(particao):
                grupos_iguais = True
                for grupo in particao:
                    if grupo not in nova_particao:
                        grupos_iguais = False
                        break
                if grupos_iguais:
                    print("Particao estabilizou")
                    break

            particao = nova_particao
            iteracao += 1

        print("Particao final:", particao)
        return self.construirAfdMinimo(afd, particao)

    def construirAfdMinimo(self, afd_original, particao):
        estado_para_grupo = {}
        for i, grupo in enumerate(particao):
            for estado in grupo:
                estado_para_grupo[estado] = "q" + str(i)

        print("Mapeamento de estados originais para novos estados:")
        for estado_original, novo_estado in estado_para_grupo.items():
            print(estado_original, "->", novo_estado)

        novos_estados = set()
        for estado in estado_para_grupo.values():
            novos_estados.add(estado)

        novas_transicoes = {}
        novo_estado_inicial = estado_para_grupo[afd_original.estado_inicial]

        novos_estados_finais = set()
        for grupo in particao:
            for estado in grupo:
                if estado in afd_original.estados_finais:
                    estado_grupo = estado_para_grupo[estado]
                    novos_estados_finais.add(estado_grupo)
                    break

        for (estado, simbolo), destino in afd_original.transicoes.items():
            if estado in estado_para_grupo and destino in estado_para_grupo:
                origem_grupo = estado_para_grupo[estado]
                destino_grupo = estado_para_grupo[destino]
                novas_transicoes[(origem_grupo, simbolo)] = destino_grupo

        return AFD(novos_estados, afd_original.alfabeto, novas_transicoes,
                   novo_estado_inicial, novos_estados_finais)


def criarAfdExemplo():
    estados = {'A', 'B', 'C', 'D', 'E', 'F'}
    alfabeto = {'0', '1'}

    transicoes = {
        ('A', '0'): 'B', ('A', '1'): 'C',
        ('B', '0'): 'A', ('B', '1'): 'D',
        ('C', '0'): 'E', ('C', '1'): 'F',
        ('D', '0'): 'E', ('D', '1'): 'F',
        ('E', '0'): 'E', ('E', '1'): 'F',
        ('F', '0'): 'F', ('F', '1'): 'F'
    }

    estado_inicial = 'A'
    estados_finais = {'C', 'D', 'E', 'F'}

    return AFD(estados, alfabeto, transicoes, estado_inicial, estados_finais)


def demonstrarMinimizacao():
    print("MINIMIZACAO DE AFD")

    afd_original = criarAfdExemplo()

    print("AFD ORIGINAL:")
    print("Estados:", afd_original.estados)
    print("Alfabeto:", afd_original.alfabeto)
    print("Estado inicial:", afd_original.estado_inicial)
    print("Estados finais:", afd_original.estados_finais)
    print("Transicoes:")
    for (estado, simbolo), destino in sorted(afd_original.transicoes.items()):
        print("d(", estado, ",", simbolo, ") =", destino)

    print("INICIANDO MINIMIZACAO")
    minimizador = MinimizadorAFD()
    afd_minimo = minimizador.minimizar(afd_original)

    print("AFD MINIMIZADO FINAL:")
    print("Estados:", afd_minimo.estados)
    print("Alfabeto:", afd_minimo.alfabeto)
    print("Estado inicial:", afd_minimo.estado_inicial)
    print("Estados finais:", afd_minimo.estados_finais)
    print("Transicoes:")
    for (estado, simbolo), destino in sorted(afd_minimo.transicoes.items()):
        print("d(", estado, ",", simbolo, ") =", destino)

    print("RESUMO DA REDUCAO:")
    print("Estados:", len(afd_original.estados), "->", len(afd_minimo.estados))
    print("Transicoes:", len(afd_original.transicoes), "->", len(afd_minimo.transicoes))


def exemploSIMPLES():
    print("EXEMPLO SIMPLIFICADO")

    estados = {'A', 'B', 'C'}
    alfabeto = {'0', '1'}
    transicoes = {
        ('A', '0'): 'A', ('A', '1'): 'B',
        ('B', '0'): 'B', ('B', '1'): 'A',
        ('C', '0'): 'C', ('C', '1'): 'B'
    }
    estado_inicial = 'A'
    estados_finais = {'A', 'C'}

    afd = AFD(estados, alfabeto, transicoes, estado_inicial, estados_finais)

    print("AFD com estados redundantes:")
    print("Estados:", afd.estados)
    print("Estados finais:", afd.estados_finais)

    print("INICIANDO MINIMIZACAO")
    minimizador = MinimizadorAFD()
    afd_min = minimizador.minimizar(afd)

    print("AFD MINIMIZADO FINAL:")
    print("Estados:", afd_min.estados)
    print("Estados finais:", afd_min.estados_finais)
    print("Transicoes:")
    for (estado, simbolo), destino in sorted(afd_min.transicoes.items()):
        print("d(", estado, ",", simbolo, ") =", destino)


if __name__ == "__main__":
    demonstrarMinimizacao()
    exemploSIMPLES()
