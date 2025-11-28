from moesi import *
import os

# Classe dos itens do leilão
class Item:
    def __init__(self, id_item: int, nome: str, preco_inicial: float):
        """ Representa um item em leilão """
        self.id: int = id_item
        self.nome: str = nome
        self.preco: float = preco_inicial
        self.encerrado: bool = False

    def __repr__(self):
        status = "Encerrado" if self.encerrado else "Ativo"
        return f"{self.nome} | Endereço: {self.id} | Status: {status}"


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
        preco = self.ler(item.id)
        print(f"[{self.nome}] Consultou Item {item.id}: R$ {preco}")
        return preco
    
    def dar_lance(self, item: Item, valor_lance: int) -> bool:
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
        valor_atual: int | None = self.ler(item.id) 

        if valor_atual is not None and valor_lance > valor_atual:
            # Se o lance for maior, realiza a escrita do novo valor
            # Gera um Write Miss/Hit
            # Invalida as outras cópias na cache dos outros processadores
            self.escrever(item.id, valor_lance)

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
        
    def adicionar_item(self, nome: str, preco_inicial: float) -> Item:
        """
        Adiciona um novo item ao leilão, a partir da entrada *nome* e *preco_incial*.
        """
        id = len(self.itens) 
        item: Item = Item(id, nome, preco_inicial)
        self.itens.append(item)

        # Inicializa o preço na RAM
        # Setup inicial, antes dos compradores entrarem em ação
        self.ram.escrever(id, preco_inicial)  

        print(f"[Leilão] Item adicionado: {item}, no endereço {item.id}")

        return item
    
    def adicionar_comprador(self, nome: str) -> Comprador:
        """
        Adiciona um novo comprador ao leilão, a partir do *nome*.
        """

        id_proc = len(self.compradores) 
        # Cria a cache de cada comprador
        cache = Cache(id_proc, self.barramento)

        comprador = Comprador(id_proc, cache, nome)
        self.compradores.append(comprador)
        self.barramento.colocar_cache(cache)
        print(f"[Leilão] Comprador adicionado: {comprador.nome}")
        return comprador
    
    def descobrir_vencedor(self, item: Item) -> tuple[Comprador | None, float]:
        """
        Descobre o vencedor do leilão do *item* especificado.
        Se alguma cache tiver o dado em 'MODIFIED' ou 'OWNED', esse é o vencedor."
        """
        
        # Varre as caches dos compradores
        for comprador in self.compradores:
            linha = comprador.cache.buscar_linha(item.id)
        
        # Se encontrar M ou O
        if linha in [Estado.MODIFIED, Estado.OWNED]:
            valor = linha.dado
            return comprador, valor
        
        # Se ninguém tem o dado em M ou O, vale o que está na RAM
        valor_ram: int = self.ram.ler(item.id)
        return None, valor_ram

    def encerrar_item(self, item: Item) -> None:
        """
        Encerra o leilão do *item* especificado.
        """
        if item.encerrado:
            print(f"[Leilão] O leilão desse item já foi encerrado.")
            return

        vencedor, preco_final = self.descobrir_vencedor(item)        
        item.encerrado = True
        print(f"[Leilão] Item encerrado: {item}")
        print(f"[Leilão] Vencedor: {vencedor.nome if vencedor else 'Nenhum vencedor'}")
        print(f"[Leilão] Preço final: R$ {preco_final}")

    def interface(self) -> None:
        """
        Interface simples de linha de comando para interagir com o leilão.
        """
        leilao = True
        while leilao:
       
            print("\n--- Menu do Leilão ---")
            print("1. Adicionar Item")
            print("2. Adicionar Comprador")
            print("3. Verificar Preço do Item")
            print("4. Dar Lance")
            print("5. Encerrar Leilão do Item")
            print("6. Sair")
            escolha = input("Escolha uma opção: ")

            if escolha == '1':

                nome = str(input("Nome do Item: "))
                preco_inicial = int(input("Preço Inicial: R$ "))
                self.adicionar_item(nome, preco_inicial)
            elif escolha == '2':
                nome = str(input("Nome do Comprador: "))
                self.adicionar_comprador(nome)
            elif escolha == '3':
                print('\n\nCompradores disponíveis:')
                for comprador in self.compradores:
                    print(f"ID: {comprador.id} - Nome: {comprador.nome}")

                print('Itens disponíveis:')
                for item in self.itens:
                    print(f"ID: {item.id} - Nome: {item.nome}")
                try:
                    id = int(input("ID do Comprador: "))
                    item_id = int(input("ID do Item: "))
                    print("\n\n")
                    self.compradores[id].verificar_preco(self.itens[item_id])
                except IndexError:
                    print("ID inválido. Tente novamente.")
                
            elif escolha == '4':
                print('\n\nCompradores disponíveis:')
                for comprador in self.compradores:
                    print(f"ID: {comprador.id} - Nome: {comprador.nome}")

                print('Itens disponíveis:')
                for item in self.itens:
                    print(f"ID: {item.id} - Nome: {item.nome}")
                try:
                    id = int(input("ID do Comprador: "))
                    item_id = int(input("ID do Item: "))
                    valor_lance = int(input("Valor do Lance: R$ "))
                    print("\n\n")
                    self.compradores[id].dar_lance(self.itens[item_id], valor_lance)
                except IndexError:
                    print("ID inválido. Tente novamente.")

                    
            elif escolha == '5':
                item_id = int(input("ID do Item: "))
                if item_id < 0 or item_id >= len(self.itens):
                    print("ID do Item inválido. Tente novamente.")
                else:
                    self.encerrar_item(self.itens[item_id])

            elif escolha == '6':
                leilao = False
                print("Encerrando o leilão. Obrigado por participar!")
            else:
                print("Opção inválida. Tente novamente.")
            
    def limpa_tela(self):
        # Limpa a tela do terminal
        os.system('cls' if os.name == 'nt' else 'clear')





