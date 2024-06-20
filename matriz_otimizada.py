# TODO da pra otimizar mtt isso aq
#from salas import Sala #NOTE debug
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
        Essa funcao só ta aqui pra DEBUG!!!!!'''
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
    
    return random.choice(posiveisPosicoes[len(salas):]) #escolher entre todas não lojas e nao boss (posso usar o len pq a de cima funciona em ordem)


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
    
    #essa lista vai ser de todas as posicoes dos que foram colocados (todos que tem 1) (tb vai ser util pra colocar as outras salas dps, loja boss e etc(alem de escolher a posicao inicial do player))
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
        
    #so botei essa funcao abaixo pra dar a posicao do player por didatica msm, poderia se aqui nessa de gerar matriz
    pos_start_player = colocar_outras_salas(matriz, [2,3], posicao_de_todos) #coloca as salas novas e retorna a posciao de start do player
    return matriz, pos_start_player


def coletar_em_volta(matriz:list, index:tuple, linhas, colunas):
    '''Retorna o que tem em volta como lista tipo cima baixo direita esquerda'''

    final = []

    linha = index[0]
    coluna = index[1]

    max_l = linhas - 1
    max_c = colunas -1 

    if 0 < linha <= max_l and 0 <= coluna <= max_c:
        final.append(matriz[linha-1][coluna])
        ##superior
    else:
        final.append(None) #podemos dar append no none mesmo que n tenha nada em volta pq vamos ignorar o none na hora de linkar

        
    if 0 <= linha < max_l and 0 <= coluna <= max_c:
        final.append(matriz[linha+1][coluna])
        ##inferior
    else:
        final.append(None)


    if 0 <= linha <= max_l and 0 <= coluna < max_c:
        final.append(matriz[linha][coluna+1])
        ##direita
    else:
        final.append(None)
        

    if 0 <= linha <= max_l and 0 < coluna <= max_c:
        final.append(matriz[linha][coluna-1])
        ##esquerda
    else:
        final.append(None)    
    

    return final

def super_linkening(matriz_pronta, linha, coluna):
    switch = 0
    for l in range(linha):
        for c in range(switch, coluna+switch, 2): 
            if matriz_pronta[l][c] != None: #verficar se funciona msm
                em_volta = coletar_em_volta(matriz_pronta, (l,c), linha, coluna)
                
                for (pos, elem, pos_relativa) in zip(['cima', 'baixo', 'direita', 'esquerda'], em_volta, ['baixo', 'cima', 'esquerda', 'direita']):
                    #elem:Sala = elem #NOTE debug, tirar dps
                    if elem != None:
                        matriz_pronta[l][c].ponteiro[pos] = elem #a sala atual aponta para os que tao em volta
                        elem.ponteiro[pos_relativa] = matriz_pronta[l][c] #os que tao em volta apontam pra sala atual
                        #precisa da posicao relativa pq o referencial muda
        

        switch = (switch+1)%2 #switch sempre 0 ou  1 #essa ideia do switch divide o trabalho pela metade


if __name__ == '__main__':
    n = 6 
    max = 29 
    matriz, _ = gerar_matriz(n, max)
    printar_matriz(matriz)


