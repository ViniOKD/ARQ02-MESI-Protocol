from moesi import Estado, LinhaCache, RAM, Barramento

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


