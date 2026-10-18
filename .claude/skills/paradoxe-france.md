# Skill: Paradoxe France — Pipeline Completo de Produção de Vídeo

## Descrição
Produz episódios completos para o canal YouTube **Paradoxe France**: pesquisa, roteiro em francês, narração IA, download de cenas, montagem com ffmpeg, motion graphics cinematográficos e música de fundo. Entrega o MP4 final pronto para upload.

## Invocação
O usuário diz o tema do episódio (ex: "episódio sobre a crise imobiliária") ou o número da lista em `canal_contradictions/ESTRATEGIA_CANAL.md`.

## Contexto Obrigatório
Antes de começar, leia:
- `canal_contradictions/BRIEFING.md` — briefing completo do canal
- `canal_contradictions/ESTRATEGIA_CANAL.md` — lista de episódios e identidade visual

## Pipeline de Produção (executar na ordem)

### ETAPA 1 — PESQUISA (WebSearch)
1. Pesquise o tema em **fontes confiáveis francesas**: INSEE, Le Monde, Le Figaro, France Info, Eurostat, Statista, rapports officiels, Wikipedia FR
2. Colete: dados estatísticos com datas, comparações internacionais, citações de especialistas, exemplos concretos de lugares/pessoas
3. Anote todas as fontes para a descrição do vídeo
4. Pesquise os dois lados: a imagem oficial/positiva E a realidade/contradição

### ETAPA 2 — ROTEIRO EM FRANCÊS
Escreva o roteiro completo seguindo esta estrutura obrigatória:

```
HOOK (0:00 - 0:30)
- Frase de impacto chocante com dado concreto
- Pergunta retórica que prende o espectador
- Tom: direto, intrigante

CONTEXTO — LE BEAU CÔTÉ (0:30 - 3:00)
- Apresenta a imagem oficial/idealizada da França sobre o tema
- Dados positivos, conquistas, prestígio internacional
- Tom: admirativo mas com ironia sutil

DÉVELOPPEMENT — LA CONTRADICTION (3:00 - 15:00)
- Revela a contradição com dados, exemplos, lugares reais
- Alterna entre dados estatísticos, exemplos locais e reflexões do narrador
- Subdivide em 3-4 blocos temáticos com transições naturais
- Inclui comparações com outros países europeus
- Tom: investigativo, questionador

CLIMAX (15:00 - 18:00)
- O ponto mais forte, a comparação mais chocante
- Confrontação direta: imagem vs realidade
- Tom: grave, impactante

RÉFLEXION + CTA (18:00 - 20:00)
- Comentário editorial pessoal do narrador (não julgamento, mas reflexão)
- Pergunta aberta ao público
- CTA: "Abonnez-vous à Paradoxe France pour découvrir les autres paradoxes de ce pays fascinant. Dites-nous en commentaire..."
- Sugere o próximo episódio relacionado
```

#### Regras do roteiro:
- **Idioma**: 100% francês, fluente e natural (não tradução do português)
- **Narrador EDITORIAL**: NÃO apenas informa — ele COMENTA, questiona, faz apartes pessoais ("Et c'est là que ça devient intéressant...", "On pourrait se demander...", "Personnellement, ce qui me frappe...")
- **Frases curtas e ritmadas** — estilo jornalístico cinematográfico
- **Dados concretos** com fontes (números, datas, percentagens, comparações)
- **Tom**: sério, respeitoso, direto — nunca agressivo ou sensacionalista
- **Mostra os dois lados** — termina com reflexão, não julgamento
- **Conforme monetização YouTube**: conteúdo original, valor educativo, sem repetição, sem clickbait, sem discurso de ódio, sem afirmações sem fonte
- **Duração alvo**: 20 minutos (aprox. 3000-3500 palavras em francês)

#### Conferência linguística:
Após escrever, releia todo o roteiro verificando:
- Fluidez natural em francês (pas de traduction littérale)
- Coerência narrativa do início ao fim
- Transições suaves entre blocos
- Variedade de vocabulário (sem repetições próximas)
- Expressões idiomáticas francesas autênticas
- Dados corretos e coerentes entre si

### ETAPA 3 — NARRAÇÃO (API Dark Planner)
1. Envie o roteiro completo para a API do Dark Planner:
   - URL: variável de ambiente `DARK_PLANNER_API_URL`
   - Key: variável de ambiente `DARK_PLANNER_API_KEY`
   - Idioma: `fr` (francês)
   - Voz: conforme configuração do projeto
2. Salve o áudio MP3 em `saida/<nome_episodio>/narracao.mp3`
3. Meça a duração exata com ffprobe

**Fallback**: Se Dark Planner não disponível, use vidIQ voiceover (voz Daniel, voiceId: onwK4e9ZLuTAKqWW03F9, categoria: informative_educational)

### ETAPA 4 — DOWNLOAD DE CENAS E VÍDEOS
1. Para cada bloco do roteiro, defina 4-6 palavras-chave de busca em inglês para Pexels
2. Baixe vídeos via API Pexels (`PEXELS_API_KEY`) — resolução próxima de 1920x1080, landscape
3. **Fontes alternativas** (se Pexels insuficiente): Mixkit (scraping CDN), Pixabay Videos

#### Regra de duração variada das cenas (FUNDAMENTAL):
As cenas NÃO devem ter duração uniforme. Varie assim:
- Cenas curtas de ambientação: **3-4 segundos**
- Cenas de transição: **5-6 segundos**
- Cenas com dados/estatísticas na tela: **8-10 segundos**
- Cenas de impacto/clímax: **6-8 segundos**
- Cenas contemplativas/reflexão: **10-14 segundos**
- Cenas de abertura/fechamento: **5-7 segundos**

