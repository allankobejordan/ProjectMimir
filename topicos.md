# ProjectMímir

Mesa de apuração documental para um escritório ou departamento jurídico. Um condutor abre um procedimento, anexa PDFs, controla prazos e pergunta ao acervo. A resposta volta com peça e página. Se o trecho não foi recuperado, o sistema recusa responder.

Mímir é o conselheiro que se consulta. Mímisbrunnr é o poço: o módulo que recupera o trecho. A API e a busca são duas peças, e a entrevista precisa dessa separação.

Ritmo previsto: 8 a 10 horas por semana, 18 semanas. O demo de entrevista é a etapa 5, por volta da semana 12. Até lá o produto sobe com um comando, passa por uma verificação de segurança e ainda não depende de nuvem.

A instalação é de um escritório e um banco. Cobrança, onboarding e vários clientes ficam para depois de existir uma segunda implantação e de estar claro o que quebra ao dividir os dados.

## Como vamos estudar

O objetivo não é digitar sintaxe. É sair de cada etapa sabendo explicar, em entrevista, **por que** aquela peça existe: segurança, cloud, IA aplicada e o stack que aparece em currículo.

A IA escreve o código. Você escreve a regra, o prompt e a leitura. Se a IA gerar algo que você não consegue explicar, a etapa não fechou.

### Quatro eixos do currículo

| Eixo | O que você precisa saber dizer | Onde entra |
| --- | --- | --- |
| Backend e API | Django, DRF, OpenAPI, Postgres, constraint, fila | Etapas 1 e 2 |
| Segurança | Papel, segredo fora do git, upload seguro, varredura lida | Em toda etapa; ZAP na 5 |
| Cloud e deploy | Docker, ECS, RDS, S3, IAM, Kubernetes | Etapas 5, 6 e 7 |
| IA na programação | Prompt com limite, RAG com citação, afinação só onde classifica | Prompt desde a 1; RAG na 3; afinação na 8 |

### O que fica na sua mão

- A regra do domínio (contrato ADR).
- O prompt, com limite e critério de pronto.
- A leitura do que foi gerado e da saída de erro: qual camada, por quê.
- A classificação de alerta de segurança: defeito, aceito com motivo, ou falso positivo.
- A resposta da entrevista, sem olhar o código.

### O que a IA escreve

Model, view, teste, configuração, Docker, manifesto, comando de terminal. HTML e CSS continuam fora. A tela vem do Unfold e do Refine.

### O prompt que não quebra o projeto

Um pedido solto gera arquivo a mais e regra a menos. O prompt tem cinco linhas, nesta ordem:

1. Objetivo, em uma frase.
2. O que não pode mudar: o contrato em `docs/adr/` e os arquivos que já existem.
3. Segurança: sem segredo no código, sem SQL concatenado, sem apagar arquivo que não foi citado.
4. Como saber que deu certo: o comando e a saída esperada.
5. Se um comando falhar, parar e mostrar a saída inteira. Não seguir para o próximo.

Exemplo, o que destravou o `startproject`:

```text
Crie o projeto Django 5.2 dentro de ProjectMímir, com o pacote config.
A pasta já tem docs, pyproject.toml e .venv. Não apague esses arquivos.
Não grave SECRET_KEY nova no repositório.
O destino do startproject precisa existir antes: mkdir tmp_project,
depois django-admin startproject config tmp_project, e só então suba
manage.py e config para a raiz.
Deu certo quando manage.py check terminar sem erro.
Se um comando falhar, pare.
```

### Git: treino de equipe (só você, fluxo de time)

Você digita os comandos Git. A IA não cria branch nem commit no seu lugar, salvo se você pedir explicitamente.

Quatro branches, cada uma com um papel:

| Branch | Papel |
| --- | --- |
| `allan-dev` | Uma demanda por vez |
| `senior-dev` | Outra demanda, em paralelo |
| `develop` | Integração: recebe as duas e é onde o conflito é resolvido |
| `main` | Só o que já passou pela `develop` e funciona; é o que sobe |

