# Playbook - Live Case AI Builder

## Antes (15 min de setup, conforme o PDF deles)
- Terminal aberto, Claude Code logado e funcionando (roda um prompt de teste).
- Python funcionando (`python --version`).
- Git funcionando (`git --version`), pasta de trabalho vazia com git init.
- Compartilhamento de tela testado na ferramenta de call.
- CLAUDE.md pronto na pasta (esse arquivo já prepara o Claude Code pra
  trabalhar do jeito certo desde o primeiro prompt).

## Nos 50 min de construção

1. Primeiros ~5 min: leia o leads_raw.json e a spec você mesma, sem o
   Claude. Entenda o problema com a sua cabeça antes de delegar.
2. Primeiro prompt pro Claude Code: contexto completo + spec colada +
   caminho do arquivo + peça pra ele inspecionar o dado antes de codar
   qualquer transformação.
3. Valide cada passo antes de avançar pro próximo. Fale em voz alta o que
   está checando - o avaliador está prestando atenção nisso.
4. A cada 10-15 min, commit. Isso também ajuda a mostrar progresso mesmo
   se não terminar.
5. Se o Claude errar ou for por um caminho ruim, corrija rápido e direto:
   diga o que está errado e o que você quer no lugar. Não deixe rodar
   solto.
6. Nos últimos 10 min: para de pedir feature nova. Garanta que roda sem
   erro e que o output bate com o exemplo esperado.

## Debrief (3 min pitch + 3 min perguntas)

Pitch (3 min), estrutura sugerida:
- O que foi pedido (1 frase).
- O que você decidiu fazer e por quê (as decisões técnicas importam mais
  que o código em si).
- Até onde chegou: o que funciona, com prova rápida (roda e mostra).
- O que faltou e o que você faria a seguir, se tivesse mais tempo.

Perguntas prováveis dos avaliadores:
- Por que essa decisão técnica e não outra.
- Como você validou que o output está certo.
- Onde você corrigiu o Claude e por quê.
- O que você faria diferente com mais tempo.

Não peça desculpa por não terminar. Eles disseram explicitamente que não
precisa terminar tudo.

## Multiagente (Task tool) - como usar nos 50 min

Tem 4 subagentes prontos em .claude/agents/: data-explorer, spec-analyst,
builder, verifier. O CLAUDE.md já instrui o Claude Code a seguir esse
protocolo sozinho, mas o fluxo esperado é:

1. Spec chegou -> dispara data-explorer + spec-analyst juntos (paralelo,
   os dois só leem, sem risco). ~2-3 min.
2. Você recebe: schema real do dado + checklist de requisitos + o que é
   independente vs dependente. Você decide a decomposição, não deixa o
   Claude decidir sozinho - esse é o seu momento de mostrar decisão
   técnica pros avaliadores.
3. Só manda builder em paralelo pra peças de verdade independentes (ex:
   normalizar telefone e normalizar email são independentes; dedup
   depende dos dois já normalizados, então não paraleliza com eles).
   Se dependente, faz sequencial - não force paralelo pra parecer
   sofisticada, isso queima tempo à toa.
4. Depois de integrar as peças, dispara verifier com o checklist + o
   output, nunca com o código (evita validar "de dentro" do próprio viés).
5. Narre em voz alta cada disparo: o quê, por quê paralelo ou sequencial,
   o que voltou. Isso é literalmente o que eles estão avaliando.

Regra de ouro: se a tarefa só tem 1-2 peças, esquece orquestração e vai
direto sequencial com o Claude. Multiagente só vale a pena quando tem
peça de verdade independente pra paralelizar - senão é só overhead.
