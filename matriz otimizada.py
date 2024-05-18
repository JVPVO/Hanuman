import random
###
### VERSAO BETA
###
def printar_matriz_dupla(matriz, m2=[]):
    for l in range(len(matriz)):
        for c in range(len(matriz[l])):
            print(f'{matriz[l][c]:2}', end=' ')

        
        if m2 != []:
            print('    ', end='')
            for c in range(len(matriz[l])):
                print(f'{m2[l][c]:2}', end=' ')
            
        print()
    print()

def get_arround_list(matriz:list, index:tuple):
    '''Retorna o que tem em volta'''
    resultado = [] #cima, baixo, direita, esquerda
    emvolta = []
    linha = index[0]
    coluna = index[1]

    max_l = len(matriz) - 1
    max_c = len(matriz[0]) -1 
    
    contador = 0

    if linha != 0:
        consulta = matriz[linha-1][coluna]
        resultado.append([linha-1,coluna]) ##superior
        emvolta.append(consulta)
        contador += 1 if consulta != -1 and consulta != 0 else 0
    else:
        resultado.append(0)
        emvolta.append(-2)
        
    if linha != max_l:
        consulta = matriz[linha+1][coluna]
        resultado.append([linha+1,coluna]) ##inferior
        emvolta.append(consulta)
        contador += 1 if consulta != -1 and consulta != 0 else 0
    else:
        resultado.append(0)
        emvolta.append(-2)

    if coluna != max_c:
        consulta = matriz[linha][coluna+1]
        resultado.append([linha,coluna+1]) ##direita
        emvolta.append(consulta)
        contador += 1 if consulta != -1 and consulta != 0 else 0
    else:
        resultado.append(0)
        emvolta.append(-2)
        
    if coluna != 0:
        consulta = matriz[linha][coluna-1]
        resultado.append([linha,coluna-1]) ##esquerda
        emvolta.append(consulta)
        contador += 1 if consulta != -1 and consulta != 0 else 0
    else:
        resultado.append(0)
        emvolta.append(-2)
    
    return resultado, contador, emvolta

def validar_em_volta(list):
    for elem in list:
        if elem != 0 and elem != -1:
            return True
    return False

def gerar_matriz(n, minsalas, maxsalas):
    global matriz_num #DEBUG NOTE
    def cont_emvolta(matriz_original, lista_Problemas:list,):
        '''No final resulta uma matriz que tem quantas salas tem em volta dquele indice'''
        #transfomrar no consertador logo?
        matriz_cont =[]
        linhas = len(matriz_original)
        colunas = len(matriz_original[0])

        max_l = linhas - 1
        max_c = colunas -1 
        
        for linha in range(linhas):
            temp = []
            for coluna in range(colunas):
                if matriz_original[linha][coluna] != 0:
                    temp.append(get_arround_list(matriz_original, (linha, coluna))[1])
                else:
                    temp.append(0)
            matriz_cont.append(temp)
        return matriz_cont
            
        
        
    
    def backtracking(matriz:list, index:tuple, selecionaveis, PBLM4:list):
        nonlocal salastotais
        resultado, quantos, emvolta = get_arround_list(matriz, index)
        if salastotais == 0:
            matriz[index[0]][index[1]] = 3 #ja comeca adicionando pelo boss
            salastotais += 1
        else:
            selecionado = random.choices(selecionaveis)[0]
            if validar_em_volta(emvolta):
                matriz[index[0]][index[1]] = selecionado
            else:
                matriz[index[0]][index[1]] = 0
            
            if selecionado != 0:
                salastotais += 1
            
        random.shuffle(resultado)
        for lado in resultado:
            if -1 not in emvolta:
                continue

            if lado != 0 and matriz[lado[0]][lado[1]] == -1:
                backtracking(matriz, lado, selecionaveis, PBLM4)
                #ta se fechando e não ta voltando            
        
        return matriz
            
        

    
    ### Depois remover ####
    assert 0 < minsalas < n**2 
    assert minsalas <= maxsalas < n**2
    #######################

    matriz = []
    
    problemas_Quatro = []
    selecionaveis = [0, 1, 2]
    salastotais = 0

    for _ in range(n):
        matriz.append([-1]*n)
    
    matriz = backtracking(matriz, [3,2], selecionaveis, problemas_Quatro)
    matriz_num = cont_emvolta(matriz, [])
    
    printar_matriz_dupla(matriz, matriz_num) ##debug
    return matriz
    


gerar_matriz(6, 3, 4)
