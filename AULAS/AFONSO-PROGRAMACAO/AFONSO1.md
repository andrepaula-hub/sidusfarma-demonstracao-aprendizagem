06/08/2026, 10:38

2026-08-04-Afonso-01

Módulo 11 · Engenharia de Software · 3º ano · Aula 1

Spec-Driven
Development

Especificar antes de implementar: a especificação como fonte de verdade

Computação 2 · Prof. Afonso Brandão · 04/08/2026

📐  Especificação

✅  Critérios de aceite

🤖  IA orientada por spec

🔁  Spec → código

Agenda: 2 Horas de Spec-Driven Development

🎯  Bloco 1 (30min)

📋  Bloco 2 (35min)

Por quê SDD: problema, motivação,
conceitos-chave (SSoT, RF, RNF), qualidade
ISO 25010.

Anatomia do Spec: 6 seções (Visão, RF, RNF,
API, Schema, Testes). ADR: rastreabilidade
arquitetural. Pipeline de elicitação: 6
estágios.

📐  Bloco 3 (30min)

🤖  Bloco 4 (25min)

Modelagem como código: OpenAPI e
Gherkin; entidade-relacionamento, diagrama
de classes e diagrama de sequência em
Mermaid.

SDD e IA: verificação iterativa e
demonstração ao vivo sobre um sistema de
biblioteca.

🎯  Objetivo: Ao final da aula, você será capaz de escrever uma especificação executável com

anatomia clara, rastreada em ADRs, que guia desenvolvimento com testes e geração de código

assistida por IA.

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

1/16

Estrutura completa da aula06/08/2026, 10:38

2026-08-04-Afonso-01

1. Por Quê Spec-Driven Development?

❌  O Problema Comum

✅  A Solução: SDD

Iniciar a implementação sem definição formal

Spec-Driven Development é a metodologia

do comportamento esperado resulta em:

onde a especificação técnica é a única fonte

Retrabalho constante

Inconsistência de contratos de API

Desalinhamento com stakeholders

Testes incompletos

Dívida técnica acumulada

de verdade (Single Source of Truth —

SSoT):

Código deriva da spec

Testes verificam a spec

Documentação reflete a spec

IA gera dentro da spec

Conceitos-Chave: Single Source of Truth

Single Source of Truth (SSoT)

Princípio de arquitetura da informação: cada informação relevante reside em um único artefato
autoritário, do qual todas as demais representações são derivadas. Quando duas versões divergem,
a fonte única prevalece; as cópias devem ser reconciliadas com ela, jamais o inverso.

Requisito Funcional (RF)

Requisito Não Funcional (RNF)

O que o sistema deve fazer: funções e
comportamentos observáveis.

Como o sistema deve se comportar:
qualidade, desempenho, segurança.

Ex: "O sistema deve permitir registro de

usuário por nome e e-mail."

Ex: "Registro deve concluir em ≤2 segundos
sob carga nominal."

SDD vs. TDD

TDD (Test-Driven Development) escreve testes antes do código — fixa correção interna. SDD
descreve interfaces e contratos antes — fundamenta o TDD. SDD não substitui TDD, o TDD

implementa a verdade definida pela SDD.

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

2/16

O problema de começar a implementar antes de especificarA especificação como documento autoritário06/08/2026, 10:38

2026-08-04-Afonso-01

2. Qualidade Não Funcional: ISO 25010:2023

As 9 Características ISO 25010

Um modelo internacional que define qualidade de forma objetiva, impedindo que requisitos

permaneçam implícitos ou subjetivos:

📊  Desempenho

🔄  Compatibilidade

Tempo de resposta, uso de recursos,

Coexistência e interoperabilidade com outros

capacidade.

sistemas.

👤  Usabilidade

⚡  Confiabilidade

Apreensibilidade, operabilidade, proteção
contra erros.

Ausência de falhas, disponibilidade, tolerância
a falhas.

🔐  Segurança

