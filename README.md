# Normalizador e enriquecedor de leads

## O que foi pedido

Receber `leads_raw.json` (dados de marketing bagunçados) e produzir um JSON pronto pro CRM: leads limpos/validados/classificados, os que não dá pra aproveitar com o motivo, e um resumo de contagens — conforme o contrato em `case.md`.

## Arquitetura

Medallion simplificado, rodando local em JSON (sem banco — dado batch único, não ingestão contínua):

- **`dados-do-case/bronze/bronze.py`** → lê `dados-do-case/leads_raw.json`, grava `dados-do-case/bronze/leads_bronze.json`. Schema unificado (une `name`/`nome` como colunas separadas, sem escolher uma), todo campo cru vira texto ou `null`, nenhuma limpeza. É fidelidade ao dado como chegou — serve de auditoria, não de camada de negócio.
- **`dados-do-case/silver/silver.py`** → lê o bronze, normaliza, valida, deduplica e classifica. Grava `dados-do-case/silver/leads_clean.json` — exatamente o schema pedido no case.
- **Gold não foi construído** (ver Próximos passos) — o case não pede KPI/dashboard, só o JSON leads/rejected/summary que o silver já entrega.

## Decisões técnicas

- **Email é a chave do lead**: normalizado (`strip().lower()`), validado por regex. Sem email válido → rejeitado, com uma exceção controlada abaixo.
- **Correção de typo de email**: só o caso inequívoco de faltar o `@` (ex: `carlos.example.com` → `carlos@example.com`) é corrigido automaticamente. Quando não há email nenhum, continua rejeitado — não inventamos identidade a partir de outro campo.
- **Duplicatas**: mescladas por campo (não descarta o registro inteiro) — cada campo pega o valor mais recente disponível por `created_at`, preenchendo com o registro mais antigo quando o mais novo estiver vazio.
- **Nome**: coalesce de `name`/`nome` (a entrada tinha as duas chaves), `title case`, espaços colapsados.
- **Telefone**: normalizado pra `+55DDDNNNNNNNNN` (só dígitos, prefixo BR — todos os leads da amostra são brasileiros). Ilegível/curto demais → `null`.
- **Datas**: 6 formatos distintos suportados (ISO, `DD/MM/YYYY`, `YYYY/MM/DD`, `Jan D, YYYY`, ISO datetime, epoch unix). Ambiguidade dia/mês assumida como **dia primeiro**, por consistência com o resto do dado (BR).
- **Segment**: classificado via IA (Gemini), com fallback determinístico por palavra-chave se a chamada falhar ou a key não estiver configurada. Mensagem ausente ou vazia é sempre `unknown` — nunca é chutado, mesmo pela IA.
- **`rejected.raw`**: guarda o registro exatamente como chegou, sem nenhuma transformação — é o dado bruto pra quem for investigar manualmente.

## Validação

`silver.py` roda duas checagens a cada execução, sem depender de conferência visual:
- `validate_output`: consistência interna dos números (`received = valid + rejected`, `leads = valid - duplicates_removed`, emails únicos).
- `validate_against_case_schema`: relê o **arquivo gravado em disco** e confere campo a campo contra o contrato literal do `case.md` (chaves exatas, tipos, `email` minúsculo/válido/único, `created_at` em ISO, `segment` restrito ao enum).

## Números (dataset atual)

`received: 12 → valid: 10 (1 recuperado por correção de typo) → duplicates_removed: 2 → leads finais: 8 → rejected: 2`

## Se eu tivesse acesso ao time que pediu esse JSON, perguntaria/sugeriria

**1. O critério de "lead válido" deveria ser email OU telefone, não só email?**
Hoje um lead só entra em `leads[]` com email válido (ou corrigível por typo óbvio). Isso derruba casos como o da "Ana" no dataset: sem email, mas com telefone válido e uma mensagem de intenção clara. Se o negócio aceita contato só por telefone, o critério de entrada devia ser "email válido **ou** telefone válido" — o que muda o schema (email deixaria de ser obrigatório, telefone vira chave alternativa). É uma decisão de produto, não técnica: eu não tomaria essa decisão sozinho sem confirmar com quem vai usar o dado no CRM.

**2. O problema real está na captação, não no tratamento.**
Boa parte do trabalho aqui foi reconciliar sujeira que nunca deveria ter chegado assim: telefone em 5 formatos diferentes, email com espaço/maiúscula/typo, datas em 6 formatos. Sugeriria ao time de marketing/produto: máscara de input no campo telefone desde o formulário, validação de email em tempo real (bloquear submit sem `@`), e exigir pelo menos um contato válido (email ou telefone) antes de aceitar o lead. Tratar na origem é mais barato do que reconciliar depois — e reduz o volume de `rejected` estruturalmente, não só com mais regras no pipeline.

## Próximos passos (não implementados)

- **Gold layer**: agregações por `segment`/`source` (contagens, taxa de rejeição) como fonte pra um dashboard — a visão original de arquitetura incluía isso, mas o case não exige e não deu tempo.
- **Testes unitários isolados** pra edge cases fora do dataset real (telefone com 8 dígitos, data tipo `"abc"`, etc.) — hoje a cobertura vem só das asserções contra o dado real.

