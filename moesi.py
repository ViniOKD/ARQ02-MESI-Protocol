from __future__ import annotations # resolve o forward reference type hinting - causado por Barramento referenciar Cache antes dela ser declarada
from enum import Enum
import random
from collections import deque


TAMANHO_RAM = 50
TAMANHO_CACHE = 5
#TODO: VERIFICAR A UTILIZAÇAO DA FIFO IMPROVISADA NA CACHE
# POSSIVELMENTE ADICIONAR COLLECTIONS


# definição dos estados da MOESI
class Estado(Enum):
    MODIFIED = "M" # Dado sujo, exclusivo de uma cache. Responsabilidade de write-back
    OWNED = "O" # Dado sujo, compartilhado. Fornece dados para outros caches
    EXCLUSIVE = "E" # Dado limpo igual a MP, exclusivo.
    SHARED = "S" # Dado limpo (ou cópia de um Processador), compartilhado
    INVALID = "I" # Dado inválido/vazio


# estrutura de uma linha de cache
class LinhaCache:
    def __init__(self):
        """
        Inicializa uma linha de cache vazia, com estado inicial padrão inválido (*INVALID*)
        """
        self.tag : int | None = None # endereço do bloco na RAM
        self.dado : int | None = None # dado armazenado na linha de cache
        self.estado : Estado = Estado.INVALID # estado inicial é sempre inválido


    def __repr__ (self):
        """
        Representação em string da linha de cache
        Exemplo: [LINHA] Tag: 10 , Dado: 500 , Estado: EXCLUSIVE
        """
        dado_str = str(self.dado) if self.dado is not None else "Vazio"
        tag_str = str(self.tag) if self.tag is not None else "-"
        return f"[LINHA] Tag: {tag_str} | Dado: {dado_str} | Estado: {self.estado.value}"
    
# classe da memória principal (RAM)
class RAM: 
    def __init__(self, tamanho = TAMANHO_RAM):
        """
        Inicializa a memória RAM com o tamanho especificado.
        Preenche os endereços de memória com valores aleatórios, entre 1 e 9999.
        """
        self.tamanho : int = tamanho
        # Preenchendo a memória com valores aleatórios, uma lista de inteiros
        self.memoria  : list[int] = [random.randint(1, 9999) for _ in range(tamanho)]
    

    def ler(self, endereco : int) -> int | None:
        """
        Retorna o valor armazenado no endereço especificado da memória RAM.
        Retorna None se o endereço for inválido.
        """

        if 0 <= endereco < self.tamanho:
            return self.memoria[endereco]
        else:
            print(f"Endereço {endereco} inválido na RAM.")
            return None
        
    def escrever(self, endereco : int, valor : int ) -> None:
        """
        Escreve um valor no endereço especificado da memória RAM.
        Basicamente, funciona como uma atualização.
        """

        if 0 <= endereco < self.tamanho:
            self.memoria[endereco] = valor
        else:
            print(f"Endereço {endereco} inválido na RAM.")

    def __repr__(self):
        """
        Representação em string da memória RAM.
        Exibe os endereços e seus respectivos valores.
        """
        repr_str = "[RAM]\n"
        for endereco, valor in enumerate(self.memoria):
            repr_str += f"Endereço {endereco}: {valor}\n"
        return repr_str


# classe do barramento de dados
class Barramento():
    def __init__ (self, ram: RAM):
        """ Inicializa o barramento de dados """
        self.ram : RAM = ram # conecta o barramento à Memoria Principal
        self.caches : list[Cache] = [] # lista de caches conectadas ao barramento
    
    def colocar_cache(self, cache : Cache):
        """ Conecta uma cache ao barramento """
        self.caches.append(cache)

    def log(self, msg: str) -> None:
        """ Função de log para o barramento """
        print(f"[Barramento] {msg}")

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
                    self.log(f'{cache.id} (M->O): Forneceu dado modificado')

                # Outra cache tinha o dado limpo exclusivo (E)
                elif estado_anterior == Estado.EXCLUSIVE:
                    # Vai compartilhar o dado, então passa a ser SHARED
                    linha.estado = Estado.SHARED
                    self.log(f'{cache.id} (E->S): Forneceu dado exclusivo limpo')

                # Outra cache tinha dado modificado compartilhado (O)
                elif estado_anterior == Estado.OWNED:
                    # Continua sendo OWNED, pois já estava compartilhado
                    self.log(f'{cache.id} (O->O): Forneceu dado compartilhado modificado')
                
                # Outra cache tinha dado compartilhado (S)
                elif estado_anterior == Estado.SHARED:
                    # Continua sendo SHARED, pois já estava compartilhado
                    self.log(f'{cache.id} (S->S): Forneceu dado compartilhado')

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

