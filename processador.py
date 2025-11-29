from abc import ABC
from colors import color
from cache import Cache
import logging
class Processador(ABC):
    def __init__(self, id_processador: int, cache: Cache):
        """
        Inicializa um processador com seu ID e cache associada.
        """
        self.id: int = id_processador
        self.cache: Cache = cache
        
    
    def log(self, msg: str) -> None:
        """Registra uma mensagem no histórico do processador"""
        print(color(f"[Processador {self.id}] {msg}", "processador"))
        logging.info(f"[Processador {self.id}] {msg}")


    def ler(self, endereco: int) -> int | None:
        """
        Realiza uma operação de leitura (load) de um endereço.
        """
        self.log(f"Executando leitura do endereço {endereco}")
        dado = self.cache.ler(endereco)
        
        if dado is not None:
            self.log(f"Leitura concluída. Valor: {dado}")
        else:
            self.log(f"Leitura falhou para endereço {endereco}")
        
        return dado
    

    def escrever(self, endereco: int, valor: int) -> None:
        """
        Realiza uma operação de escrita (store) em um endereço.
        """
        self.log(f"Executando escrita no endereço {endereco} com valor {valor}")
        self.cache.escrever(endereco, valor)
        self.log(f"Escrita concluída")
    
    def mostrar_cache(self) -> None:
        """Exibe o estado atual da cache do processador"""
        print(f"\n{'='*50}")
        self.log(f"Estado da Cache") 
        print(f"{'='*50}")
        print(self.cache)

    def __repr__(self) -> str:
        """Representação em string do processador"""
        resultado = f"[Processador {self.id}] Cache: {len(self.cache.linhas)}/{self.cache.tamanho} linhas ocupadas"
        if self.cache.linhas:
            for linha in self.cache.linhas:
                resultado += f"\n  {linha}"
        else:
            resultado += "\n  Cache vazia."
        return resultado