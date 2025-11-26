from moesi import Estado, LinhaCache, RAM, Barramento, Cache, Processador
from leilao import Compradores

def teste1():
    linha = LinhaCache()
    print(f"Estado Inicial: {linha}") 
    linha.tag = 10
    linha.dado = 500
    linha.estado = Estado.EXCLUSIVE

    print(f"Após carga: {linha}")

    print("teste RAM")
    ram_sistema = RAM(tamanho=50)
    print(ram_sistema) 
    
    # Teste de leitura
    endereco_teste = 10
    valor_lido = ram_sistema.ler(endereco_teste)
    print(f"Leitura do Endereço {endereco_teste}: {valor_lido}")

    # Teste de escrita
    novo_valor = 777
    print(f"Escrevendo {novo_valor} no Endereço {endereco_teste}...")
    ram_sistema.escrever(endereco_teste, novo_valor)

    # Verifica se a escrita funcionou lendo novamente
    valor_pos_escrita = ram_sistema.ler(endereco_teste)
    print(f"Leitura pós-escrita no Endereço {endereco_teste}: {valor_pos_escrita}")

    # Visualizando a RAM novamente para ver o 777 lá
    print("\nEstado Final da RAM:")
    print(ram_sistema)


def teste2():
    r1 = RAM()
    bs = Barramento(r1)
    c1 = Cache(1, bs)
    c2 = Cache(2, bs)
    c3 = Cache(3, bs)
    bs.colocar_cache(c1)
    bs.colocar_cache(c2)
    bs.colocar_cache(c3)
    p1 = Compradores(1, c1, nome = "Comprador 1")
    p2 = Compradores(2, c2, nome = "Comprador 2")
    p3 = Compradores(3, c3, nome = "Comprador 3")

    print(r1)
    p1.load(10)
    p1.mostrar_cache()
    p2.load(10)
    #p2.mostrar_cache()
    #p2.store(10, 500)
    #p2.mostrar_cache()
    p1.store(10, 100)
    p2.store(10, 50)
    p2.load(10)
    p1.mostrar_cache()
    p2.mostrar_cache()




teste2()