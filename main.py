"""
Sistema de leilão simples em Python.
Utilizando MOESI para controle de coerência de cache.
Feito por:
- Caio Garcia
- Carlos Eduardo Da Paixão Bravin
- Vinicius Taguchi Okada
"""
from leilao import Leilao


def main():
    leilao = Leilao()
    leilao.interface()

if __name__ == "__main__":
    main()