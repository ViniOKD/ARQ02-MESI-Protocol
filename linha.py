from moesi import Estado

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
        Exemplo: [LINHA] Tag: 10 , Dado: 500 , Estado: E
        """
        dado_str = str(self.dado) if self.dado is not None else "Vazio"
        tag_str = str(self.tag) if self.tag is not None else "-"
        return f"[LINHA] Tag: {tag_str} | Dado: {dado_str} | Estado: {self.estado.value}"