🔧  Manutenibilidade

Confidencialidade, integridade, autenticidade.

Modularidade, testabilidade, modificabilidade.

📈  Flexibilidade

🛡  Segurança Operacional

Adaptabilidade, escalabilidade,
instalabilidade.

Fail-safe, alerta de perigo, recuperação.

✅  Funcionalidade

Correção, completude, propriedade das

funções.

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

3/16

9 características mensuráveis de qualidade de software06/08/2026, 10:38

2026-08-04-Afonso-01

3. Os Quatro Pilares de uma Especificação Madura

📡  Contrato de API

🗄  Schema de Dados

Rotas, métodos HTTP, códigos de status e

Tipos, chaves, índices e restrições de

payloads de requisição/resposta usando

integridade no banco de dados.

OpenAPI v3.

Exemplo: users.id PK, users.email UNIQUE

Exemplo: GET /usuarios/{id} retorna {nome,

NOT NULL.

email} ou 404.

✅  Regras e Cenários

📏  Metas de Qualidade

Critérios de aceite em linguagem

Critérios mensuráveis para cada

Gherkin/BDD (Dado/Quando/Então).

característica ISO 25010 aplicável.

Exemplo: "Dado saldo 100, Quando saque 30,
Então saldo=70."

Exemplo: "Latência ≤100ms p95,
complexidade ciclomática ≤5."

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

4/16

Componentes essenciais de toda especificação executável06/08/2026, 10:38

2026-08-04-Afonso-01

4. Anatomia de um Spec: Estrutura Completa

📋  Seção 1: Visão e Escopo

📐  Seção 2: Requisitos Funcionais

Por que o sistema existe, quem são os

Numerados (RF-001) para que testes e código

usuários, qual problema resolve e o que fica

possam citá-los. Descrição, pré e pós-

fora de escopo.

condições.

"Cotação que reduz a resposta de 24h para

"RF-001: cria cotação. Pré: autenticado. Pós:

<5min."

quoteId."

⚡  Seção 3: Requisitos Não Funcionais

🔄  Seção 4: Contrato de API

Numerados (RNF-001), cada um com métrica,

Rotas, métodos, parâmetros, payloads e

limite numérico e instrumento de verificação.

códigos de status em OpenAPI 3.1 — com

"RNF-001: p95 ≤100ms, medida no gateway."

caminho de erro.

POST /api/v1/quotes → 201 {quoteId, total} |
400

🗄  Seção 5: Modelo de Dados

✅  Seção 6: Cenários de Teste

Entidades, atributos, tipos, chaves e
restrições de integridade — sem citar produto.

Quote {id UUID PK, total Decimal NOT NULL}

Dado/Quando/Então, um por regra de
negócio. Cada cenário deve falhar antes da
implementação.

"Dado 12 unidades, Quando cotar, Então
desconto 5%."

5. ADR: Architecture Decision Record

O que é um ADR?

Documento que registra uma decisão arquitetural significativa, seu contexto, opções consideradas,

decisão tomada e justificativa. É independente de tecnologia — captura o "porquê" de

arquitetônico, não o "como" de implementação.

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

5/16

Seções obrigatórias e componentes de uma especificação maduraRastreabilidade de decisões arquiteturais antes de specs e código06/08/2026, 10:38

2026-08-04-Afonso-01

Seções do ADR

Exemplo Mínimo

Título: ADR-001: Usar padrão de fila para

ADR-001: Fila de Processamento

processamento assíncrono

Decision: Processamento assíncrono de

Status: Proposed | Accepted | Deprecated |

cotações via fila.

Superseded

Context: O problema arquitetural

Rationale: RF-002 exige latência <2s na

resposta. Cálculo de desconto é custoso. Fila

Decision: A escolha feita (sem tecnologia)

desacopla lógica de negócio.

Rationale: Por que essa sobre outras

Consequences: Trade-offs e impactos

Consequences: +1 componente (fila). RNF:
taxa de processamento ≥1000 msgs/min.

