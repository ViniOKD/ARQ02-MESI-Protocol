from __future__ import annotations
from enum import Enum
from collections import deque
from typing import ClassVar
from moesi import *
from functools import wraps



class Item:
    def __init__(self, id_item: int, nome: str, preco_inicial: int):
        self.id = id_item
        self.nome = nome
        self.preco_inicial = preco_inicial
        self.lance_vencedor: int = preco_inicial
        self.comprador_vencedor: Compradores | None = None
        self.historico_lances: list[tuple[str, int]] = []


# 2. Classe Leiloeiro (Coordenador)
class Leiloeiro(Processador):
    def __init__(self, barramento: Barramento):
        # O Leiloeiro usa a Cache 0 para interagir com o Barramento (coordenador)
        super().__init__(id_processador=0, cache=Cache(0, barramento))
        self.nome: str = "Leiloeiro"
        self.barramento = barramento
        self.items: dict[int, Item] = {}

    def adicionar_item(self, id_item: int, nome: str, preco_inicial: int) -> None:
        """
        Inicializa um item na RAM e registra no Leiloeiro.
        (Usa RAM.escrever diretamente para garantir o valor inicial)
        """
        self.barramento.ram.escrever(id_item, preco_inicial)
        self.items[id_item] = Item(id_item, nome, preco_inicial)
        print(f"\n[Leiloeiro] Item '{nome}' (Endereço {id_item}) adicionado com preço inicial R$ {preco_inicial}.")

    def encerrar_leilao(self, id_item: int, compradores: list[Compradores]) -> tuple[int | None, str]:
        """
        Lê o valor final para determinar o lance vencedor.
        O LOAD garante que o valor mais atual (sujo M ou O) seja propagado.
        """
        if id_item not in self.items:
            return None, "Item não encontrado."
        
        item = self.items[id_item]
        
        # O LOAD do Leiloeiro garante que ele obtenha o dado mais atual da rede.
        valor_final = self.load(id_item) 
        item.lance_vencedor = valor_final
        
        vencedor_cache_id = None
        
        # Busca qual cache tem o valor MODIFIED ou OWNED (se o valor final não for o inicial)
        if valor_final > item.preco_inicial:
            for cache in self.barramento.caches:
                linha = cache.buscar_linha(id_item)
                # Verifica se a cache tem o dado válido com o valor final do leilão
                if linha and linha.estado in [Estado.MODIFIED, Estado.OWNED, Estado.SHARED] and linha.dado == valor_final:
                    vencedor_cache_id = cache.id
                    break

        if vencedor_cache_id:
            # Encontra o comprador pelo ID da cache
            item.comprador_vencedor = next((c for c in compradores if c.cache.id == vencedor_cache_id), None)
        else:
             # Ninguém deu lance ou o lance final é o inicial (lido da RAM)
            item.comprador_vencedor = None
        
        print(f"\n{'#'*50}")
        print(f"[Leiloeiro] Leilão do item '{item.nome}' (End. {id_item}) encerrado!")
        if item.comprador_vencedor:
            print(f"GANHADOR: {item.comprador_vencedor.nome} com lance de R$ {item.lance_vencedor}")
        else:
            print(f"Nenhum lance válido. Preço final: R$ {item.lance_vencedor}")
        print(f"{'#'*50}")
        
        return item.lance_vencedor, item.comprador_vencedor.nome if item.comprador_vencedor else "Ninguém"


