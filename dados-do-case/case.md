# Case — Normalizador e enriquecedor de leads

> Enunciado entregue ao candidato no início do case. Use com a ferramenta de IA que você preferir.

## Contexto

O time de marketing recebe leads de uma fonte de dados, e os dados chegam **bagunçados**: campos faltando, formatos inconsistentes, emails inválidos, duplicatas. Antes de subir esses leads para aplicação, eles precisam ser limpos, validados e classificados.

Sua tarefa é **construir uma ferramenta que recebe o arquivo bruto e produz uma lista pronta pro CRM**.

## Mão na massa

A partir daqui é a construção da ferramenta descrita acima.

## Entrada

O arquivo [`leads_raw.json`](leads_raw.json) — uma lista de leads crus, do jeito que chegaram. Espere inconsistências de verdade (você vai descobrir quais ao olhar).

## Saída desejada

Um JSON com **dois grupos** e um **resumo**:

```jsonc
{
  "leads": [
    {
      "email": "string",          // minúsculo, sem espaços, válido — é a chave do lead
      "name": "string | null",    // limpo (sem espaços sobrando); null se ausente
      "phone": "string | null",   // normalizado de forma consistente; null se ausente/ruim
      "company": "string | null", // null se vazio/ausente
      "source": "string | null",
      "created_at": "string | null", // data normalizada para o formato ISO YYYY-MM-DD
      "segment": "hot | warm | cold | unknown"
    }
  ],
  "rejected": [
    { "reason": "string", "raw": { } }   // leads que não dá pra aproveitar, com o motivo
  ],
  "summary": {
    "received": 0,
    "valid": 0,
    "duplicates_removed": 0,
    "rejected": 0
  }
}
```

## Regras

1. **Email é a identidade do lead.** Padronize e trate o que não for válido.
2. **Normalize as datas**, a entrada tem vários formatos.
3. **Telefone**: deixe num formato consistente.
4. **`segment`** é a intenção do lead, inferida a partir da **mensagem** dele:
   - `hot` = quer comprar / urgente · `warm` = comparando / decisão futura · `cold` = só pesquisando.
   - **Sem mensagem, não há o que inferir → `unknown`** (não chute).
5. O resultado tem que **bater com o schema** acima.

## Combinados

- Pense em voz alta — queremos acompanhar seu raciocínio e como você usa a IA.
- Comece pelo que entrega valor; o que não der tempo, explique como faria.
- Pode perguntar. Faça as perguntas que você faria num problema real antes de sair codando.

## Glossário

**Lead** - um contato que demonstrou algum interesse no seu produto/serviço (deixou e-mail, preencheu formulário, pediu orçamento), mas ainda não é cliente. É um potencial cliente que entrou no radar.
**CRM** (Customer Relationship Management) — o sistema/software onde você registra e acompanha todos esses contatos e clientes: quem são, o histórico de conversas, em que etapa da negociação estão e quais os próximos passos. É a ferramenta que organiza o relacionamento com leads e clientes num só lugar.
**Trade-off** — uma escolha em que, para ganhar uma coisa, você abre mão de outra. Não dá pra ter as duas ao mesmo tempo, então você troca um benefício por outro.