Nunca usar a mesma duração em mais de 2 cenas consecutivas. A variação de ritmo é essencial para manter o espectador engajado.

4. Salve os brutos em `saida/<nome_episodio>/temp/bruto_XXX.mp4`
5. Registre créditos Pexels em `saida/<nome_episodio>/creditos_pexels.txt`

### ETAPA 5 — MÚSICA DE FUNDO
1. Baixe uma faixa instrumental adequada ao tom do episódio:
   - **Pixabay Music** (pixabay.com/music) — livre de royalty, sem atribuição
   - **Mixkit Music** (mixkit.co/free-stock-music) — livre, sem direitos autorais
2. Estilo: cinematográfico, atmosférico, documentário — nunca intrusivo
3. Salve em `saida/<nome_episodio>/musica_fundo.mp3`
4. Volume na mixagem final: **0.06 a 0.10** (bem baixo, sob a narração)

### ETAPA 6 — MONTAGEM (ffmpeg)
1. Padronize cada cena: `1920x1080`, `30fps`, `yuv420p`, `setsar=1`
   ```
   ffmpeg -y -i bruto.mp4 -t <duracao_variada> -an \
     -vf "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,fps=30,format=yuv420p,setsar=1" \
     -c:v libx264 -preset veryfast -crf 20 cena_XXX.mp4
   ```
2. Concatene todas as cenas com a narração:
   ```
   ffmpeg -y -f concat -safe 0 -i lista.txt -i narracao.mp3 \
     -stream_loop -1 -i musica_fundo.mp3 \
     -filter_complex "[2:a]volume=0.08[m];[1:a][m]amix=inputs=2:duration=first[a]" \
     -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k \
     -t <duracao_narracao> -movflags +faststart saida.mp4
   ```

### ETAPA 7 — MOTION GRAPHICS (estilo referência analisado)
Aplique motion graphics cinematográficos inspirados no DNA visual analisado:

#### Elementos obrigatórios:
1. **Cartela de título do episódio** (0-4s): fundo escuro com overlay 55%, título em Montserrat ExtraBold 100-120px branco centralizado, linha decorativa vermelha (#E63946) abaixo, subtítulo em Regular 36px cinza claro, fade in com scale-up sutil

2. **Lower thirds** (para cada bloco temático): barra vermelha vertical 6px à esquerda, fundo preto @0.65, título Bold 44-46px branco, subtítulo Regular 26-28px cinza, fade in/out 0.4s

3. **Stat boxes** (para cada dado de impacto): caixa preta @0.7 centralizada, barra vermelha 4px no topo, número em Bold 48-64px vermelho (#E63946), descrição em Regular 22-28px branco, fade in 0.5s

4. **Barra de impacto** (para o clímax): faixa vermelha full-width @0.85 no centro vertical, texto Bold 60-68px branco

5. **Efeito typewriter** (para reflexões do narrador): texto monoespaçado branco, aparecendo letra a letra (simular com fade sequencial de palavras)

6. **Marca-texto animado** (para citações/dados-chave): fundo amarelo pastel @0.3 atrás de texto específico

7. **Cartela de encerramento** (últimos 6s): overlay escuro, título do canal "PARADOXE FRANCE" em Bold 52px, subtítulo do episódio em vermelho, linhas decorativas

#### Regras visuais:
- Fonte títulos: `fonts/Montserrat-ExtraBold.ttf`
- Fonte corpo: `fonts/Montserrat-Regular.ttf`
- Paleta: azul escuro (#1B2A4A), vermelho (#E63946), branco, preto
- SEM barra de progresso no topo
- SEM barras permanentes em cima/baixo
- Todos os textos dos motion graphics em FRANCÊS
- Timing sincronizado com a narração (usar timestamps do áudio)

### ETAPA 8 — RENDERIZAÇÃO FINAL
```
ffmpeg -y -i video_com_audio.mp4 -vf "<filtros_motion_graphics>" \
  -c:v libx264 -preset medium -crf 18 -c:a copy \
  -movflags +faststart video_final.mp4
```

### ETAPA 9 — CONFERÊNCIA FINAL
Antes de entregar, verifique:
- [ ] Vídeo abre e reproduz sem erros
- [ ] Duração entre 18 e 25 minutos
- [ ] Áudio narração audível e claro
- [ ] Música de fundo presente mas discreta
- [ ] Motion graphics aparecem nos momentos certos
- [ ] Textos em francês sem erros
- [ ] Resolução 1920x1080
- [ ] Arquivo MP4 com tamanho razoável (< 2GB)

### ETAPA 10 — ENTREGA
Entregue ao usuário:
1. **MP4 final** pronto para upload: `saida/<nome_episodio>/<nome>_final.mp4`
2. **Roteiro completo** em francês: `saida/<nome_episodio>/roteiro.txt`
3. **Título do vídeo** em francês (otimizado SEO YouTube)
4. **Descrição do vídeo** em francês com: resumo, timestamps/chapitres, fontes citadas, CTA
5. **5 tags** em francês para YouTube
6. **Créditos** das cenas: `saida/<nome_episodio>/creditos_pexels.txt`
7. **Sugestão de thumbnail**: descrição do que a thumbnail deve conter

## Variáveis de Ambiente Necessárias
- `DARK_PLANNER_API_URL` — endpoint da API Dark Planner
- `DARK_PLANNER_API_KEY` — chave da API Dark Planner
- `PEXELS_API_KEY` — chave da API Pexels

## Notas
- Se uma API falhar, informe o usuário e sugira alternativa
- Sempre salve progresso intermediário (roteiro antes de gerar áudio, etc.)
- Use `saida/<nome_episodio>/` como pasta de trabalho para cada episódio
- Commit e push ao final de cada etapa importante
