## TODO melhorar randomizacao
## TODO ajeitar o poroblema das 4 entradas (possivelmente com uma matriz de cont)
## TODO talvez um numero de salas minimo?
## TODO Consertar problema da formação do tipo prédio

import random

# 1 sala
# 2 loja
# 3 colunas

def printar_matriz(matriz):
    for linha in matriz:
        for coluna in linha:
            print(coluna, end=' ')
        print()

def gerar_matriz(n):
    def get_arround_list(matriz:list, index:tuple):
        '''Retorna o que tem em volta'''
        resultado = []
        linha = index[0]
        coluna = index[1]

        max_l = len(matriz) - 1
        max_c = len(matriz[0]) -1 
        
        contador = 0

        if linha != 0:
            consulta = matriz[linha-1][coluna]
            resultado.append(consulta) ##superior
            contador += 1 if consulta != 0 else 0
            
        if linha != max_l:
            consulta = matriz[linha+1][coluna]
            resultado.append(consulta) ##inferior
            contador += 1 if consulta != 0 else 0

        if coluna != max_c:
            consulta = matriz[linha][coluna+1]
            resultado.append(consulta) ##direita
            contador += 1 if consulta != 0 else 0
            
        if coluna != 0:
            consulta = matriz[linha][coluna-1]
            resultado.append(consulta) ##esquerda
            contador += 1 if consulta != 0 else 0
       
        return resultado, contador
       

    matriz = []
    selecionaveis = [0,1,2,3]
    pesos = [50, 40, 5, 5]


    for l in range(n):
        coluna = []
        for c in range(n):
            coluna.append(0)
        matriz.append(coluna)

    matriz[1][1]=1 ##melhorar isso dps?
    
    for l in range(n):
        for c in range(n):
            sel = random.choices(selecionaveis, weights=pesos)[0]
            
            em_volta, qntd_em_volta = get_arround_list(matriz, [l,c])

            if (sel == 3 or sel == 2) and qntd_em_volta !=0:
                selecionaveis[sel] = 0
                matriz[l][c] = sel
            
            else:
                
                #consertar isso aq q tá bme ruim
                if selecionaveis[2] == 2 or selecionaveis[3] == 3:
                    pesos[3] += 1
                    pesos[2] += 1
                
                if qntd_em_volta != 0:
                    if qntd_em_volta == 1:
                        matriz[l][c] = 1
                    else:
                        matriz[l][c] = sel
                
    return matriz

printar_matriz(gerar_matriz(6))


