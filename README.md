# Simulador MOESI - Implementação de Leilão

- Universidade Estadual de Maringá
- Disciplina: Arquitetura e organização de computadores II
- Curso: Ciência da Computação
- Professora: Sandra Cossul
---

Simulador do protocolo de coerência de cache **MOESI**, demonstrando seu funcionamento prático através de um **sistema de leilões**.

---

# Autores
* **Vinicius Taguchi Okada** 
* **Carlos Eduardo da Paixão Bravin** 
* **Caio Garcia** 


## Visão Geral
Nesta simulação, tratamos **participantes do leilão como processadores**. A concorrência de lances ilustra transições de estado complexas, com foco no estado **OWNED**, onde um comprador detém a versão mais recente do dado (o maior lance) antes da gravação na memória principal.

## Estrutura do Projeto
* **Processador:** Entidade que realiza lances (Writes) e consultas (Reads).
* **Cache:** Gerencia os estados locais (M, O, E, S, I).
* **Controlador:** Implementa a lógica estrita do protocolo MOESI.
* **Leilão:** Camada de aplicação que orquestra os itens e participantes.

## Fluxo
`Lance (Write)` → `Atualização MOESI (Owned/Modified)` → `Propagação/Invalidação` → `Novo Estado Global`


## Como executar

No terminal, execute:
```bash
python main.py
```
Ou, para criar um executavel
Instale a dependência pyinstaller:
```bash
pip install pyinstaller
```
Após isso, no terminal execute:
```bash
pyinstaller --onefile main.py
```
O arquivo .exe estará localizado na pasta dist