Ciclo de cada par de demandas:

1. Cada demanda é feita e commitada na sua branch de trabalho.
2. Na `develop`, entram as duas: `git merge allan-dev` e `git merge senior-dev`. Se as duas mexeram na mesma linha, o conflito aparece aqui e é resolvido aqui.
3. Testa na `develop`. Funcionou: `git switch main`, `git merge develop` e `git push`.
4. As duas branches de trabalho recebem a `develop` (`git merge develop`) antes da próxima demanda, para partirem da mesma base.

Comandos treinados: `status`, `branch`, `switch`, `add`, `commit`, `log`, `diff`, `merge`, `push`, `pull` e a resolução de conflito.

### Fechamento de demanda

Uma demanda só termina quando tem estas cinco partes. Sem elas, a próxima não começa.

1. **O que fizemos e por quê** — o pedido da cliente e o risco que ele evita.
2. **Como fizemos** — arquivos, comandos e a verificação que prova que funciona.
3. **O que aprendemos** — o conceito que serve fora deste projeto.
4. **Pergunta de entrevista** — você responde com as suas palavras.
5. **Resposta guiada** — o Sênior completa ou corrige a sua resposta.

### Onde paramos (progresso)

| Item | Status |
| --- | --- |
| Etapa 0 — contrato `0001` | Feita |
| Projeto Django (`manage.py`, `config`) | Feito; `runserver` abriu |
| Repositório e remoto | `main` no GitHub, com `.gitignore` corrigido |
| Fluxo Git (`allan-dev`, `senior-dev`, `develop`, `main`) | As quatro criadas e no GitHub |
| Migrações do Django admin/auth | Aplicadas |
| App e model `Procedimento` | Criado e na `main` |
| `SECRET_KEY` fora do código | Feita na `allan-dev`; chave trocada; aguarda a `develop` |
| Model `Parte` | Próxima demanda, na `senior-dev` |
| Postgres, API, Unfold, segurança de papel | Ainda não |

Cada etapa fecha com uma pergunta que você precisa responder sem olhar o código.

## Invariantes

- Resposta sem trecho recuperado não é emitida.
- O mesmo SHA-256 não gera segunda peça no mesmo procedimento.
- Prazo concluído não reabre sem um evento registrado.
- O PDF fica no armazenamento de objeto. O banco guarda hash, página e texto.
- Um escritório por banco até existir implantação real.

## Arquitetura

| Peça | Função |
| --- | --- |
| Django, Django REST framework e drf-spectacular | Regra, permissão e contrato OpenAPI. O serializer não é o domínio. |
| Django Unfold | Tela do escritório, pronta, em cima do admin. Sem HTML próprio. |
| Refine | Painel em React lendo a API, na etapa 5. Recurso declarado, não página desenhada. |
| PostgreSQL 16 | Procedimento, prazo e busca textual em português. |
| Mímisbrunnr (pgvector) | Trecho e embedding no mesmo banco da peça, na mesma transação. |
| Redis e Celery | Extração de PDF e embedding fora do request. |
| MinIO, depois S3 | O binário. |
| n8n | Lembrete de prazo. O Django publica o evento. |
| Docker Compose | Ambiente da etapa 5. |
| ECS, RDS, S3, Secrets Manager | Primeiro deploy. |
| Kubernetes (kind, depois EKS) | Web e worker com vida própria, depois do ECS estar claro. |

## Etapa 0 — Contrato do domínio (1 semana)

Sem `startproject`. O Django começa quando esta página existir.

Tópicos:

- Entidades: escritório, procedimento, parte, peça, versão da peça, prazo, evento.
- Estados do procedimento e o que cada transição exige.
- O que é imutável depois que a peça é protocolada.
- Três recusas explícitas: responder sem trecho, duplicar arquivo, reabrir prazo sem evento.
- Papéis: condutor, revisor, leitura.
- ADR de uma página com o que o sistema não faz.

