# Histórico — Sessão 1 (17-18 Out 2026)

## O que foi discutido e decidido

### 1. Pesquisa de nicho para público alemão
- Identificamos os melhores nichos para YouTube na Alemanha
- CPM alto: finanças, carros, DIY, documentários
- Recomendação: documentários sem aparecer (faceless)

### 2. Teste de produção automática de vídeo
- Criamos o pipeline completo: roteiro → narração → cenas → montagem → motion graphics
- **Vídeo piloto produzido**: "Paris ville poubelle" (55s, 1080p)
  - Narração gerada pelo vidIQ (voz Daniel, ~11 créditos)
  - 14 cenas baixadas do Mixkit (gratuito, sem direitos autorais)
  - Montagem com ffmpeg (1920x1080, 30fps)
  - Motion graphics adicionados: títulos, dados de impacto, hashtag, barra de progresso

### 3. Decisão do canal: público FRANCÊS (não alemão)
- **Canal**: "Les Contradictions de la France"
- **Público**: franceses, conteúdo em francês
- **Conceito**: contradições da França — imagem oficial vs realidade
- **Temas**: economia, geografia, lugares esquecidos, cultura, costumes, infraestrutura

### 4. Estrutura dos vídeos definida
- Hook (30s) → Contexto bonito (3min) → Contradição (15min) → Clímax (3min) → Reflexão + CTA (2min)
- Narrador editorial que comenta e questiona
- Dados concretos com fontes
- Conforme políticas de monetização YouTube

### 5. Temporada 1 planejada (20 episódios)
- Ver lista completa em ESTRATEGIA_CANAL.md

### 6. Decisões técnicas
- Voz: vidIQ (Daniel) para trechos curtos / ElevenLabs ou Dark Planner para vídeos longos
- Cenas: Mixkit e Pexels (gratuitos, sem royalty)
- Música: Pixabay Music ou Mixkit Music (livre, sem atribuição, sem direitos autorais)
- Motion graphics: Montserrat font, paleta azul escuro + vermelho francês + branco
- Duração: 20-60 minutos por episódio

### 7. APIs a configurar (pendente)
- DARK_PLANNER_API_KEY + DARK_PLANNER_API_URL
- PEXELS_API_KEY
- ELEVENLABS_API_KEY (opcional)
- Configurar em: menu do ambiente → Editar → Network secrets

## Arquivos criados nesta sessão
- `gerar_video.py` — gerador automático de vídeos
- `adicionar_graficos.py` — script de motion graphics
- `fonts/Montserrat-*.ttf` — fontes para os gráficos
- `projetos/exemplo.json` — template de projeto de vídeo
- `.env.exemplo` — template de variáveis de ambiente
- `.gitignore` — ignora .env e pasta saida/
- `canal_contradictions/ESTRATEGIA_CANAL.md` — estratégia + 20 episódios
- `canal_contradictions/BRIEFING.md` — briefing completo para continuidade
- `canal_contradictions/HISTORICO_SESSAO_01.md` — este arquivo

## Próximos passos
1. Configurar as chaves de API no ambiente
2. Escolher o primeiro episódio para roteiro completo em francês
3. Definir narração: vidIQ, ElevenLabs ou Dark Planner
4. Produzir o primeiro vídeo de 20 minutos
