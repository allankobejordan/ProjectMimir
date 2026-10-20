# 0002 — PostgreSQL 16 em container

## Contexto

O projeto nasceu com SQLite, o banco padrão do `startproject`. As próximas etapas dependem de recursos que o SQLite não tem:

- Trava de linha (`select_for_update`) para dois usuários não concluírem o mesmo prazo ao mesmo tempo.
- `pgvector`, para guardar os embeddings da etapa 3 no mesmo banco das peças.
- Busca textual em português (`tsvector` com `unaccent`).

Também é preciso que o banco seja igual na máquina de qualquer pessoa que rodar o projeto, e igual ao do deploy.

## Decisão

PostgreSQL 16, num container descrito no `docker-compose.yml`, com:

- Usuário, senha e nome do banco no `.env`. O Django lê a conexão de `DATABASE_URL`.
- Porta publicada só em `127.0.0.1`.
- Dados num volume nomeado (`mimir_pgdata`).
- Imagem `postgres:16`, baseada em Debian.
- SQLite fora do projeto, inclusive nos testes.

## Alternativas consideradas

**MySQL 8.** Conhecido pelo trabalho com PHP. Descartado porque não tem equivalente maduro ao `pgvector` dentro do mesmo banco, e porque uma migração que falha no meio deixa o esquema pela metade: o MySQL não desfaz DDL dentro de transação, o Postgres desfaz.

**Postgres instalado direto na máquina.** Já existe um nesta máquina, na porta 5432. Descartado porque a versão e as extensões mudam de máquina para máquina, e o deploy da etapa 6 usa container. Por isso o container publica na 5433.

**Imagem `postgres:16-alpine`.** Menor. Descartada porque a Alpine usa a musl, e a ordenação de texto pode diferir da glibc usada no deploy. Para um sistema com busca em português, a diferença de ordenação é um bug difícil de achar.

**SQLite nos testes, Postgres no sistema.** Testes mais rápidos. Descartado porque o teste passaria num banco que não tem trava de linha nem `pgvector`, e falharia só em produção.

## Consequências

- Rodar o projeto exige Docker. O README traz o passo a passo.
- O usuário do banco no container é superusuário. Isso vale só para o ambiente local, porque o Django precisa criar o banco de teste. No deploy, a aplicação usa um usuário sem esse poder.
- A senha precisa ser segura para URL, porque vai dentro da `DATABASE_URL`. Caracteres como `@`, `/` e `#` quebram a leitura da URL.
- A collation em português fica para a etapa da busca, quando a ordenação de texto passar a importar.
