# ProjectMímir

Mesa de apuração documental. Django 5.2, Python 3.11, PostgreSQL 16.

## Pré-requisitos

- [uv](https://docs.astral.sh/uv/)
- Docker com Compose v2, com o seu usuário no grupo `docker`

## Subir do zero

1. Copie o modelo de configuração:

   ```bash
   cp .env.example .env
   ```

2. Gere uma chave e uma senha, e cole cada uma no `.env`:

   ```bash
   uv run python -c "import secrets; print(secrets.token_urlsafe(50))"
   uv run python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

   - A primeira vai em `SECRET_KEY`.
   - A segunda vai em `POSTGRES_PASSWORD` e no lugar de `SENHA` na `DATABASE_URL`. As duas precisam ser iguais.

3. Suba o banco e espere ele ficar `healthy`:

   ```bash
   docker compose up -d
   docker compose ps
   ```

4. Crie as tabelas e rode os testes:

   ```bash
   uv run python manage.py migrate
   uv run python manage.py test dominio
   ```

5. Suba o sistema:

   ```bash
   uv run python manage.py runserver
   ```

## Banco

- O Postgres roda no container `db`, publicado só em `127.0.0.1`, na porta `POSTGRES_PORT` (padrão `5433`).
- Os dados ficam no volume `mimir_pgdata`. `docker compose down` para o banco e mantém os dados.
- Para entrar no banco: `docker compose exec db psql -U mimir mimir`.

Decisões de arquitetura ficam em `docs/adr/`.