# classe da cache
class Cache():
    def __init__ (self, id_cache : int, barramento : Barramento, tamanho : int = TAMANHO_CACHE):
        """
        Simula uma cache simples
        """

        self.id : int = id_cache
        self.barramento : Barramento = barramento
        self.tamanho : int = tamanho
        # será usado uma lista como fila. O final é o mais recente, o início é o mais antigo
        #self.linhas : list[LinhaCache] = []
        self.linhas : deque[LinhaCache] = deque() # nao limitar o tamanho com maxlen para controlar manualmente a remoção com write-back

    def buscar_linha(self, endereco : int) -> LinhaCache | None:
        """
        Busca uma linha de cache pelo endereço *tag*.
        Retorna a linha se encontrada, ou None se não existir.
        """

        for linha in self.linhas:
            if linha.tag == endereco:
                return linha
        return None
    
    # método protegido X
    # indica que é um método interno da classe -> metodo ""protegido"" seria com __
    def _logica_fifo(self):
        """
        Responsável por manter a política FIFO, isto é,
        remover o mais antigo (índice 0). Se for sujo (M ou O), escreve de volta na RAM, write-back.
        """

        if len(self.linhas) >= self.tamanho:    
            linha_removida = self.linhas.popleft() # remove a linha mais antiga
    
            if linha_removida.estado in [Estado.MODIFIED, Estado.OWNED]:
                # Write-back na RAM
                #print(f'[Cache {self.id}]: Write-back do endereço {linha_removida.tag} para RAM.')
                #self.barramento.ram.escrever(linha_removida.tag, linha_removida.dado)
                self.write_back(linha_removida.tag, linha_removida.dado)
    
    # Pra ficar mais legivel que self.barramento.ram.escrever...
    def write_back(self, tag : int , dado : int ) -> None:
        """
        Realiza o write-back de uma linha suja (M ou O) para a RAM.
        """
        print(f'[Cache {self.id}]: Write-back do endereço {tag} para RAM.')
        self.barramento.ram.escrever(tag, dado)


    def ler(self, endereco : int) -> int | None:
        """
        Realiza uma leitura na cache(load).
        """
        linha = self.buscar_linha(endereco)

        # Read hit
        if linha and linha.estado != Estado.INVALID:
            print(f'[Cache {self.id}]: READ HIT no endereço {endereco}. Dado: {linha.dado}. Estado: {linha.estado.value}')
            return linha.dado
        
        # Read miss
        print(f'[Cache {self.id}]: READ MISS no endereço {endereco}.')
        self._logica_fifo() # aplica a política FIFO

        dado, novo_estado = self.barramento.solicitar_leitura(endereco, self.id) # trocar esse self.barramento.solicitar_leitura por uma funcao pra melhorar leitura

        nova_linha = LinhaCache()
        nova_linha.tag = endereco
        nova_linha.dado = dado
        nova_linha.estado = novo_estado
        self.linhas.append(nova_linha)
        return dado
    
    def escrever(self, endereco : int, valor : int) -> None:
        """
        Realiza uma escrita na cache(store).
        """
        linha = self.buscar_linha(endereco)

        # Write hit
        if linha and linha.estado != Estado.INVALID:
            print(f'[Cache {self.id}]: WRITE HIT no endereço {endereco}.')

            if linha.estado == Estado.MODIFIED:
                # Já está em MODIFIED, nada a fazer
                pass

            elif linha.estado == Estado.EXCLUSIVE:
                linha.estado = Estado.MODIFIED

            elif linha.estado in [Estado.SHARED, Estado.OWNED]:
                # Necessário chamar o barramento para invalidar outras caches
                self.barramento.solicitar_escrita(endereco, self.id)
                linha.estado = Estado.MODIFIED
            
            linha.dado = valor
            return
        
        # Write miss
        print(f'[Cache {self.id}]: WRITE MISS no endereço {endereco}.')
        self._logica_fifo()

        # Solicita a propriedade da escrita
        # Garantir que outras caches invalidem suas cópias
        # _ Indica que o valor da função não será usado
        _ = self.barramento.solicitar_escrita(endereco, self.id) # Em cima acontece a mesma coisa só q nao tem o _ 🤔

        nova_linha = LinhaCache()
        nova_linha.tag = endereco
        nova_linha.dado = valor
        nova_linha.estado = Estado.MODIFIED
        self.linhas.append(nova_linha)

    def __repr__ (self):
        """
        Representação em string da cache
        """
        res = f"[Cache {self.id}, tamanho {self.tamanho}]\n"

        if not self.linhas:
            res += "  (vazia)\n"
        else:
            for linha in self.linhas:
                res += f" Estado: {linha.estado.value} | Tag: {linha.tag} | Dado: {linha.dado}\n"
        return res


# TESTE
def main() -> None:
    print("\nSIMULAÇÃO MOESI\n")

    ram = RAM(TAMANHO_RAM)
    ram.escrever(10, 100) 
    print(f"Valor inicial RAM[10]: {ram.ler(10)}") # esperado : 100
    bus = Barramento(ram)
    p1 = Cache(1, bus)
    p2 = Cache(2, bus)
    p3 = Cache(3, bus)

    bus.colocar_cache(p1)
    bus.colocar_cache(p2)
    bus.colocar_cache(p3)

    # 1. P1 lê 10 (Miss -> E)
    p1.ler(10)
    
    # 2. P1 escreve 500 (Hit -> M)
    p1.escrever(10, 500)

    # 3. P2 lê 10 (Miss -> P1 fornece -> P1=O, P2=S)
    p2.ler(10)
    
    print("\n--- Estado Intermediário (P1=O, P2=S) ---")
    print(p1) 
    print(p2)

    # 4. P3 escreve 999 (Miss -> Invalida P1 e P2 -> P3=M)
    p3.escrever(10, 999)
    
    print("\n--- Estado Final ---")
    print(p1) # Esperado: Inválido (não deve aparecer ou estado I)
    print(p2) # Esperado: Inválido
    print(p3) # Esperado: MODIFIED, valor 999
    
    # 5. Verificação da RAM
    # A RAM deve ter 100. O valor 999 está sujo em P3. O valor 500 foi perdido (sobrescrito) ou descartado.
    print(f"\nValor na RAM[10]: {ram.ler(10)} (Esperado: 100 - desatualizado)")
    print(p3)


if __name__ == "__main__":
    main()


    


  


