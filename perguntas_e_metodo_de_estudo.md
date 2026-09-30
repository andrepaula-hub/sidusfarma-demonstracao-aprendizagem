# Perguntas da Demonstração de Aprendizagem

Este arquivo reúne as perguntas identificadas nas Sprints 1, 2 e 3. Os enunciados abaixo foram preservados como perguntas brutas, sem correção gramatical, padronização de termos ou tratamento do texto.

## Sprint 1 — perguntas brutas

### S1.01

"No projeto de vocês, como uma necessidade do negócio se transforma em uma estrutura de dados capaz de apoiar uma decisão? Explique esse caminho, partindo dos objetivos e processos do parceiro e das tarefas que os usuários precisam realizar, até chegar às visualizações analíticas e à modelagem conceitual do Data Warehouse. Pode explorar: como objetivos e processos do negócio se transformam em perguntas e Jobs to be Done; como estes orientam as visualizações e a definição de fatos, medidas, dimensões e granularidade do Data Warehouse; e quais problemas surgem quando negócio, usuários, visualizações e modelo de dados não estão alinhados."

### S1.02

"No projeto de vocês, o que do contexto do parceiro precisou ser traduzido para dentro do modelo de dados, para que a solução conseguisse responder às perguntas dele? Pode explorar: que decisão o parceiro precisa tomar e que informação ela exige; o que precisava existir na base para sustentar essa informação; que parte do processo dele virou dado e que parte não virou; o que ficou fora do modelo por não estar nos dados disponíveis. Se você não souber algum detalhe, explique como descobriria, por exemplo lendo a documentação, olhando os dados ou perguntando ao time."

### S1.03

"Explique uma decisão importante que o grupo tomou ao separar os quatro cubos e definir as dimensões compartilhadas entre eles, qual foi o seu papel nela, e por que foi por esse caminho. Pode explorar: o critério que separou um cubo de outro; o que se ganha ao compartilhar uma dimensão entre cubos e o que isso obriga; o que aconteceria se a mesma dimensão tivesse significados diferentes em dois cubos; o que mudaria se fosse preciso um quinto cubo."

### S1.04

"No projeto de vocês, por que não consultar direto as tabelas originais do parceiro, em vez de reorganizá-las em cubos? Pode explorar: o que a estrutura original serve bem e o que ela serve mal; que pergunta fica cara ou impossível na tabela original; o que a reorganização custa em trabalho e manutenção; quando não valeria a pena reorganizar. Se você não souber algum detalhe, explique como descobriria, por exemplo lendo a documentação, olhando os dados ou perguntando ao time."

### S1.05

"Explique uma decisão importante que o grupo tomou ao definir a política de qualidade e a classificação dos dados, qual foi o seu papel nela, e o que essa decisão impõe à solução analítica. Pode explorar: o critério que classificou um dado como sensível ou protegido; o que a política de qualidade obriga a verificar antes do uso; para que serve o catálogo de metadados na prática; o que aconteceria com a solução se um dado necessário fosse classificado como de acesso restrito."

### S1.06

"No projeto de vocês, como se decide quantos cubos analíticos existem e o que cada um deles cobre? Pode explorar: o critério que separa um cubo de outro; o que ganha e o que se perde ao dividir mais; como se verifica que as perguntas do parceiro ficam todas cobertas. Se você não souber algum detalhe, explique como descobriria, por exemplo lendo a documentação, olhando os dados ou perguntando ao time."

### S1.07

"Explique uma decisão importante que o grupo tomou ao definir a granularidade de um indicador, qual foi o seu papel nela, e o que essa escolha muda na leitura do resultado. Pode explorar: o que muda quando o mesmo indicador é lido por outro nível de agregação; o critério que definiu o nível adotado; que conclusão errada surgiria com a granularidade trocada; o que aconteceria se o parceiro pedisse o mesmo número num nível mais detalhado."

### S1.08

"No projeto de vocês, o que a granularidade escolhida para um cubo determina sobre as perguntas que ele consegue responder? Pode explorar: o que significa o grão de um cubo; que pergunta deixa de ser respondível quando o grão é grosso demais; o que custa manter um grão muito fino; como se escolhe esse nível. Se você não souber algum detalhe, explique como descobriria, por exemplo lendo a documentação, olhando os dados ou perguntando ao time."

