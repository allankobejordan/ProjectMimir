# Modelo de prompt para demanda

Uma demanda é um pacote: uma capacidade de negócio inteira, com regra, teste e tela quando houver. O tamanho certo é o que você consegue revisar em 15 minutos. Maior que isso, a revisão vira leitura por cima.

## As oito partes

1. **Contexto** — projeto, versão, onde está o contrato e o que já existe. A IA não lembra da conversa anterior.
2. **Objetivo** — uma frase, do ponto de vista da cliente.
3. **Regras de negócio** — uma por linha, tiradas do ADR. Cada uma vai virar um teste.
4. **Escopo** — o que entra e, com o mesmo peso, o que não entra.
5. **Segurança e restrições** — arquivos que podem mudar, dependências, dados de teste e comandos proibidos.
6. **Pronto quando** — comandos que você roda e o resultado esperado.
7. **Entrega** — como a IA deve responder: arquivos alterados, uma frase por regra, como testar e, quando houver escolha de tecnologia, as alternativas e o motivo da escolhida.
8. **Dúvida** — se algo estiver ambíguo, perguntar antes de implementar.

## Travas de segurança que entram em todo prompt

- Não alterar arquivos fora da lista do escopo.
- Não adicionar dependência sem perguntar.
- Sem SQL escrito à mão; usar o ORM.
- Sem segredo, senha ou dado pessoal real no código e nos testes.
- Validar no backend toda entrada que vem de fora.
- Não rodar comandos Git nem comandos que apagam (`rm -rf`, `reset --hard`, `push --force`).
- Teste para cada recusa, não só para o caminho feliz.

## Exemplo preenchido

```text
Contexto
Projeto Django 5.2 em ProjectMímir, app dominio. O contrato está em
docs/adr/0001-contrato-do-dominio.md. Já existem Procedimento, com os
três estados, e Parte.

Objetivo
O condutor abre e conclui prazos de um procedimento, e cada conclusão
fica registrada.

Regras de negócio
- Prazo só é aberto com o procedimento em apuração.
- Prazo tem descrição e data limite; o estado é aberto ou concluído.
- Concluir um prazo grava um Evento.
- Evento nunca é editado nem apagado.
- Prazo concluído só reabre com um Evento de reabertura.
- Dois pedidos concluindo o mesmo prazo ao mesmo tempo geram um único Evento.

Escopo
Inclui: models Prazo e Evento, migração, admin (Evento só leitura), testes.
Não inclui: API, telas novas, mudanças em config/settings.py.

Segurança e restrições
- Só alterar arquivos dentro de dominio/.
- Não adicionar dependência sem perguntar.
- Usar o ORM; nada de SQL escrito à mão.
- Dados de teste fictícios.
- Não rodar comandos Git.

Pronto quando
- uv run python manage.py test dominio passa, com um teste por regra,
  incluindo as recusas.
- uv run python manage.py makemigrations --check não acusa migração pendente.

Entrega
Liste os arquivos alterados, explique cada regra em uma frase e diga
como eu testo sozinho.

Dúvida
Se algo do contrato estiver ambíguo, pergunte antes de implementar.
```

Leitura de sênior deste exemplo: a última regra, a dos dois pedidos ao mesmo tempo, depende de trava de linha no banco. O SQLite não tem isso. Ler o prompt antes de mandar revela a dependência: o pacote do Postgres precisa vir antes deste.

## Checklist para revisar o que a IA entregou

- [ ] Os arquivos alterados são só os do escopo?
- [ ] Cada regra do prompt tem um teste com o nome da regra?
- [ ] Existe teste para cada recusa?
- [ ] Os testes passam quando você mesmo roda?
- [ ] A migração cria só o que foi pedido?
- [ ] Nenhum segredo, senha ou dado pessoal real apareceu?
- [ ] Nenhuma dependência nova sem você ter aprovado?
- [ ] Você consegue explicar cada regra sem abrir o código?

Se alguma resposta for não, a demanda volta antes do commit.
