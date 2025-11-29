# Simulador MOESI - Implementação de Leilão

Simulador do protocolo de coerência de cache **MOESI**, demonstrando seu funcionamento prático através de um **sistema de leilões**.

## Visão Geral
Nesta simulação, tratamos **participantes do leilão como processadores** e **itens como linhas de cache**. A concorrência de lances ilustra transições de estado complexas, com foco no estado **OWNED**, onde um comprador detém a versão mais recente do dado (o maior lance) antes da gravação na memória principal.

## Estrutura do Projeto
* **Processador:** Entidade que realiza lances (Writes) e consultas (Reads).
* **Cache:** Gerencia os estados locais (M, O, E, S, I).
* **Controlador:** Implementa a lógica estrita do protocolo MOESI.
* **Leilão:** Camada de aplicação que orquestra os itens e participantes.

## Fluxo
`Lance (Write)` → `Atualização MOESI (Owned/Modified)` → `Propagação/Invalidação` → `Novo Estado Global`
