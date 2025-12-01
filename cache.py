from __future__ import annotations
from collections import deque
from moesi import Estado
from barramento import Barramento
from colors import color
from linha import LinhaCache
import logging
TAMANHO_CACHE = 5


class Cache():
    def __init__ (self, id_cache : int, barramento : Barramento, tamanho : int = TAMANHO_CACHE):
        """ Inicializa uma cache com o barramento, id, tamanho e suas linhas. """
        self.id : int = id_cache
        self.barramento : Barramento = barramento
        self.tamanho : int = tamanho
        self.linhas : deque[LinhaCache] = deque()

    def log(self, msg: str) -> None:
        """ Função de log para o barramento """
        print(color(f"[Cache {self.id}] {msg}", "cache"))
        logging.info(f"[Cache {self.id}] {msg}")


    def buscar_linha(self, endereco : int) -> LinhaCache | None:
        """
        Busca uma linha de cache pelo endereço *tag*.
        Retorna a linha se encontrada, ou None se não existir.
        """
        for linha in self.linhas:
            if linha.tag == endereco:
                return linha
        return None
    
    def _logica_fifo(self):
        """
        Responsável por manter a política FIFO, isto é, remover o mais antigo. 
        Se for sujo (M ou O), escreve de volta na RAM, write-back.
        """

        
        if len(self.linhas) >= self.tamanho:    
            linha_removida = self.linhas.popleft() # remove a linha mais antiga
    
            if linha_removida.estado in [Estado.MODIFIED, Estado.OWNED]:
                # Write-back na RAM
                self.write_back(linha_removida.tag, linha_removida.dado)
    
    def write_back(self, tag : int , dado : int ) -> None:
        """ Realiza o write-back de uma linha suja (M ou O) para a RAM. """
        self.log(f"Write-back do endereço {tag} para RAM.")
        self.barramento.ram.escrever(tag, dado)


    def ler(self, endereco : int) -> int | None:
        """ 
        Le (load) um valor armazenado em um *endereco* especifico na cache. 
        Retorna o valor se encontrado, ou None se não existir. 
        """
        linha = self.buscar_linha(endereco)

        # Read hit
        if linha and linha.estado != Estado.INVALID:
            print(f'[Cache {self.id}]: READ HIT no endereço {endereco}. Dado: {linha.dado}. Estado: {linha.estado.value}')
            return linha.dado
        
        # Read miss
        self.log(f'READ MISS no endereço {endereco}.')
        self._logica_fifo() # aplica a política FIFO

        dado, novo_estado = self.barramento.solicitar_leitura(endereco, self.id)

        if linha: 
            # Atualiza a linha existente
            linha.dado = dado
            linha.estado = novo_estado
            return dado
        else:
            # Cria uma nova linha
            nova_linha = LinhaCache()
            nova_linha.tag = endereco
            nova_linha.dado = dado
            nova_linha.estado = novo_estado
            self.linhas.append(nova_linha)
            return dado
    
    def escrever(self, endereco : int, valor : int) :
        """
        Realiza uma escrita na cache (store).
        """
        
        linha = self.buscar_linha(endereco)

        # Write hit
        if linha and linha.estado != Estado.INVALID:
            self.log(f"WRITE HIT no endereço {endereco}.")

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
            return linha # Retorna a linha atualizada
        
        # Write miss
        self.log(f"WRITE MISS no endereço {endereco}.")
        self._logica_fifo()

        # Solicita a propriedade da escrita
        # Garantir que outras caches invalidem suas cópias
        self.barramento.solicitar_escrita(endereco, self.id)

        if linha:
            # Atualiza a linha existente
            linha.dado = valor
            linha.estado = Estado.MODIFIED
            return linha
        else:
            # Cria uma nova linha
            nova_linha = LinhaCache()
            nova_linha.tag = endereco
            nova_linha.dado = valor
            nova_linha.estado = Estado.MODIFIED
            self.linhas.append(nova_linha)
            return nova_linha

    def __repr__ (self):
        """
        Representação em string da cache
        """
        res = f"[Cache {self.id}, tamanho {self.tamanho}]\n"

        if not self.linhas:
            res += "Vazia\n"
        else:
            for linha in self.linhas:
                res += f" Estado: {linha.estado.value} | Tag: {linha.tag} | Dado: {linha.dado}\n"
        return res