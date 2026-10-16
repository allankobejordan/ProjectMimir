# Contrato do domínio 

## Contexto

Uma instalação atende um escritório. O condutor abre um procedimento, registra as partes, anexa peças e acompanha prazos. A consulta só responde com a peça e a página.

## Entidades

- Escritório: a instalação.
- Procedimento: O caso.
- Parte: quem figura no caso.
- Peça: o PDF  protocolado. Uma peça nova não apaga a anterior.
- Prazo: obrigação com data. Gravamos aberto ou concluído.
- Evento: registro do que aconteceu. Só entra, não se edita.

## Estados do procedimento

- Rascunho: ainda dá para ajustar as partes. Não entra peça nem prazo.
- Em apuração: entra peça, corre prazo, a consulta já responde.
- Encerrado: não entra peça nem prazo, e a consulta continua.



Rascunho passa para em apuração. Em apuração passa para encerrado.
Encerrado permanece encerrado.

## Recusa

1. Não responde se não achou o trecho da peça.
2. Não grava o mesmo arquivo duas vezes no mesmo procedimento.
3. Não reabre prazo concluído sem um evento novo.