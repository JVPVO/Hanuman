#Voltei pra essa versão, essa tá limitada a só matriz quadrada (e é mais restrita) (restricao do quadrado menor)
# (resolvi essa restricao mas deixei pq gostei dela)
#desisti da forma recusiva
#testei pra 1000 casos e n teve NENHUM erro (pode ser que eu tenha feito o teste errado tb né kkkk, mas acho q n)

import random

def printar_matriz(matriz):
    print('\033[0m')
    for l in range(len(matriz)):
        for c in range(len(matriz[l])):
            elem = matriz[l][c]

            if elem == 3:
                elem = f'\033[1;31m{elem:2}\033[0m'
            elif elem == 2:
                elem = f'\033[1;33m{elem:2}\033[0m'
            elif elem == 1:
                elem = f'\033[1;32m{elem:2}\033[0m'
            else:
                elem = f'\033[1;30m{elem:2}\033[0m'

            print(f'{elem}', end=' ')
        
        print()
    print()

def printar_matriz_2(matriz):
    print('\033[0m')
    for l in range(len(matriz)):
        for c in range(len(matriz[l])):
            elem = matriz[l][c]
            print(f'{elem:2}', end=' ')
        
        print()
    print()

def get_arround_list(matriz:list, index:tuple):
    '''Retorna o que tem em volta'''

    linha = index[0]
    coluna = index[1]

    max_l = len(matriz) - 1
    max_c = len(matriz[0]) -1 
    
    contador = 0

    if 0 < linha <= max_l and 0 <= coluna <= max_c:
        consulta = matriz[linha-1][coluna]
        ##superior
        contador += 1 if consulta != -1 and consulta != 0 else 0

        
    if 0 <= linha < max_l and 0 <= coluna <= max_c:
        consulta = matriz[linha+1][coluna]
        ##inferior
        contador += 1 if consulta != -1 and consulta != 0 else 0


    if 0 <= linha <= max_l and 0 <= coluna < max_c:
        consulta = matriz[linha][coluna+1]
        ##direita
        contador += 1 if consulta != -1 and consulta != 0 else 0

        
    if 0 <= linha <= max_l and 0 < coluna <= max_c:
        consulta = matriz[linha][coluna-1]
        ##esquerda
        contador += 1 if consulta != -1 and consulta != 0 else 0

    
    return contador

def __cont_emvolta__(matriz_original, lista_Problemas:list = [],):
        '''No final resulta uma matriz que tem quantas salas tem em volta dquele indice
        Essa funcao só ta aqui pra DEBUG'''
        #transfomrar no consertador logo?
        matriz_cont =[]
        linhas = len(matriz_original)
        colunas = len(matriz_original[0])
        for linha in range(linhas):
            temp = []
            for coluna in range(colunas):
                if matriz_original[linha][coluna] != 0 and matriz_original[linha][coluna] != -1:
                    temp.append(get_arround_list(matriz_original, (linha, coluna)))
                else:
                    temp.append(0)
            matriz_cont.append(temp)
        return matriz_cont

def colocar_outras_salas(matriz:list, salas:list, posiveisPosicoes:list):
    #lembrando que da forma que construimos o codigo, as possiveis posicoes já vem randomizadas
    for i, elem in enumerate(salas):
        posciao = posiveisPosicoes[i]
        matriz[posciao[0]][posciao[1]] = elem