### S1.09

"Explique uma decisão importante que o grupo tomou ao definir os requisitos não funcionais pela ISO 25010, qual foi o seu papel nela, e o que o diagnóstico das bases mudou nesses requisitos. Pode explorar: o que se ganha ao ancorar os requisitos numa norma; o que torna um requisito não funcional verificável; como os dados ausentes e duplicados que você diagnosticou afetaram o requisito de qualidade; o que aconteceria se o parceiro entregasse uma base pior do que a esperada."

### S1.10

"Explique uma decisão importante que o grupo tomou ao transformar as perguntas de negócio do parceiro em indicadores mensuráveis, qual foi o seu papel nela, e por que foi por esse caminho. Pode explorar: o critério que fez uma pergunta virar um indicador e outra não; o que um indicador captura e o que ele deixa escapar; como o Canvas dimensional sustenta esses indicadores; o que aconteceria se o indicador melhorasse mas o parceiro continuasse insatisfeito."

## Sprint 2 — perguntas brutas

### S2.01

"Descreva o caminho do dado no seu projeto, da origem até virar resposta para quem pergunta. Diga qual é o ponto de controle mais importante desse caminho e por que ele está ali. Pode explorar: o que cada etapa resolve, o que passa em cada ponto de controle, o que quebra se ele sair do lugar."

### S2.02

"O seu grupo definiu atributos de qualidade e como medi-los nas bases reais. Explique o que a medição precisa ter para servir de evidência e o que acontece quando a métrica não pode ser aplicada na base que veio do parceiro. Se não souber algum detalhe, explique como descobriria. Pode explorar: procedimento repetível, base incompleta, exceção registrada."

### S2.03

"O seu grupo definiu finalidade, hipótese legal e o atendimento dos direitos do titular. Explique por que a finalidade precisa ser declarada antes da coleta e o que acontece quando o dado passa a ser usado para outra coisa. Pode explorar: consentimento, uso secundário, direito do titular."

### S2.04

"O modelo de dados do seu projeto guarda coisas que mudam com o tempo. Explique o que precisa acontecer para uma mudança não reescrever o passado e o que se ganha guardando essa história. Se não souber algum detalhe, explique como descobriria. Pode explorar: sobrescrever, vigência, comparação entre períodos."

### S2.05

"O seu grupo traduziu critérios de sucesso em expectativas e desenhou o fluxo do perfil operacional. Explique o que se ganha traduzindo critério em expectativa antes de desenhar e o que acontece quando o desenho vem primeiro. Pode explorar: o que observar, passo sem propósito, retrabalho de desenho."

### S2.06

"O fluxo do seu grupo seleciona momentos críticos por perfil, com critérios de seleção declarados. Explique o que torna um momento crítico e o que acontece quando se escolhe momento demais. Se não souber algum detalhe, explique como descobriria. Pode explorar: risco, custo de errar, atenção do time."

### S2.07

"O seu grupo formalizou metadados obrigatórios para fatos, dimensões e medidas e definiu versionamento com numeração semântica. Explique o que a numeração semântica comunica a quem consome e o que acontece quando ela é usada errada. Pode explorar: mudança compatível, quebra, expectativa de quem consome."

### S2.08

"O seu grupo classificou os dados do projeto e definiu controles por classe. Explique o que a classe de um dado decide na prática e o que acontece com um dado que ninguém classificou. Se não souber algum detalhe, explique como descobriria. Pode explorar: perfil de acesso, técnica de proteção, dado novo."

### S2.09

"O seu grupo validou a consistência entre os critérios do job e os passos do fluxo. Explique o que se descobre confrontando critério com passo e o que fazer com um critério que nenhum passo consegue verificar. Pode explorar: critério sem evidência, passo sem propósito, momento de verificação."

### S2.10

"O fluxo do seu grupo foi desenhado para dois perfis diferentes. Explique o que muda no que o sistema precisa entregar quando o perfil é o secundário e o que aconteceria com um fluxo só para os dois. Se não souber algum detalhe, explique como descobriria. Pode explorar: expectativa, nível de detalhe, acesso."

