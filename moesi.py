from enum import Enum
import random

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
        Exemplo: [Tag: 10 | Dado: 500 | Estado: EXCLUSIVE]
        """
        dado_str = str(self.dado) if self.dado is not None else "Vazio"
        tag_str = str(self.dado) if self.tag is not None else "-"
        return f"[Tag: {tag_str} | Dado: {dado_str} | Estado: {self.estado.value}]"
    


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
        repr_str = "Memória RAM:\n"
        for endereco, valor in enumerate(self.memoria):
            repr_str += f"Endereço {endereco}: {valor}\n"
        return repr_str

