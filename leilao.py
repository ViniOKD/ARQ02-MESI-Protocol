from moesi import *

# Classe dos itens do leilão
class Item:
    def __init__(self, id_item: int, nome: str, preco_inicial: float):
        """ Representa um item em leilão """
        self.id: str = id_item
        self.nome: str = nome
        self.preco: float = preco_inicial
        self.encerrado: bool = False

    def __repr__(self):
        status = "Encerrado" if self.encerrado else "Ativo"
        return f"{self.name} | Endereço: {self.id_item} | Status: {status}"


# Classe dos compradores, ou seja, participantes no leilão
class Comprador(Processador):
    def __init__(self, id_processador: int, cache: Cache, nome : str):
        super().__init__(id_processador, cache)
        self.nome : str = nome 

    def verificar_lance(self, id_item):
        """
        Lógica de Negócio: Consulta preço.
        """
        valor = self.ler(id_item)
        print(f"[{self.nome}] Consultou Item {id_item}: R$ {valor}")
        return valor
    
    def dar_lance(self, id_item, valor_lance):
        """
        Lógica de Negócio: Tenta atualizar preço.
        """
        print(f"\n--- [{self.nome}] Tentando lance de R$ {valor_lance} ---")
        valor_atual = self.escrever(id_item) # Gera Read Miss/Hit

        if valor_lance > valor_atual:
            print(f">> Lance aceito! Atualizando memória...")
            self.store(id_item, valor_lance) # Gera Write Miss/Hit
            return True
        else:
            print(f">> Lance rejeitado (R$ {valor_lance} <= R$ {valor_atual})")
            return False
        
class Leilao():
    def __init__(self, compradores: list[Comprador], id_item: int):
        self.compradores = compradores
        self.id_item = id_item

    def dar_inicio(self):
        self.items =[]
        pass 

    def finalizar(self):
        self.items = []
        pass



def leilao():
    bs = Barramento(RAM())

    c1 = Comprador(1, Cache(1, bs), nome="Comprador 1")
    c2 = Comprador(2, Cache(2, bs), nome="Comprador 2")
    c3 = Comprador(3, Cache(3, bs), nome="Comprador 3")



def main():
    leilao()

if __name__ == "__main__":
    main()