🎯  Por Que ADR Antes de Spec?

ADR → Spec → Implementação. ADR justifica estrutura e padrões que aparecem na spec. Sem ADR,
spec parece arbitrária; com ADR, rastreabilidade é clara. Exemplo: "Por que tem fila aqui? Consulte

ADR-001."

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

6/16

06/08/2026, 10:38

2026-08-04-Afonso-01

6. Documentação Técnica: Sequência Completa (Sem Tecnologia)

1️⃣  Problema

2️⃣  ADRs

Contexto de negócio, lacunas, restrições e
métricas de sucesso.

Decisões estruturais: padrões,
decomposição, limites de módulo.

Produto e stakeholders. Não é técnico: "o que

Arquitetura. Sem tecnologia: "como

não funciona e por quê".

estruturamos a solução?".

3️⃣  Especificação

4️⃣  Tecnologia (ADR-Tech)

RF, RNF, contrato de API, modelo de dados e

Linguagem, banco e framework, justificados

cenários de aceite.

contra a especificação.

Arquitetura e time. Ainda sem tecnologia:
"qual o comportamento esperado?".

Só aqui se escolhe produto. A spec não muda;
a tecnologia a implementa.

5️⃣  Plano de implementação

Classes, funções e fluxo, abstraídos da

sintaxe.

Time com apoio de IA: "quais módulos

realizam a spec?".

⚠  Invariante: Problema → ADR → Spec → Tecnologia → Implementação. Nunca pule etapas. Spec
não deve conter "use Node.js" ou "use PostgreSQL" — isso vai em ADR-Tech.

7. Pipeline de Elicitação: 6 Estágios

1️⃣  Modelagem de Processos (IDEF0): análise as-is — o que a organização faz, lacunas, atores e fluxos.

2️⃣  Modelagem Arquitetural (RM-ODP): casos de uso, entidades, diagramas de sequência, 5 viewpoints.

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

7/16

Problema → ADR → Spec: a jornada antes de códigoDa análise de negócio à implementação06/08/2026, 10:38

2026-08-04-Afonso-01

3️⃣  Esqueleto do Software: estrutura de diretórios, limites de módulo, Docker Compose, projeto vazio mas

estruturalmente completo.

4️⃣  Documentos de Especificação (Markdown/YAML): consolidação em formatos legíveis por máquina —

100% autoria humana, IA não participa.

5️⃣  Desenvolvimento Guiado por Testes (TDD): testes que falham inicialmente, consolidando contratos

comportamentais (pré-condições, pós-condições, invariantes).

6️⃣  Implementação: somente aqui — manualmente ou com IA — o código é gerado para fazer os testes

passarem e atender metas de qualidade não funcional.

8. OpenAPI (Swagger) e Gherkin/BDD

📡  OpenAPI v3

✅  Gherkin/BDD

Especificação padronizada legível por
máquina, expressa em YAML ou JSON.

Linguagem estruturada de cenários:
Dado/Quando/Então (Given/When/Then).

Descreve rotas, métodos HTTP, parâmetros,

Legível por humanos e interpretável por

schemas, códigos de status. Contrato
explícito entre produtor e consumidor da API.

ferramentas. Cada cenário = critério de aceite
verificável.

GET /usuarios/{id} → 200 {nome, email}

Dado saldo 100; Quando saque 30; Então

| 404

saldo=70.

RM-ODP e Viewpoints

Modelo ISO/IEC 10746 que descreve sistemas distribuídos em 5 pontos de vista complementares,
evitando mistura de intenção de negócio, modelo de dados e detalhe tecnológico: Enterprise

(propósito, papéis), Information (semântica, estrutura), Computational (decomposição funcional),
Engineering (distribuição), Technology (escolhas concretas).

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

8/16

Linguagens estruturadas para especificação executável06/08/2026, 10:38

2026-08-04-Afonso-01

9. Modelagem como Código (Modeling as Code)