# 3. Classe Compradores (Agentes)
class Compradores(Processador):
    def __init__(self, id_processador: int, cache: Cache, nome : str):
        super().__init__(id_processador, cache)
        self.nome : str = nome
        self.cache.id = id_processador # Garante que a cache tenha o ID correto do comprador

    def verificar_lance(self, id_item):
        """Lógica de Negócio: Consulta o preço atual."""
        # Usa LOAD, que inicia uma Bus-Read se houver MISS, buscando o valor mais atual.
        return self.load(id_item)
    
    def dar_lance(self, id_item, valor_lance):
        """
        Lógica de Negócio: Tenta atualizar o preço.
        A coerência MOESI garante a atomicidade da tentativa de STORE.
        """
        self.log(f"\n--- Tentando lance em Item {id_item} de R$ {valor_lance} ---")
        
        # 1. LOAD: Obtém o valor atual.
        # MOESI garante que ele obtenha o valor mais atual (seja de RAM, M, O, E ou S).
        valor_atual = self.load(id_item) 

        if valor_lance > valor_atual:
            self.log(f">> Lance de R$ {valor_lance} aceito (Atual: R$ {valor_atual})")
            
            # 2. STORE: Escreve o novo valor.
            # O STORE inicia um Bus-Invalidate, forçando outras caches (M, O, E, S) a invalidar a linha.
            # O Comprador que fizer o STORE com sucesso obtém a linha no estado MODIFIED (M).
            self.store(id_item, valor_lance) 
            return True
        else:
            self.log(f">> Lance rejeitado (R$ {valor_lance} <= R$ {valor_atual})")
            return False


# 4. Função de Simulação
def leilao_simulacao():
    print("\n" + "="*50)
    print("SIMULAÇÃO DE LEILÃO (Lógica de Negócio sobre MOESI)")
    print("="*50)
    
    # Setup
    # Você precisará redefinir RAM, Barramento e as Caches aqui.
    # Exemplo (se as classes base estivessem incluídas):
    # ram = RAM(TAMANHO_RAM)
    # bs = Barramento(ram)
    # leiloeiro = Leiloeiro(bs)
    # compradores = [Compradores(1, Cache(1, bs), nome="C1"), Compradores(2, Cache(2, bs), nome="C2")]
    # bs.colocar_cache(leiloeiro.cache); [bs.colocar_cache(c.cache) for c in compradores]

    # ... (Assumindo que bs, leiloeiro e compradores foram inicializados) ...
    # Exemplo:
    class MockRAM:
        def __init__(self): self.memoria = {10: 0}
        def escrever(self, addr, val): self.memoria[addr] = val
        def ler(self, addr): return self.memoria.get(addr, 0)
    class MockCache(Cache):
         def __init__(self, id_cache, barramento):
            super().__init__(id_cache, barramento, tamanho=1)
    
    ram_mock = MockRAM()
    bs = Barramento(ram_mock)
    
    c1 = Compradores(1, MockCache(1, bs), nome="C1")
    c2 = Compradores(2, MockCache(2, bs), nome="C2")
    c3 = Compradores(3, MockCache(3, bs), nome="C3")
    compradores_list = [c1, c2, c3]

    leiloeiro = Leiloeiro(bs)
    bs.colocar_cache(leiloeiro.cache)
    [bs.colocar_cache(c.cache) for c in compradores_list]

    ITEM_ID = 10 
    leiloeiro.adicionar_item(ITEM_ID, "Estátua Antiga", 100)
    
    # 2. Sequência de Lances

    # C1 dá o primeiro lance
    c1.dar_lance(ITEM_ID, 120) 

    # C2 consulta o valor (lê 120 de C1) e dá um lance maior
    c2.verificar_lance(ITEM_ID) 
    c2.dar_lance(ITEM_ID, 150) 

    # C3 tenta um lance menor - coerência garante que ele veja 150
    c3.dar_lance(ITEM_ID, 140) 

    # C1 tenta dar um lance maior que 150
    c1.dar_lance(ITEM_ID, 180) 

    print("\n--- Estado Final das Caches ---")
    print(c1.cache) 
    print(c2.cache) 
    print(c3.cache) 

    # 3. Encerramento
    leiloeiro.encerrar_leilao(ITEM_ID, compradores_list)

# # Se você quiser testar esta parte do código:
# # Certifique-se de que todas as classes base MOESI (RAM, Barramento, etc.) 
# # estejam definidas no mesmo escopo ou importadas.
if __name__ == "__main__":
     leilao_simulacao()