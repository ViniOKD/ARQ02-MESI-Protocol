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
    """
    Representa um comprador no leilão, capaz de verificar preços e dar lances.
    """
    def __init__(self, id_proc: int, cache: Cache, nome : str):
        super().__init__(id_processador = id_proc, cache = cache)
        self.nome : str = nome 

    def verificar_preco(self, item: Item) -> float | None:
        """
        Verifica o preço atual do item - Uma operação de leitura (READ).
        """
        valor = self.ler(item.id_item)
        print(f"[{self.nome}] Consultou Item {item.id_item}: R$ {valor}")
        return valor
    
    def dar_lance(self, item: Item, valor_lance: float) -> bool:
        """
        Ação de dar um lance, realiza uma leitura (READ) do valor atual e,
        se o lance for maior, realiza uma escrita (WRITE) do novo valor.
        """

        print(f"\n[{self.nome}] Tentando lance de R$ {valor_lance}")
        if item.encerrado:
            print(f"O leilão desse item já foi encerrado.")
            return False
        
        if valor_lance <= 0:
            print(f"Lance inválido. O valor do lance deve ser maior que zero.")

        # Gera Read Miss/Hit, na tentativa de ler o valor atual do item
        valor_atual: int | None = self.ler(item.id_item) 

        if valor_atual is not None and valor_lance > valor_atual:
            # Se o lance for maior, realiza a escrita do novo valor
            # Gera um Write Miss/Hit
            # Invalida as outras cópias na cache dos outros processadores
            self.escrever(item.id_item, valor_lance)

            print(f"\n[Leilão] Lance aceito! {self.nome} valor R$ {valor_lance}")
            return True
        else:
            print(f"\n[Leilão] Lance rejeitado! o valor atual é R$ {valor_atual}")
            return False
        
class Leilao:
    def __init__(self):
        self.ram: RAM = RAM(TAMANHO_RAM) 
        self.barramento: Barramento = Barramento(self.ram)
        self.compradores: list[Comprador] = []
        self.itens: list[Item] = []
        
        # TODO: Verificar outra maneira de gerar IDs únicos
        self.id_item: int = 0
        self.id_processador: int = 0



    def adicionar_item(self, nome: str, preco_inicial: float) -> Item:
        """
        Adiciona um novo item ao leilão, a partir da entrada *nome* e *preco_incial*.
        """
        item: Item = Item(self.id_item, nome, preco_inicial)
        self.itens.append(item)

        # Inicializa o preço na RAM
        # Setup inicial, antes dos compradores entrarem em ação
        self.ram.escrever(self.id_item, preco_inicial)  
        self.id_item += 1

        print(f"[Leilão] Item adicionado: {item}, no endereço {item.id}")

        return item
    
    def adicionar_comprador(self, nome: str) -> Comprador:
        """
        Adiciona um novo comprador ao leilão, a partir do *nome*.
        """

        id_proc = self.id_processador
        # Cria a cache de cada comprador
        cache = Cache(id_proc, self.barramento)

        comprador = Comprador(id_proc, cache, nome)
        self.id_processador += 1
        self.compradores.append(comprador)

        print(f"[Leilão] Comprador adicionado: {comprador.nome}")
    
    def descobrir_vencedor(self, item: Item) -> tuple[Comprador | None, float]:
        """
        Descobre o vencedor do leilão do *item* especificado.
        Se alguma cache tiver o dado em 'MODIFIED' ou 'OWNED', esse é o vencedor."
        """
        
        # Varre as caches dos compradores
        for comprador in self.compradores:
            linha = comprador.cache.buscar_linha(item.item_id)

        # Se encontrar M ou O
        if linha in [Estado.MODIFIED, Estado.OWNED]:
            valor = linha.dado
            if valor is not None:
                return comprador, valor
        
        # Se ninguém tem o dado em M ou O, vale o que está na RAM
        valor_ram = self.ram.ler(item.id_item)
        return None, valor_ram

    def encerrar_item(self, item: Item) -> None:
        """
        Encerra o leilão do *item* especificado.
        """
        if item.encerrado:
            print(f"[Leilão] O leilão desse item já foi encerrado.")
            return

        vencedor, preco_final = self.descobrir_vencedor(self, item)        
        item.encerrado = True
        print(f"[Leilão] Item encerrado: {item}")
        print(f"[Leilão] Vencedor: {vencedor.nome if vencedor else 'Nenhum vencedor'}")
        print(f"[Leilão] Preço final: R$ {preco_final}")

        