def posciao_valida(matriz, l, c, n):
    if matriz[l][c] == 1: # se já tem coisa ali n vamos continuar
        return False
    
    
    direcoes = [[-1, 0], [1, 0], [0, -1], [0, 1]]
    
    #for para contar quantos tem em volta (to verificando os em volta da posicao que quero adcionar)
    for linha, coluna in direcoes:
        atual_l = l + linha
        atual_c = c + coluna

        if get_arround_list(matriz, (atual_l, atual_c)) == 3: # se tem alguem em volta com 3 ligacoes n podemos por mais um em volta
            return False
 
    ############## TIRA TUDO ISSO SE QUISER A FOMACAO QUADRADO (essa formacao quadrado tem um efeito labirintico)
    #Esses ifs todos é pra checar as condicoes necessárias
          #Se tá dentro da matriz ainda        #acima                 #esquerda                  #cima esquerda
    if (0 <= l-1 < n and 0 <= c-1 < n) and (matriz[l-1][c] == 1 and matriz[l][c-1] == 1) and matriz[l-1][c-1] == 1:
        return False
          #Se tá dentro da matriz ainda        #acima                  #direita                  #cima direita
    elif (0 <= l-1 < n and 0 <= c+1 < n) and (matriz[l-1][c] == 1 and matriz[l][c+1] == 1) and matriz[l-1][c+1] == 1:
        return False
          #Se tá dentro da matriz ainda        #abaixo                #esquerda                  #baixo esquerda
    elif (0 <= l+1 < n and 0 <= c-1 < n) and (matriz[l+1][c] == 1 and matriz[l][c-1] == 1) and matriz[l+1][c-1] == 1:
        return False
          #Se tá dentro da matriz ainda        #abaixo                 #direita                  #baixo direita
    elif (0 <= l+1 < n and 0 <= c+1 < n) and (matriz[l+1][c] == 1 and matriz[l][c+1] == 1) and matriz[l+1][c+1] == 1:
        return False
    ##############    


    return True

def gerar_matriz(tamanho:int, qntd:int):
    '''tamanho: tamanho da matriz
    qntd: quantidade de salas'''
    matriz = []
    
    #inicia matriz de 0's
    for _ in range(tamanho):
        matriz.append([0]*tamanho)
    
    #aleatoriza a posicao inicial
    posicao_inicial_l = random.randint(0, tamanho-1)
    posicao_inicial_c = random.randint(0, tamanho-1)
    
    #posciao já começa com 1
    matriz[posicao_inicial_l][posicao_inicial_c] = 1
    
    #essa lista vai ser de todas as posicoes dos que foram colocados (todos que tem 1) (tb vai ser util pra colocar as outras salas dps, loja boss e etc)
    posicao_de_todos = [[posicao_inicial_l, posicao_inicial_c]] #como se fosse um identifiador de cada elemento 
    
    
    direcoes = [[-1, 0], [1, 0], [0, -1], [0, 1]]
                #cima     #baixo  #esquer  #direita
    
    #esse for todo é pra ir adcionando os 1's
    for _ in range(qntd - 1): #-1 pq a gnt já adcionou um ali
        
        random.shuffle(posicao_de_todos) #pra aleatorizar o elemento de partida atual
        
        adicionado = False
        for pos in posicao_de_todos:
            l = pos[0]
            c = pos[1]

            
            random.shuffle(direcoes) #pra ser uma direcao aleatoria
            
            #para cada direção
            for linha, coluna in direcoes:
                atual_l = l + linha
                atual_c = c + coluna

                   #previne acessar fora da memoria                        #funcao pra validar nossas condicoes
                if (0 <= atual_l < tamanho and 0 <= atual_c < tamanho) and posciao_valida(matriz, atual_l, atual_c, tamanho):
                    matriz[atual_l][atual_c] = 1 #coloco 1 de novo na nova posicao
                    
                    #da append na posicao atual pra gnt poder voltar dps
                    posicao_de_todos.append([atual_l, atual_c]) # isso tudo pra n fazer recursiva....
                    
                    adicionado = True
                    break # se adcionei nao passo mais pelas direcoes (é pq eu atualizei a lista posicao_de_todos, preciso dela no meu for)

            
            if adicionado:
                break
        

    colocar_outras_salas(matriz, [2,3], posicao_de_todos)  
    return matriz


n = 6 
max = 29 
matriz = gerar_matriz(n, max)
printar_matriz(matriz)

