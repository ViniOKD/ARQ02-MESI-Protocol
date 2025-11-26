from moesi import *
from functools import wraps



class Leiloeiro(Processador):
    def __init__(self, barramento: Barramento):
        super().__init__(id_processador= 0, cache=Cache(0, barramento))
        self.nome : str = "Leiloeiro"

    def asasa(self, id_comprador, id_item, valor_lance):
        pass


class Compradores(Processador):
    def __init__(self, id_processador: int, cache: Cache, nome : str):
        super().__init__(id_processador, cache)
        self.nome : str = nome

    def verificar_lance(self, id_item):
        """
        Lógica de Negócio: Consulta preço.
        """
        valor = self.load(id_item)
        print(f"[{self.nome}] Consultou Item {id_item}: R$ {valor}")
        return valor
    
    @log
    def dar_lance(self, id_item, valor_lance):
        """
        Lógica de Negócio: Tenta atualizar preço.
        """
        print(f"\n--- [{self.nome}] Tentando lance de R$ {valor_lance} ---")
        valor_atual = self.load(id_item) # Gera Read Miss/Hit

        if valor_lance > valor_atual:
            print(f">> Lance aceito! Atualizando memória...")
            self.store(id_item, valor_lance) # Gera Write Miss/Hit
            return True
        else:
            print(f">> Lance rejeitado (R$ {valor_lance} <= R$ {valor_atual})")
            return False
        
class Leilao():
    def __init__(self, leiloeiro: Leiloeiro, compradores: list[Compradores], id_item: int):
        self.leiloeiro = leiloeiro
        self.compradores = compradores
        self.id_item = id_item

    def dar_inicio(self):
        self.items =[]
        pass 

    def finalizar(self):
        self.items = []
        pass


global aa
aa = ""

def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global aa
        aa += f"Chamando {func.__name__} com args: {args}, kwargs: {kwargs}\n"
        resultado = func(*args, **kwargs)
        aa += f"Função {func.__name__} retornou: {resultado}\n"
        return resultado
    return wrapper

# TV -> 120,00 
# valor p1 -> 100 -> NAO
# valor p2 -> 150 -> SIM

def leilao():
    bs = Barramento(RAM())

    leiloeiro = Leiloeiro(bs)
    c1 = Compradores(1, Cache(1, bs), nome="Comprador 1")
    c2 = Compradores(2, Cache(2, bs), nome="Comprador 2")
    c3 = Compradores(3, Cache(3, bs), nome="Comprador 3")



def main():
    leilao()

if __name__ == "__main__":
    main()