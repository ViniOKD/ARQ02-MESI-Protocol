from enum import Enum
# definição dos estados da MOESI
class Estado(Enum):
    MODIFIED = "M" # Dado sujo, exclusivo de uma cache. Responsabilidade de write-back
    OWNED = "O" # Dado sujo, compartilhado. Fornece dados para outros caches
    EXCLUSIVE = "E" # Dado limpo igual a MP, exclusivo.
    SHARED = "S" # Dado limpo (ou cópia de um Processador), compartilhado
    INVALID = "I" # Dado inválido/vazio








  