Pergunta de fechamento: por que a peça tem versão e o PDF não é substituído no lugar?

## Etapa 1 — Núcleo Django e Postgres (3 semanas)

**Currículo desta etapa:** Django, DRF, OpenAPI, Postgres, papéis, CSRF, segredo em variável de ambiente, `gitleaks`, `bandit`/`semgrep` lidos por você.

**Como estudar:** a IA gera o código. Você pede com o prompt de cinco linhas, lê o model e o teste, e responde a pergunta de fechamento.

Tópicos:

- Projeto Django com settings separados por ambiente, dependências no `uv`. *(base já criada; falta o app do domínio)*
- Models com constraints de banco, não só validação no formulário.
- Banco em UTF8, com collation de português definida na criação, para a busca da etapa 3 tratar acento de forma estável.
- API REST: criar procedimento, registrar parte, registrar metadado da peça, abrir e concluir prazo.
- OpenAPI gerado com `drf-spectacular`. O n8n e o Refine leem esse contrato.
- Django Unfold como tela do condutor. O mesmo model aparece no admin. Não há template, CSS nem componente seu.
- Permissão por papel em cada endpoint e a mesma permissão no admin.
- Transação e `select_for_update` na conclusão do prazo.
- Índice para a consulta de prazos abertos por data limite.
- `EXPLAIN` dessa consulta, lido de verdade.
- Teste em que duas conclusões simultâneas deixam um único evento de conclusão.
- `select_related` e `prefetch_related` onde a listagem do procedimento cairia em N+1.
- `ruff`, `pyright` e `pytest` no fluxo do dia.
- Login do Django e permissão por papel. Concluir prazo exige o papel de condutor.
- CSRF ligado na sessão. A API que o n8n chama, mais adiante, usa credencial própria, não a sessão do navegador.
- `SECRET_KEY` e senha fora do repositório, em variável de ambiente.
- `gitleaks` no dia do primeiro commit, para um segredo colado no código não entrar no git.
- `bandit` e `semgrep` assim que existir código Python. Você lê o achado e diz se é defeito ou alerta. É o mesmo ofício do Syhunt, no seu repositório.
- `manage.py check --deploy` quando existir o settings de produção, ainda nesta etapa.

Pergunta de fechamento: o que acontece se dois usuários concluírem o mesmo prazo ao mesmo tempo?

## Etapa 2 — Arquivo e fila (2 semanas)

**Currículo:** Celery, Redis, MinIO/S3, upload seguro, job idempotente.

Tópicos:

- Upload que grava o PDF no MinIO e só então confirma a peça.
- SHA-256 como chave de duplicata dentro do procedimento. O nome do arquivo não decide.
- Request que responde assim que o objeto e o metadado existem.
- Tarefa Celery idempotente para extrair texto por página com `pypdf`.
- Reprocessar a mesma peça não duplica páginas.
- Falha no meio da extração deixa a peça num estado visível, com nova tentativa segura.
- Redis como broker. O worker não importa regra HTTP.
- Upload com tamanho máximo e tipo conferido pelo conteúdo. O nome enviado pelo navegador não vira caminho nem chave no MinIO.

Pergunta de fechamento: por que o hash, e não o nome do arquivo, decide a duplicata?

## Etapa 3 — Mímisbrunnr (3 semanas)

**Currículo:** RAG, pgvector, busca híbrida, avaliação com conjunto anotado, texto da peça como dado (não como ordem).

A busca é um módulo do projeto. LangChain fica de fora nesta etapa, para o ranking ser explicável.

Tópicos:

