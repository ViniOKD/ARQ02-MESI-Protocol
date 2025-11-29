import random
from colors import color
import logging
TAMANHO_RAM = 50

class RAM: 
    def __init__(self, tamanho = TAMANHO_RAM):
        """
        Inicializa a memória RAM com o tamanho especificado.
        Preenche os endereços de memória com valores aleatórios, entre 1 e 9999.
        """
        self.tamanho : int = tamanho
        # Preenchendo a memória com valores aleatórios, uma lista de inteiros
        self.memoria  : list[int] = [random.randint(1, 9999) for _ in range(tamanho)]
    

    def log(self, msg: str) -> None:
        """ Função de log para a RAM """
        print(color(f"[RAM] {msg}", "ram"))
        logging.info(f"[RAM] {msg}")

    def ler(self, endereco : int) -> int | None:
        """
        Retorna o valor armazenado no endereço especificado da memória RAM.
        Retorna None se o endereço for inválido.
        """

        if 0 <= endereco < self.tamanho:
            return self.memoria[endereco]
        else:
            self.log(f"Endereço {endereco} inválido na RAM.")
            return None
        
            
    def escrever(self, endereco : int, valor : int ) -> None:
        """
        Escreve um valor no endereço especificado da memória RAM.
        Basicamente, funciona como uma atualização.
        """

        if 0 <= endereco < self.tamanho:
            self.memoria[endereco] = valor
        else:
            self.log(f"Endereço {endereco} inválido na RAM.")

    def __repr__(self):
        """
        Representação em string da memória RAM.
        Exibe os endereços e seus respectivos valores.
        """
        repr_str = "[RAM]\n"
        for endereco, valor in enumerate(self.memoria):
            repr_str += f"Endereço {endereco}: {valor}\n"
        return repr_str