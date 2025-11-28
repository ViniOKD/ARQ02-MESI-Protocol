from moesi import TAMANHO_RAM, Estado, LinhaCache, RAM, Barramento, Cache, Processador
from leilao import Comprador, Item, Leilao

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
    l1 = Leilao()
    l1.interface()

def teste3():
    bs = Barramento(RAM(10))
    c1 = Cache(1, bs)
    c2 = Cache(2, bs)
    p1 = Processador(1, c1)
    p2 = Processador(2, c2)

    p1.escrever(0, 10)
    p1.ler(0)
    p2.ler(0)


def teste4():
    print("\nSIMULAÇÃO MOESI\n")

    ram = RAM(TAMANHO_RAM)
    ram.escrever(10, 100) 
    print(f"Valor inicial RAM[10]: {ram.ler(10)}") # esperado : 100
    bus = Barramento(ram)
    p1 = Cache(1, bus)
    p2 = Cache(2, bus)
    p3 = Cache(3, bus)

    bus.colocar_cache(p1)
    bus.colocar_cache(p2)
    bus.colocar_cache(p3)

    # 1. P1 lê 10 (Miss -> E)
    p1.ler(10)
    
    # 2. P1 escreve 500 (Hit -> M)
    p1.escrever(10, 500)

    # 3. P2 lê 10 (Miss -> P1 fornece -> P1=O, P2=S)
    p2.ler(10)
    
    print("\nEstado Intermediário (P1=O, P2=S)")
    print(p1) 
    print(p2)

    # 4. P3 escreve 999 (Miss -> Invalida P1 e P2 -> P3=M)
    p3.escrever(10, 999)
    
    print("\nEstado Final")
    print(p1) # Esperado: Inválido (não deve aparecer ou estado I)
    print(p2) # Esperado: Inválido
    print(p3) # Esperado: MODIFIED, valor 999
    
    # 5. Verificação da RAM
    # A RAM deve ter 100. O valor 999 está sujo em P3. O valor 500 foi perdido (sobrescrito) ou descartado.
    print(f"\nValor na RAM[10]: {ram.ler(10)} (Esperado: 100 - desatualizado)")
    print(p3)


#teste3()
#teste2()

def leilao_linha():
    l1 = Leilao()
    bs = Barramento(RAM(50))
    l1.adicionar_comprador("nome")
    l1.adicionar_comprador("claudio")
    l1.adicionar_item("banana", 50)
    l1.adicionar_comprador("fernando en")
    l1.compradores[0].dar_lance(l1.itens[0], 100)
    l1.compradores[1].dar_lance(l1.itens[0], 120)
    l1.compradores[2].dar_lance(l1.itens[0], 130)
    l1.encerrar_item(l1.itens[0])


leilao_linha()