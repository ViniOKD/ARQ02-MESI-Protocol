from __future__ import annotations
from typing import TYPE_CHECKING
from ram import RAM
from colors import color
from moesi import Estado
import logging
# Permite que o editor entenda o que é o Cache sem importar
if TYPE_CHECKING:
    from cache import Cache

class Barramento():
    def __init__ (self, ram: RAM):
        """ Inicializa o barramento de dados """
        self.ram : RAM = ram # conecta o barramento à Memoria Principal
        self.caches : list[Cache] = [] # lista de caches conectadas ao barramento
    
    def log(self, msg: str) -> None:
        """ Função de log para o barramento """
        print(color(f"[Barramento] {msg}", "barramento"))
        logging.info(f"[Barramento] {msg}")

    def colocar_cache(self, cache : Cache):
        """ Conecta uma cache ao barramento """
        from cache import Cache
        if isinstance(cache, Cache):
            self.caches.append(cache)



    def solicitar_leitura(self, endereco : int, id_requisitante : int) -> tuple[int | None, Estado]:
        """
        Acontece quando uma ocorre uma READ MISS na cache, isto é, a cache requisitante não possui o dado.
        O barramento verifica se as outras caches possuem o dado
        """

        self.log(f'Processador {id_requisitante} pede LEITURA do endereço {endereco}.')

        dado_encontrado = None
        outra_cache_tem = False

        for cache in self.caches:
            if cache.id == id_requisitante:
                continue # pula a cache requisitante

            linha = cache.buscar_linha(endereco)

            # verificando se a linha existe e não está inválida
            if linha and linha.estado != Estado.INVALID:
                dado_encontrado = linha.dado
                outra_cache_tem = True # indica que outra cache possui o dado
                estado_anterior = linha.estado

                # Outra cache tinha o dado modificado exclusivo (M)
                if estado_anterior == Estado.MODIFIED:
                    # Agora ela é OWNED, pois vai compartilhar o dado e se responsabilizar pela sua atualização na RAM
                    linha.estado = Estado.OWNED
                    self.log(f'Cache {cache.id} (M->O): Forneceu dado modificado')

                # Outra cache tinha o dado limpo exclusivo (E)
                elif estado_anterior == Estado.EXCLUSIVE:
                    # Vai compartilhar o dado, então passa a ser SHARED
                    linha.estado = Estado.SHARED
                    self.log(f'Cache {cache.id} (E->S): Forneceu dado exclusivo limpo')

                # Outra cache tinha dado modificado compartilhado (O)
                elif estado_anterior == Estado.OWNED:
                    # Continua sendo OWNED, pois já estava compartilhado
                    self.log(f'Cache {cache.id} (O->O): Forneceu dado compartilhado modificado')
                
                # Outra cache tinha dado compartilhado (S)
                elif estado_anterior == Estado.SHARED:
                    # Continua sendo SHARED, pois já estava compartilhado
                    self.log(f'Cache {cache.id} (S->S): Forneceu dado compartilhado')

        if outra_cache_tem:
            return dado_encontrado, Estado.SHARED
        else:
            dado = self.ram.ler(endereco)
            self.log(f'Nenhuma outra cache possui o dado. Lido da RAM: {dado}')
            return dado, Estado.EXCLUSIVE
        
    def solicitar_escrita(self, endereco : int, id_requisitante : int) -> int | None:
        """
        Acontece quando ocorre uma WRITE MISS ou WRITE HIT em linha *SHARED* na cache requisitante.
        Dessa forma, garante que todas as outras caches invalidem suas cópias do dado.
        A cache requisitante ficará com o dado em estado *MODIFIED*.
        """

        self.log(f'Processador {id_requisitante} pede ESCRITA do endereço {endereco}.')

        dado_encontrado = None
        outra_cache_tem = False

        for cache in self.caches:
            if cache.id == id_requisitante:
                continue # pula a cache requisitante

            linha = cache.buscar_linha(endereco)

            if linha and linha.estado != Estado.INVALID:
                if linha.estado in [Estado.MODIFIED, Estado.OWNED]:
                    # Se outra cache tinha o dado modificado, ela precisa fornecer esse dado
                    # A RAM está desatualizada
                    dado_encontrado = linha.dado
                    outra_cache_tem = True
                    self.log(f'{cache.id} tinha dado modificado, forneceu {dado_encontrado}')

                linha.estado = Estado.INVALID
                self.log(f'{cache.id} (->I): Teve linha invalidada')

        if not outra_cache_tem:
            dado_encontrado = self.ram.ler(endereco)
            self.log(f'Nenhuma outra cache possuía o dado modificado. Lido da RAM: {dado_encontrado}')

        return dado_encontrado