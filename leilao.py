from moesi import Estado
from colors import color
from ram import RAM, TAMANHO_RAM
from cache import Cache
from processador import Processador
from barramento import Barramento

# Classe dos itens do leilão
class Item:
    def __init__(self, id_item: int, nome: str, preco_inicial: int):
        """ Representa um item em leilão """
        self.id: int = id_item
        self.nome: str = nome
        self.preco: int = preco_inicial
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

    def verificar_preco(self, item: Item) -> int | None:
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

        print(color(f"\n[{self.nome}] Tentando lance de R$ {valor_lance}", "ciano"))
        if item.encerrado:
            print(color(f"O leilão desse item já foi encerrado.", "vermelho"))
            return False
        
        if valor_lance <= 0:
            print(color(f"Lance inválido. O valor do lance deve ser maior que zero.", "vermelho"))
            return False

        # Gera Read Miss/Hit, na tentativa de ler o valor atual do item
        valor_atual: int | None = self.ler(item.id) # TODO: VER ESSA QUESTÃO DO INT OU FLOAT

        if valor_atual is not None and valor_lance > valor_atual:
            # Se o lance for maior, realiza a escrita do novo valor
            # Gera um Write Miss/Hit
            # Invalida as outras cópias na cache dos outros processadores
            self.escrever(item.id, valor_lance)

            print(color(f"\n[Leilão] Lance aceito! {self.nome} valor R$ {valor_lance}", "verde"))
            return True
        else:
            print(color(f"\n[Leilão] Lance rejeitado! o valor atual é R$ {valor_atual}", "vermelho"))
            return False
        