### S2.11

"O seu grupo detalhou perfis de acesso e as práticas de segurança e autenticação. Explique o que o perfil de acesso decide sobre o dado e por que a verificação não pode ficar só na camada que exibe a informação. Pode explorar: menor privilégio, contorno da interface, registro do acesso."

## Sprint 3 — perguntas brutas

### S3.01

"Explique como a sua solução percebe que uma execução do pipeline falhou, e o que ela faz em seguida. Diga também o que não pode ser reprocessado duas vezes. Pode explorar: sinal da falha, retentativa, efeito já gravado."

### S3.02

"O pipeline do seu grupo é orquestrado por DAG. Explique o que a orquestração resolve que um script em sequência não resolve, e o que precisa ser verdade para reexecutar só a tarefa que falhou. Se não souber, explique como descobriria. Pode explorar: dependência, reexecução parcial, histórico, agendamento."

### S3.03

"O seu grupo definiu a arquitetura e os contratos do pipeline, e implementou o acesso e a autenticação das fontes. Diga qual foi o seu papel nisso e o que o pipeline faz quando a fonte muda de estrutura sem avisar. Pode explorar: contrato declarado, campo novo, campo que sumiu, tipo trocado."

## Contagem conhecida

- Perguntas diferentes identificadas: **24**.
- Sprint 1: **10** perguntas diferentes.
- Sprint 2: **11** perguntas diferentes; S2.01 apareceu repetida nos prints.
- Sprint 3: **3** perguntas diferentes.
- A pergunta sobre o caminho do dado também apareceu em mais de um registro da Sprint 2.

## Como temos estudado

Nossa preparação passou a seguir este padrão:

1. **Começar pelo verbo e pelo critério da pergunta.** Identificamos se ela pede descrever, explicar uma decisão, comparar, dizer o que acontece quando algo falha ou indicar uma evidência.
2. **Responder com elementos reais do projeto.** Usamos nomes como Raw, Staging, Trusted, quarentena, Airflow, dbt, MinIO, `audit.audit_pipeline_runs`, os três cubos, o perfil A, M1/M2/M3, contratos e KPIs.
3. **Dar a consequência prática.** Explicamos o que a etapa resolve e o que quebra se ela for removida, atrasada ou aplicada incorretamente.
4. **Separar fato implementado de proposta.** Não apresentar como implementado algo que está apenas documentado ou proposto; por exemplo, distinguir snapshot acumulativo de uma eventual implementação de SCD Tipo 2.
5. **Evitar números decoráveis quando não são necessários.** Mantemos fórmulas, denominadores, filtros, grãos e relações; omitimos números específicos quando eles não ajudam a responder.
6. **Usar respostas curtas, mas completas.** A estrutura preferida é um parágrafo ou tópicos curtos, cobrindo diretamente todos os pontos pedidos.
7. **Usar feedback como critério de revisão.** A Sprint 1 mostrou que respostas genéricas perdiam pontos; a Sprint 2 mostrou que faltavam exemplos concretos de momentos, evidências e consequências; a Sprint 3 está sendo estudada em torno de falha, DAG, contratos, idempotência e schema drift.

### Exemplos do padrão

- Para uma pergunta sobre qualidade: não basta dizer que há validação; é preciso indicar a regra, o universo, a cobertura, a exceção e o que acontece com uma base incompleta.
- Para uma pergunta sobre fluxo: não basta listar camadas; é preciso dizer o que Raw, Staging, validação, quarentena, Trusted, DW e dashboard resolvem e o que quebra se cada uma sair do lugar.
- Para uma pergunta sobre pipeline: não basta dizer que há retry; é preciso citar a DAG, as duas tentativas, o registro em `audit.audit_pipeline_runs`, o `run_id`, o checksum e a chave idempotente.
- Para uma pergunta sobre verificação: não basta definir o conceito; é preciso citar um momento real, como o M2, em que pesquisas próximas ou além do prazo são conferidas, e indicar qual evidência confirma o critério.
