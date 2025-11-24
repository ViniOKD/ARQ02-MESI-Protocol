from enum import Enum
import random


#TODO: especificar o tipo do endereço nas funções (int, str...)

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
        self.tag = None # endereço do bloco na RAM
        self.dado = None # dado armazenado na linha de cache
        self.estado = Estado.INVALID # estado inicial é sempre inválido

    def __repr__ (self):
        """
        Representação em string da linha de cache
        Exemplo: [LINHA] Tag: 10 , Dado: 500 , Estado: EXCLUSIVE
        """
        dado_str = str(self.dado) if self.dado is not None else "Vazio"
        tag_str = str(self.dado) if self.tag is not None else "-"
        return f"[LINHA] Tag: {tag_str} , Dado: {dado_str} , Estado: {self.estado.value}]"
    


# classe da memória principal (RAM)
class RAM: 
    def __init__(self, tamanho = 50):
        """
        Inicializa a memória RAM com o tamanho especificado.
        Preenche os endereços de memória com valores aleatórios, entre 1 e 9999.
        """
        self.tamanho = tamanho
        # Preenchendo a memória com valores aleatórios, uma lista de inteiros
        self.memoria = [random.randint(1, 9999) for _ in range(tamanho)]
    

    def ler(self, endereco):
        """
        Retorna o valor armazenado no endereço especificado da memória RAM.
        Retorna None se o endereço for inválido.
        """

        if 0 <= endereco < self.tamanho:
            return self.memoria[endereco]
        else:
            print(f"Endereço {endereco} inválido na RAM.")
            return None
        
    def escrever(self, endereco, valor):
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
        self.ram = ram # conecta o barramento à MP
        self.caches: list = [] # lista de caches conectadas ao barramento
    
    def colocar_cache(self, cache):
        """ Conecta uma cache ao barramento """
        self.caches.append(cache)

    def log(self, msg):
        """ Função de log para o barramento """
        print(f"[Barramento] {msg}")

    def solicitar_leitura(self, endereco, id_requisitante):
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
        
    def solicitar_escrita(self, endereco, id_requisitante):
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





    





