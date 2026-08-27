# Contexto

Sessão técnica ao vivo (live case, processo "AI Builder"). Vou receber um
dataset JSON (provavelmente leads_raw.json) e uma especificação de saída
no início da sessão. Tenho 50 min de construção individual, e depois um
debrief de 3 min de pitch + 3 min de perguntas.

O que está sendo avaliado: como eu converso com você (contexto e instruções
que dou, como corrijo o rumo quando você erra), como eu valido o que você
produz, minhas decisões técnicas, e minha comunicação. Não precisa terminar
tudo: um raciocínio bem conduzido vale mais que solução completa no susto.

# Como trabalhar comigo nessa sessão

1. Antes de escrever qualquer código, reformule a spec com suas palavras e
   liste as suposições que está fazendo. Pergunte se algo não estiver claro.
2. Sempre inspecione o JSON de entrada de verdade primeiro (estrutura,
   campos, nulos, duplicatas, formatos inconsistentes) antes de decidir a
   lógica de transformação. Não assuma schema.
3. Construa em passos pequenos e validáveis: uma função por vez, testa com
   uma amostra real, só segue pro próximo requisito depois que eu confirmar.
4. Depois de qualquer mudança relevante, rode o código e mostra o resultado
   (nem que seja print de 2-3 registros). Não acumule várias mudanças sem
   validar entre elas.
5. Escreva validações explícitas do output contra a spec (assert, contagens,
   checagem de schema) em vez de esperar eu confirmar visualmente.
6. Se a spec for ambígua, não adivinhe: registre a suposição em comentário
   ou log e segue.
7. Código simples e legível é melhor que código esperto. Sem abstração,
   framework ou lib desnecessária. Biblioteca padrão do Python primeiro; só
   usa pandas ou outra lib se resolver claramente mais rápido.
8. Depois de cada etapa funcional, sugira um `git commit` com mensagem
   clara. Prefiro checkpoints a perder progresso.
9. Explique em 1-2 frases o que você fez e por quê, principalmente decisões
   técnicas — eu vou precisar repetir isso pros avaliadores no debrief.
10. Se eu corrigir o rumo, não insista na abordagem antiga. Ajusta e segue,
    sem ficar se justificando.
11. Aos 40 minutos de sessão, para de adicionar feature nova. Foca em
    garantir que o que existe roda sem erro e o output bate com o exemplo
    esperado da spec.

# Ambiente

Python 3.x, rodando localmente. Vou compartilhar tela — mantenha respostas
objetivas no terminal, sem textão.
