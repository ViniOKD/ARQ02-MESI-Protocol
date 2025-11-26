# SIMULADOR DE MOESI E IMPLEMENTAÇÃO DE LEILÃO

# MOESI SIMULATOR + AUCTION HOUSE IMPLEMENTATION

# PT-BR

## Objetivo

Este projeto tem como objetivo implementar um simulador de memória cache utilizando uma extensão do protocolo MESI (Modify, Exclusive, Shared, Invalid), como MESIF ou MOESI, integrado a uma **aplicação prática** que demonstra seu funcionamento em um cenário real.

## Descrição

Este projeto consiste em uma simulação do protocolo de coerência de cache **MOESI**, aplicada em um contexto prático baseado em um **sistema de leilões**.

A ideia central é representar cada participante do leilão (leiloeiro e compradores) como **processadores**, enquanto cada item em disputa é tratado como uma **linha de cache**.  
Dessa forma, cada ação realizada — como propor um lance, atualizar um valor ou consultar o estado atual do leilão — é convertida internamente em operações de leitura, escrita ou invalidação na cache simulada.

A implementação busca demonstrar:

- como os estados do protocolo MOESI se comportam em cenários de concorrência;
- como diferentes processadores interagem ao disputar acesso ao mesmo dado;
- como o estado **OWNED** pode ser aplicado de maneira intuitiva em um ambiente onde um participante “detém” temporariamente a informação mais atualizada (maior lance).

Este simulador tem finalidade educacional, servindo como apoio aos estudos de Arquitetura de Computadores, Coerência de Cache e Sistemas Distribuídos aplicados.

## Protocolo MOESI

O protocolo **MOESI** foi escolhido devido às características necessárias para a aplicação proposta.  
O estado **OWNED (O)** é especialmente relevante, pois permite que um processador mantenha dados compartilhados, porém modificados, sem precisar escrevê-los imediatamente na memória principal.

Essa característica se encaixa diretamente no contexto de um sistema de leilões, onde um comprador pode “possuir” temporariamente a informação de maior lance.

## Sistema de Leilão

A aplicação prática deste projeto é um **sistema de leilões**, onde o leiloeiro e os compradores se comportam como _Processadores_.  
Cada lance é mapeado para uma operação na _Cache_, e o comprador que oferece o maior valor passa a deter a linha correspondente ao item em estado **OWNED**, representando que ele possui os dados atualizados antes dos demais processadores.

## Arquitetura do Projeto

**sujeito a mudanças até a finalizacao do projeto**

A arquitetura do sistema foi organizada para permitir uma separação clara entre:

1. **Simulação da Cache**
2. **Regras do Protocolo MOESI**
3. **Aplicação Real (Sistema de Leilão)**

A seguir, uma visão geral dos principais componentes:

### 1. Processo (Processador)

Cada comprador ou leiloeiro é representado como uma instância da classe **Processador**, responsável por:

- realizar operações de leitura e escrita na cache;
- solicitar atualizações de estado conforme o protocolo;
- interagir com outros processadores quando necessário.

O leiloeiro pode agir como coordenador, enquanto cada comprador é um processador independente.

---

### 2. Cache

Cada processador possui sua própria **cache local**, organizada em linhas que representam os itens do leilão.

Cada linha pode assumir um dos estados:

- **M — Modified**
- **O — Owned**
- **E — Exclusive**
- **S — Shared**
- **I — Invalid**

A lógica interna controla transições entre estados conforme o MOESI define.

---

### 3. Controlador de Coerência (MOESI)

Implementa toda a lógica do protocolo, incluindo:

- transições de estado entre processadores;
- propagação de dados modificados;
- invalidação de linhas quando necessário;
- garantia de que apenas um processador pode estar em estado _Modified_ ou _Owned_.

Toda a inteligência do protocolo fica concentrada aqui, deixando o simulador extensível.

---

### 4. Módulo de Leilão

Conecta o simulador ao problema real.  
Ele é responsável por:

- criar itens para leilão (linhas da cache);
- registrar participantes;
- receber lances;
- traduzir ações do leilão em operações de cache (read/write);
- aplicar regras de disputa.

O participante com o maior lance mantém a linha do item em estado **Owned**, indicando que ele possui a informação mais atualizada até que outro participante tente superá-lo.

---

### 5. Fluxo Geral de Execução

Participante → Faz Lance → Operação de Escrita na Cache
↓
Protocolo MOESI → Atualiza Estado do Item
↓
Cache dos Outros Processadores → Invalidação / Compartilhamento
↓
Leilão → Atualiza o "dono" do maior lance
Esse ciclo se repete até que o item seja arrematado ou o leilão seja finalizado.

---

### 6. Testes e Cenários

O projeto inclui:

- cenários de corrida de lances (concorrência);
- vários compradores disputando o mesmo item;
- leitura de valor atual por outros processadores;
- transições completas do MOESI em tempo real.

Esses testes ajudam a visualizar e validar o comportamento do protocolo.