Entende-se por modelagem como código a prática de descrever os modelos do sistema em notação
textual — Mermaid, PlantUML, Structurizr DSL — armazenada junto da especificação. O diagrama é

derivado do texto por ferramenta; a fonte de verdade é o texto.

Por que texto

Três modelos obrigatórios

Revisável por diff e sujeito a aprovação em

pull request.

Versionado com o código que descreve.

Divergência entre modelo e implementação

torna-se visível.

Dados: entidade-relacionamento
( erDiagram ).
Estático: classes ( classDiagram ).
Dinâmico: sequência ( sequenceDiagram ).

Posição na especificação

O modelo de dados fundamenta o schema.

O modelo estático delimita

responsabilidades.

O modelo dinâmico define a ordem das

interações e os caminhos de erro.

Exemplo conduzido nos próximos slides: sistema de biblioteca — três entidades persistidas e cinco

classes de domínio.

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

9/16

O modelo é texto versionado no repositório, não imagem anexada06/08/2026, 10:38

2026-08-04-Afonso-01

10. Modelagem de Dados: Entidade-Relacionamento

// modelos/dados.mmd
erDiagram
  LIVRO  ||--o{ EMPRESTIMO : origina
  LEITOR ||--o{ EMPRESTIMO : realiza
  LIVRO {
    uuid id PK
    text isbn UK
    text titulo
    int  exemplares
  }
  LEITOR {
    uuid id PK
    text email UK
    bool ativo
  }
  EMPRESTIMO {
    uuid id PK
    uuid livro_id FK
    uuid leitor_id FK
    date prevista
    date efetiva
  }

LIVRO

uuid

id

text

isbn

text

titulo

int

exemplares

PK

UK

LEITOR

uuid

id

PK

text

email

UK

bool

ativo

origina

realiza

EMPRESTIMO

uuid

id

uuid

livro_id

uuid

leitor_id

date

prevista

date

efetiva

PK

FK

FK

A cardinalidade  ||--o{  fixa a regra: um livro
origina zero ou muitos empréstimos.
efetiva  nula identifica empréstimo em
aberto — decisão que deve constar da

especificação, não do código.

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

10/16

Biblioteca — três entidades persistidas, com chaves e cardinalidades explícitas06/08/2026, 10:38

2026-08-04-Afonso-01

11. Modelagem Estática: Diagrama de Classes

// modelos/estatico.mmd
classDiagram
  class Livro {
    +UUID id
    +String isbn
    +int exemplares
    +disponivel() bool
  }
  class Leitor {
    +UUID id
    +bool ativo
  }
  class Emprestimo {
    +Date prevista
    +Date efetiva
    +emAtraso(hoje) bool
  }
  class PoliticaEmprestimo {
    +int prazoDias
    +int limitePorLeitor
    +validar(leitor, livro)
  }
  class ServicoEmprestimo {
    +registrar(leitor, livro)
    +devolver(emprestimo)
  }
  ServicoEmprestimo --> PoliticaEmprestimo
  ServicoEmprestimo --> Emprestimo
  Emprestimo --> Livro
  Emprestimo --> Leitor

Livro

+UUID id

+String isbn

+int exemplares

+disponivel() : bool

Leitor

+UUID id

+bool ativo

Emprestimo

+Date prevista

+Date efetiva

ServicoEmprestimo

+emAtraso(hoje) : bool

+registrar(leitor, livro)

+devolver(emprestimo)

PoliticaEmprestimo

+int prazoDias

+int limitePorLeitor

+validar(leitor, livro)

Três classes correspondem às entidades

persistidas; duas existem apenas em memória.
PoliticaEmprestimo  isola as regras de prazo
e limite, que mudam por decisão institucional e

não por alteração de esquema.

12. Modelagem Dinâmica: Diagrama de Sequência

// modelos/dinamico.mmd
sequenceDiagram
  actor A as Atendente
  participant API as POST /emprestimos
  participant S as ServicoEmprestimo
  participant P as PoliticaEmprestimo
  participant R as Repositorio
  A->>API: leitor_id, livro_id
  API->>S: registrar(leitor, livro)
  S->>P: validar(leitor, livro)
  alt limite excedido ou sem exemplar
    P-->>S: recusa(motivo)
    S-->>API: 422 motivo
  else apto
    P-->>S: aprovado(prazo 14d)
    S->>R: salvar(emprestimo)
    R-->>S: emprestimo
    S-->>API: 201 emprestimo
  end

POST /emprestimos

ServicoEmprestimo

PoliticaEmprestimo

Repositorio

Atendente

leitor_id, livro_id

registrar(leitor, livro)

alt

[limite excedido ou sem exemplar]

validar(leitor, livro)

422 motivo

recusa(motivo)

[apto]

aprovado(prazo 14d)

salvar(emprestimo)

emprestimo

201 emprestimo

O bloco  alt  torna o caminho de recusa parte
do modelo. Cada ramo corresponde a um

cenário Gherkin e a um código de status no
contrato OpenAPI.

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

11/16

Cinco classes de domínio — estrutura, responsabilidades e dependênciasRegistro de empréstimo — ordem das interações e caminho de erro06/08/2026, 10:38

2026-08-04-Afonso-01

13. Spec-Driven Development e IA

💡  Três Papéis da Especificação Diante de Modelos Generativos

A IA gera código sintaticamente correto com facilidade, mas sem alinhamento com requisitos não

funcionais quando a instrução é vaga. Uma spec bem estruturada:

🚪  Restringe

📚  Codifica

Limita o espaço de soluções possíveis,

Encapsula conhecimento de domínio que o

evitando decisões arquiteturais improvisadas.

modelo não possui internamente.

✅  Verifica

Define metas de qualidade verificáveis após

geração.

Comportamentos que o Modelo Não Infere

Processamento de Eventos Complexos (CEP): análise de fluxos contínuos que correlacionam

múltiplos eventos ao longo do tempo (sequências, ausência de eventos, agregações em janelas).

Exemplo: alerta após 3 falhas de autenticação em <1 minuto. Essas janelas e ordens devem ser

definidas explicitamente na especificação.

14. Verificação e Refinamento Iterativo

Característica

Estratégia de Verificação

📊  Desempenho

Perfilamento (profiling) de tempo e recursos

⚡  Confiabilidade

Injeção de falhas, teste de fallback

🔐  Segurança

Análise estática, auditoria de código

🔧  Manutenibilidade

Complexidade ciclomática, taxa de duplicação

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

12/16

Como a especificação restringe, codifica e verifica geração de códigoComo validar que o código atende a especificação06/08/2026, 10:38

2026-08-04-Afonso-01

Ciclo de Verificação: código é gerado → verificado contra metas → desvios → relatório retorna à IA

com spec original + instrução de correção → regeneração → reverificação até que todas as metas
sejam atendidas (máx. N iterações).

⚠  Importante: Verificação não é uma etapa opcional de revisão manual — é parte integrante do
método. Sem verificação, a especificação permanece uma intenção não confirmada.

📋  Ficha Técnica: Spec-Driven Development

Definição

Quando Usar

Metodologia na qual a especificação técnica é
a única fonte de verdade (SSoT),

Sempre que há múltiplos stakeholders,
requisitos não funcionais críticos ou

fundamentando código, testes,

documentação e geração por IA.

envolvimento de IA na geração de código.

Os 4 Pilares

Artefatos Principais

1. Contrato de API (OpenAPI)

2. Schema de Dados

3. Regras e Cenários (Gherkin)

Documento Markdown estruturado, ADR,

especificação OpenAPI v3, cenários Gherkin,

modelos em Mermaid (dados, classes,

4. Metas de Qualidade (ISO 25010)

sequência), testes automatizados.

Sequência Inviolável (Pipeline 6 Estágios)

1. Processos (IDEF0) → 2. Arquitetura (RM-ODP) → 3. Esqueleto → 4. Spec (100% humana) → 5. TDD

→ 6. Implementação (IA-assistida)

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

13/16

Resumo executivo — o que levar para o projeto06/08/2026, 10:38

2026-08-04-Afonso-01

📐  Demonstração ao Vivo

Transcrição (trecho)

Indefinições a resolver antes de

Cliente: Hoje anotamos em caderno quem

levou o quê. Some livro, e ninguém sabe com

codificar

Prazo fixo ou variável por perfil de leitor — e

quem está. Queria um sistema para cadastrar

quem define o perfil.

o acervo e controlar os empréstimos.

Renovação e reserva: existem no escopo?

Analista: Por quantos dias o livro fica com o

Qual precedência entre elas?

leitor?

Cliente: Duas semanas, acho. Mas para

professor podia ser mais, né?

Analista: Existe renovação ou reserva?

Cliente: Isso eu não tinha pensado. Renovar

acho que sim, se ninguém estiver esperando.

Analista: E quando o leitor atrasa?

Cliente: Multa não dá, a biblioteca é

comunitária. Talvez bloquear até devolver. Ah,

e tem título com dois ou três exemplares
iguais. E precisa ser rápido, o computador da

recepção é antigo.

Consequência do atraso: bloqueio de quê,

por quanto tempo, com qual reversão.

Limite de empréstimos simultâneos por

leitor.

Título e exemplar são a mesma entidade? O

empréstimo recai sobre qual deles?

"Rápido" sem métrica, limite nem

instrumento não constitui requisito.

O que será produzido em aula

ADR da decisão estrutural, especificação com

RF e RNF mensuráveis, os três modelos em
Mermaid — três entidades e cinco classes —,

contrato OpenAPI, cenários Gherkin e

verificação do código gerado.

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

14/16

Entrevista com o cliente — plataforma de acervo e empréstimos de uma biblioteca comunitária06/08/2026, 10:38

2026-08-04-Afonso-01

📐

Spec-Driven Development

Especificação é contrato. Código é promessa. Testes são prova. IA é executor.

A disciplina de escrever especificações antes de qualquer linha de código não é overhead — é o

fundamento que transforma ambiguidade em clareza, e ambição em entrega.

Próximas aulas: Modelagem de Dados · Arquitetura de Software · Testing em Escala

Módulo 11 · Engenharia de Software · Aula 1 · Computação 2 · Prof. Afonso Brandão

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

15/16

06/08/2026, 10:38

2026-08-04-Afonso-01

Sobre este encontro

Spec-Driven Development · 04/08/2026 · Prof. Afonso

OBJETIVO DE APRENDIZAGEM

Ao final do encontro, o estudante deve ser capaz de escrever uma especificação executável com

anatomia clara, rastreada em ADRs, que orienta a implementação, os testes e a geração de código
assistida por modelos generativos.

ESTRATÉGIA DO ENCONTRO

Exposição em quatro blocos com construção incremental de uma especificação de referência; o

encerramento é uma demonstração conduzida pelo professor sobre um sistema de biblioteca, e a
aplicação ao projeto do grupo ocorre após a aula, conforme roteiro do material.

ESTRUTURA DO ENCONTRO

1. Bloco 1 (30 min) — Por que SDD: problema, motivação, SSoT, requisito funcional e não funcional,

qualidade ISO/IEC 25010

2. Bloco 2 (35 min) — Anatomia da especificação: seis seções, ADR e rastreabilidade, pipeline de

elicitação

3. Bloco 3 (30 min) — Modelagem como código: OpenAPI e Gherkin; entidade-relacionamento,

classes e sequência em Mermaid

4. Bloco 4 (25 min) — Especificação e IA: verificação iterativa e demonstração ao vivo

https://afonsolelis.github.io/aulas/pages/module-11-eng-software/slides/slide-lesson-1.html

16/16