- Corte do texto por página, que é a unidade da citação.
- Embedding gravado com `pgvector`, na mesma transação que liga o trecho à peça.
- Busca híbrida: `tsvector` em português, com `unaccent`, mais similaridade vetorial.
- Endpoint de pergunta no procedimento.
- Resposta que cita peça e página. Sem trecho recuperado, a API recusa, com um código estável.
- Conjunto de 30 perguntas anotadas, com a página esperada, rodando em teste.
- Troca de modelo de embedding só entra se esse conjunto mostrar ganho.
- O texto da peça é dado, não ordem. Uma frase dentro do PDF pedindo para ignorar a citação não muda a consulta. O teste disso entra nas 30 perguntas.

Pergunta de fechamento: por que o embedding fica no Postgres e não num banco vetorial separado?

## Etapa 4 — Prazo no n8n (1 semana)

**Currículo:** automação n8n, webhook assinado, idempotência, retry.

Tópicos:

- Evento de prazo a dois dias do vencimento, publicado pelo agendador (`celery beat`).
- Webhook com assinatura. O n8n valida o segredo antes de agir.
- O fluxo chama a API, monta o lembrete e envia. O Django não conhece o canal.
- Chave de idempotência para o mesmo prazo não gerar dois lembretes.
- Retry do n8n quando a API estiver indisponível, sem duplicar o envio.

Pergunta de fechamento: o que impede o mesmo prazo de disparar dois lembretes?

## Etapa 5 — Docker e verificação (2 semanas)

**Currículo:** Docker Compose, GitHub Actions, Refine (React/TS sem página à mão), Semgrep, Bandit, pip-audit, OWASP ZAP.

Marco de entrevista. A partir daqui outra pessoa sobe o sistema e faz uma pergunta.

Tópicos:

- `docker compose` com web, worker, beat, Postgres, Redis, MinIO e n8n.
- Healthcheck e ordem de subida. O worker espera o banco.
- Variáveis de ambiente e volumes nomeados. Segredo fora da imagem.
- Log com identificador do request atravessando a extração.
- README com o caminho: criar procedimento, anexar PDF, esperar a extração, perguntar, ver o lembrete.
- Refine apontado para a API: lista de procedimento, peça e prazo, mais a tela da pergunta. TypeScript e React entram no currículo por esse painel, sem página feita do zero.
- GitHub Actions rodando o teste a cada push.
- Imagem da web e do worker rodando sem usuário root.
- `pip-audit` na lista de dependências, no mesmo fluxo do GitHub Actions.
- `semgrep` e `bandit` nesse fluxo. O push com defeito confirmado não segue.
- OWASP ZAP em modo baseline contra o Compose, com `DEBUG` desligado. Você anota cada alerta: corrigido, aceito com motivo, ou falso positivo.
- A etapa fecha com essa lista escrita. Ferramenta sem leitura não conta como verificação.

Pergunta de fechamento: o que quebra se o worker subir antes do Postgres? E, no relatório da varredura, qual alerta você corrigiu e qual descartou, e por quê?

## Etapa 6 — AWS (2 semanas)

**Currículo:** ECR, ECS, RDS, S3, Secrets Manager, IAM, security group, TLS, OpenTelemetry.

Kubernetes espera. Esta etapa ensina rede, permissão e banco gerenciado.

Tópicos:

- Imagem publicada no ECR pelo mesmo fluxo da etapa 5.
- Web e worker como serviços separados no ECS. O worker não atende HTTP.
- RDS para o Postgres, com migração executada no deploy.
- S3 no lugar do MinIO, sem mudar a regra da peça.
- Segredos no Secrets Manager. Nada de senha na task definition em texto.
- Security group mínimo: a web fala com o banco; o banco não fica aberto.
- TLS na frente da web. Cookie de sessão marcado como seguro nesse ambiente.
- OpenTelemetry com o mesmo request id na web, no worker e no rastro do webhook.

Pergunta de fechamento: por que o worker não fica no mesmo serviço da web?

## Etapa 7 — Kubernetes (2 semanas)

**Currículo:** kind, Deployment, Service, Job de migrate, readiness, Secret/ConfigMap; leitura do EKS.

Tópicos:

