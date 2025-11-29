"""
Sistema de leilão simples em Python.
Utilizando MOESI para controle de coerência de cache.
Feito por:
- Caio Garcia
- Carlos Eduardo Da Paixão Bravin
- Vinicius Taguchi Okada
"""
from leilao import Leilao
import logging
from datetime import datetime
import os

if not os.path.exists('logs'):
    os.makedirs('logs')

nome_arquivo = f"logs/simulacao_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log" # nome do arquivo do log gerado baseando-se no horario

logging.basicConfig(
    filename=nome_arquivo,  # nome do arquivo
    level=logging.INFO,         
    format="%(asctime)s - %(message)s", # formato das linhas do log
    datefmt="%H:%M:%S" # formato da data
)

def main():
    leilao = Leilao()
    leilao.interface()

if __name__ == "__main__":
    main()