class Leilao:
    def __init__(self):
        self.ram: RAM = RAM(TAMANHO_RAM) 
        self.barramento: Barramento = Barramento(self.ram)
        self.compradores: list[Comprador] = []
        self.itens: list[Item] = []
        self.id_item_prox: int = 0
        
    def adicionar_item(self, nome: str, preco_inicial: int) -> Item:
        """
        Adiciona um novo item ao leilão, a partir da entrada *nome* e *preco_incial*.
        """
        id = self.id_item_prox
        item: Item = Item(id, nome, preco_inicial)
        self.itens.append(item)

        # Inicializa o preço na RAM
        # Setup inicial, antes dos compradores entrarem em ação
        self.ram.escrever(id, preco_inicial)
        self.id_item_prox += 1  
        print(color(f"[Leilão] Item adicionado: {item}, no endereço {item.id}", "azul_claro"))
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

        print(color(f"[Leilão] Comprador adicionado: {comprador.nome}", "azul_claro"))
        return comprador
    
    def descobrir_vencedor(self, item: Item) -> tuple[Comprador | None, int]:
        """
        Descobre o vencedor do leilão do *item* especificado.
        Se alguma cache tiver o dado em 'MODIFIED' ou 'OWNED', esse é o vencedor."
        """
        linha, comprador = None, None
        
        if self.compradores == []:
            return None, self.ram.ler(item.id)
    
        # Varre as caches dos compradores
        for comprador in self.compradores:
            linha = comprador.cache.buscar_linha(item.id)
            if linha == None:
                continue
            # Se encontrar M ou O
            if linha.estado in [Estado.MODIFIED, Estado.OWNED]:
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
        self.itens.pop(item.id)
        print(color(f"[Leilão] Item encerrado: {item}", "azul_claro"))
        print(color(f"[Leilão] Vencedor: {vencedor.nome if vencedor else 'Nenhum vencedor'}", "verde"))
        print(color(f"[Leilão] Preço final: R$ {preco_final}", "amarelo_claro"))
        print(vencedor.cache)

    def interface(self) -> None:
        """
        Interface simples de linha de comando para interagir com o leilão.
        """
        leilao = True
        while leilao:
       
            print(color("\n--- Menu do Leilão ---", "azul_claro"))
            print("1. Adicionar Item")
            print("2. Adicionar Comprador")
            print("3. Verificar Preço do Item")
            print("4. Dar Lance")
            print("5. Encerrar Leilão do Item")
            print("6. Mostrar as caches")
            print("7. Sair")
            escolha = input(color("Escolha uma opção: ", "azul_claro"))

            if escolha == '1':

                nome = str(input(color("Nome do Item: ", "azul_claro")))
                try:
                    preco_inicial = int(input(color("Preço Inicial: R$ ", "amarelo")))
                    self.adicionar_item(nome, preco_inicial)
                except ValueError:
                    print(color("Preço inválido. Tente novamente.", "vermelho"))

            elif escolha == '2':
                nome = str(input(color("Nome do Comprador: ", "azul_claro")))
                if nome not in self.compradores:
                    self.adicionar_comprador(nome)
                else:
                    print(color("Já existe um comprador de mesmo nome, escolha outro", "vermelho"))

            elif escolha == '3':
                if not self.compradores:
                    print(color("Nenhum comprador cadastrado.", "vermelho"))
                    continue
                if not self.itens:
                    print(color("Nenhum item cadastrado.", "vermelho"))
                    continue

                print(color('\n\nCompradores disponíveis:', "ciano_neon"))
                for comprador in self.compradores:
                    print(color(f"ID: {comprador.id} - Nome: {comprador.nome}", "ciano_claro"))

   
                
                print(color('\nItens disponíveis:', "verde_neon"))
                for item in self.itens:
                    print(color(f"ID: {item.id} - Nome: {item.nome}", "verde"))
                


                try:

                    id_comp = int(input(color("\n\nID do Comprador: ", "ciano_neon")))
                    item_id = int(input(color("\nID do Item: ", "verde_neon")))
                    print("\n\n")
                    if 0 <= id_comp < len(self.compradores) and 0 <= item_id < len(self.itens):
                        self.compradores[id_comp].verificar_preco(self.itens[item_id])
                    else:
                        print(color("ID inválido. Tente novamente.", "vermelho"))
                # ValueError - caso o input não seja um número
                # IndexError - caso o ID não exista na lista
                except (ValueError, IndexError):
                    print(color("ID inválido. Tente novamente.", "vermelho"))
                
            elif escolha == '4':
                if not self.compradores:
                    print(color("Nenhum comprador cadastrado.", "vermelho"))
                    continue
                if not self.itens:
                    print(color("Nenhum item cadastrado.", "vermelho"))
                    continue
                print(color('\n\nCompradores disponíveis:', "ciano_neon"))
                for comprador in self.compradores:
                    print(color(f"ID: {comprador.id} - Nome: {comprador.nome}", "ciano_claro"))

                print(color('\n\nItens disponíveis:', "verde_neon"))
                for item in self.itens:
                   print(color(f"ID: {item.id} - Nome: {item.nome}", "verde"))

                try:
                    id_comp = int(input(color("\n\nID do Comprador: ", "ciano_neon")))
                    item_id = int(input(color("\nID do Item: ", "verde_neon")))
                    valor_lance = int(input(color("\nValor do Lance: R$ ", "amarelo_claro")))
                    print("\n\n")
                    if 0 <= id_comp < len(self.compradores) and 0 <= item_id < len(self.itens):
                        self.compradores[id_comp].dar_lance(self.itens[item_id], valor_lance)
                    else:
                        print(color("ID inválido. Tente novamente.", "vermelho"))
                except (ValueError, IndexError):
                    print(color("ID inválido. Tente novamente.", "vermelho"))

                    
            elif escolha == '5': # TODO: adicionar verificação de IDs
                if not self.itens:
                    print(color("Nenhum item cadastrado.", "vermelho"))
                    continue

                print(color('Itens disponíveis:', "verde_neon"))
                for item in self.itens:
                    print(color(f"ID: {item.id} - Nome: {item.nome}", "verde"))
                item_id = int(input(color("ID do Item: ", "verde_neon")))
                if item_id < 0 or item_id >= len(self.itens):
                    print(color("ID inválido. Tente novamente.", "vermelho"))
                else:
                    self.encerrar_item(self.itens[item_id])

            elif escolha == '6':
                print(color("\n--- Caches dos Compradores ---", "azul_claro"))
                for comprador in self.compradores:
                    print(color(f"\nComprador: {comprador.nome}", "ciano_claro"))
                    print(comprador.cache)

            elif escolha == '7':
                leilao = False
                print(color("Encerrando o leilão. Obrigado por participar!", "amarelo_claro"))
            else:
                print(color("Opção inválida. Tente novamente.", "vermelho"))
            