- Os mesmos processos descritos em manifests e subidos no `kind`.
- `Deployment` e `Service` da web, `Deployment` do worker, `Job` de migração.
- Probe de readiness na web, separado do processo estar vivo.
- Réplicas diferentes para web e worker, com o motivo escrito.
- ConfigMap para configuração e Secret para credencial.
- Leitura do que o EKS acrescentaria em relação ao ECS já feito: controle de réplica e rollout, não um produto novo.

Pergunta de fechamento: o que o probe de readiness cobre que o healthcheck do Compose não cobre?

## Etapa 8 — Classificador de peça (2 semanas)

**Currículo:** fine-tuning vs prompt, métrica de acerto/custo/latência, quando afinar e quando não.

Afinar não serve para “ensinar os PDFs” ao modelo que responde. O acervo muda. Quem responde continua sendo o Mímisbrunnr.

Tópicos:

- Rótulos feitos por você: ofício, ata, relatório, manifestação.
- Conjunto separado de treino e de verificação. A peça usada na medida não entra no treino.
- Um classificador afinado nesse conjunto.
- O mesmo conjunto medido com um prompt, sem afinação.
- Tabela de acerto, custo e latência. O prompt permanece se ganhar.
- O tipo previsto fica na peça e pode filtrar a busca. Ele não substitui a citação.

Pergunta de fechamento: por que o modelo que responde a pergunta não foi afinado?

## Ferramentas

| Ferramenta | Onde entra |
| --- | --- |
| Django Unfold | Tela interna desde a etapa 1. |
| drf-spectacular | Contrato OpenAPI da API, na etapa 1. |
| Refine | Painel React em cima da API, na etapa 5. |
| uv | Ambiente e dependências, desde a etapa 1. |
| ruff e pyright | Antes do erro de runtime. |
| pytest | Prazo concorrente e as 30 perguntas. |
| psycopg 3 | Driver do Postgres, inclusive o vetor. |
| pypdf | Texto por página. |
| Celery e Redis | Fila, a partir da etapa 2. |
| MinIO | Arquivo local, até o S3. |
| n8n | Lembrete, etapa 4. |
| Docker Compose | Marco da etapa 5. |
| GitHub Actions | Teste e, depois, imagem. |
| ECR, ECS, RDS, S3, Secrets Manager | Etapa 6. |
| kind e, no fim, EKS | Etapa 7. |
| OpenTelemetry | Request id no deploy. |
| gitleaks | Segredo no git, no primeiro commit da etapa 1. |
| bandit e semgrep | Código Python, a partir da etapa 1 e no CI da etapa 5. |
| pip-audit | Dependência com falha conhecida, no CI da etapa 5. |
| OWASP ZAP baseline | Aplicação rodando, no fim da etapa 5, com DEBUG desligado. |

## Segurança, em uma leitura

O controle nasce junto com a peça que ele protege. Autenticação na etapa 1, porque é ali que existe usuário. Upload na etapa 2, porque é ali que existe arquivo. Texto hostil de PDF na etapa 3, porque é ali que o modelo lê a peça. Assinatura na etapa 4, porque é ali que outro sistema chama o seu. Varredura na etapa 5, porque só então existe um sistema inteiro para apontar a ferramenta. Rede e cofre de segredo na etapa 6, porque só então existe nuvem.

`gitleaks`, `bandit`, `semgrep` e `pip-audit` olham o repositório e as bibliotecas. O ZAP olha a aplicação no ar, em varredura baseline, na instalação que você mesmo sobe. O trabalho de sênior é classificar o relatório, não colecionar ferramenta.

## O que fica de fora até haver motivo

- Escrever sintaxe à mão como exercício.
- HTML, CSS e frontend próprio.
- Vários escritórios no mesmo banco.
- Cobrança e cadastro self-service.
- LangChain como casca da busca.
- Afinar o modelo que redige a resposta.
- Kubernetes antes de o Compose e o ECS mostrarem web e worker com cargas diferentes.
