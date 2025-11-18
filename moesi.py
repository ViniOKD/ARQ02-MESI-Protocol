from enum import Enum


# estados MOESI em tipo enumerado
class Estados(Enum):
    MODIFIED = "M"
    OWNED = "O"
    EXCLUSIVE = "E"
    SHARED = "S"
    INVALID = "I"


# Representação das linhas de cache que devem conter: Tag (Qual bloco de RAM está armazenado), dado (valor do bloco),
# estado (MOESI), posicao na FIFO (First-In-First-Out - Ordem de chegada)
class LinhasDeCache:
    def __init__(self):
        self.__tag = None
        self.__dado = None
        self.__estado : Estados = None
        self.__pos_fifo = None
    # TODO: FUNCOES
    # Getters e setters
    def set_tag(self, tag):
        self.__tag = tag
    
    def set_dado(self, dado):
        self.__dado = dado

    def set_estado(self, estado):
        self.__estado = estado

    def set_pos(self, pos):
        self.__pos = pos

    def get_tag(self):
        return self.__tag
    
    def get_dado(self):
        return self.__dado
    
    def get_estado(self):
        return self.__estado

    def get_pos(self):
        return self.__pos


## Representação do bloco de ram
## A ram deve possuir um vetor de 50 valores. Cada valor deve ter uma posicao 
## DUVIDA: sera que tem q deixar explicito as posicções ou só botar um get no vetor? tipo return Ram[30] 
class Ram:
    def __init__(self):
        self.__valores = [None for x in range(50)]

    # TODO: GETTERS e SETTERS
    # TODO: FUNCOES

# Controlador de coerencia
class ControladorDeCoerencia:
    def __init__(self):
        self.__id_processador = None
        self.__operacao = None
        self.__endereco_memoria = None
    # TODO: GETTERS e SETTERS
    # TODO: IMPLEMENTAÇÃO DAS REGRAS (OS READ/WRITE MISS/HIT ETC)
