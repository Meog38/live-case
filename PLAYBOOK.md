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
