#!/usr/bin/env python3
"""Gera vídeos automaticamente para canais dark.

Fluxo:
  1. Áudio da narração: baixado pela API do Dark Planner (ou um arquivo local).
  2. Cenas: vídeos de banco de imagens baixados pela API do Pexels.
  3. Montagem: ffmpeg corta, padroniza em 1920x1080 e junta tudo com o áudio.

Uso:
  python3 gerar_video.py projetos/exemplo.json
  python3 gerar_video.py projetos/exemplo.json --audio narracao.mp3

Variáveis de ambiente (ou arquivo .env na mesma pasta):
  PEXELS_API_KEY          chave da API do Pexels (obrigatória)
  DARK_PLANNER_API_URL    endpoint da API do Dark Planner que devolve o áudio
  DARK_PLANNER_API_KEY    chave da API do Dark Planner
"""

import argparse
import json
import os
import random
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request
from pathlib import Path

PASTA_BASE = Path(__file__).resolve().parent
LARGURA, ALTURA, FPS = 1920, 1080, 30
USER_AGENT = "gerador-videos-dark/1.0"


def carregar_env():
    arquivo = PASTA_BASE / ".env"
    if not arquivo.exists():
        return
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        linha = linha.strip()
        if not linha or linha.startswith("#") or "=" not in linha:
            continue
        chave, valor = linha.split("=", 1)
        os.environ.setdefault(chave.strip(), valor.strip().strip('"').strip("'"))


def requisicao(url, headers=None, dados=None):
    headers = {"User-Agent": USER_AGENT, **(headers or {})}
    req = urllib.request.Request(url, data=dados, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read(), resp.headers.get("Content-Type", "")


def baixar_arquivo(url, destino, headers=None):
    conteudo, _ = requisicao(url, headers)
    Path(destino).write_bytes(conteudo)
    return destino


def rodar(cmd):
    resultado = subprocess.run(cmd, capture_output=True, text=True)
    if resultado.returncode != 0:
        sys.exit(f"Erro ao executar {cmd[0]}:\n{resultado.stderr[-2000:]}")
    return resultado.stdout


def duracao(arquivo):
    saida = rodar(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                   "-of", "default=nw=1:nk=1", str(arquivo)])
    return float(saida.strip())


# ---------------------------------------------------------------- Dark Planner

def baixar_audio_dark_planner(projeto, destino):
    """Pede a narração à API do Dark Planner e salva em `destino`.

    O formato exato da requisição depende da documentação do Dark Planner.
    Aqui enviamos o roteiro e a voz em JSON e aceitamos duas respostas:
    o próprio arquivo de áudio, ou um JSON com o link do áudio.
    """
    url = os.environ.get("DARK_PLANNER_API_URL")
    chave = os.environ.get("DARK_PLANNER_API_KEY")
    if not url or not chave:
        sys.exit("Defina DARK_PLANNER_API_URL e DARK_PLANNER_API_KEY, "
                 "ou passe um áudio pronto com --audio.")

    corpo = json.dumps({
        "text": projeto["roteiro"],
        "voice": projeto.get("voz", ""),
        "language": projeto.get("idioma", "de"),
    }).encode("utf-8")
    headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
    conteudo, tipo = requisicao(url, headers, corpo)

    if tipo.startswith("audio/") or tipo == "application/octet-stream":
        Path(destino).write_bytes(conteudo)
        return destino

    resposta = json.loads(conteudo)
    link = (resposta.get("audio_url") or resposta.get("url")
            or resposta.get("data", {}).get("audio_url"))
    if not link:
        sys.exit(f"Resposta inesperada do Dark Planner: {str(resposta)[:500]}")
    return baixar_arquivo(link, destino)


# ---------------------------------------------------------------------- Pexels

def buscar_videos_pexels(termo, chave, por_pagina=15):
    params = urllib.parse.urlencode({
        "query": termo, "orientation": "landscape", "size": "medium",
        "per_page": por_pagina,
    })
    conteudo, _ = requisicao(f"https://api.pexels.com/videos/search?{params}",
                             {"Authorization": chave})
    return json.loads(conteudo).get("videos", [])


def escolher_arquivo(video):
    """Escolhe a versão MP4 mais próxima de 1920x1080 sem passar muito disso."""
    candidatos = [f for f in video.get("video_files", [])
                  if f.get("file_type") == "video/mp4" and f.get("width")]
    if not candidatos:
        return None
    return min(candidatos, key=lambda f: abs(f["width"] - LARGURA))


def baixar_cenas(projeto, duracao_total, pasta, chave):
    termos = projeto["palavras_chave"]
    seg_por_cena = projeto.get("segundos_por_cena", 6)
    cenas, creditos, usados = [], [], set()

    resultados = {}
    for termo in termos:
        videos = buscar_videos_pexels(termo, chave)
        random.shuffle(videos)
        resultados[termo] = videos
        print(f"  Pexels: {len(videos)} vídeos para '{termo}'")

    # Alterna entre as palavras-chave para variar as cenas.
    while acumulado < duracao_total:
        algum = False
        for termo in termos:
            if acumulado >= duracao_total:
                break
            fila = resultados[termo]
            while fila and fila[0]["id"] in usados:
                fila.pop(0)
            if not fila:
                continue
            video = fila.pop(0)
            arquivo = escolher_arquivo(video)
            if not arquivo:
                continue
            usados.add(video["id"])
            destino = pasta / f"bruto_{len(cenas):03d}.mp4"
            baixar_arquivo(arquivo["link"], destino)
            dur = min(seg_por_cena, duracao(destino))
            cenas.append((destino, dur))
            creditos.append(f"{video['user']['name']} - {video['url']}")
            acumulado += dur
            algum = True
            print(f"  Cena {len(cenas)} baixada ({acumulado:.0f}/{duracao_total:.0f}s)")
        if not algum:
            sys.exit("Acabaram os vídeos do Pexels. Adicione mais palavras-chave.")
    return cenas, creditos


# -------------------------------------------------------------------- Montagem

def montar_video(cenas, audio, saida, pasta_temp, musica=None, volume_musica=0.08):
    """Padroniza cada cena, junta todas e coloca a narração por cima."""
    padronizadas = []
    filtro = (f"scale={LARGURA}:{ALTURA}:force_original_aspect_ratio=increase,"
              f"crop={LARGURA}:{ALTURA},fps={FPS},format=yuv420p,setsar=1")
    for i, (arquivo, dur) in enumerate(cenas):
        destino = pasta_temp / f"cena_{i:03d}.mp4"
        rodar(["ffmpeg", "-y", "-i", str(arquivo), "-t", f"{dur:.3f}", "-an",
               "-vf", filtro, "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
               str(destino)])
        padronizadas.append(destino)

    lista = pasta_temp / "lista.txt"
    lista.write_text("".join(f"file '{p.resolve()}'\n" for p in padronizadas))

    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(lista), "-i", str(audio)]
    if musica:
        cmd += ["-stream_loop", "-1", "-i", str(musica), "-filter_complex",
                f"[2:a]volume={volume_musica}[m];[1:a][m]amix=inputs=2:duration=first[a]",
                "-map", "0:v", "-map", "[a]"]
    else:
        cmd += ["-map", "0:v", "-map", "1:a"]
    cmd += ["-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-t", f"{duracao(audio):.3f}",
            "-movflags", "+faststart", str(saida)]
    rodar(cmd)
    return saida


# ------------------------------------------------------------------------ main

def main():
    parser = argparse.ArgumentParser(description="Gera vídeos automáticos para canais dark.")
    parser.add_argument("projeto", help="arquivo JSON do projeto")
    parser.add_argument("--audio", help="usar este áudio em vez de baixar do Dark Planner")
    parser.add_argument("--musica", help="música de fundo opcional (fica em volume baixo)")
    parser.add_argument("--manter-temp", action="store_true", help="não apagar arquivos temporários")
    args = parser.parse_args()

    carregar_env()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg não encontrado. Instale antes de continuar.")
    chave_pexels = os.environ.get("PEXELS_API_KEY")
    if not chave_pexels:
        sys.exit("Defina PEXELS_API_KEY (https://www.pexels.com/api/).")

    projeto = json.loads(Path(args.projeto).read_text(encoding="utf-8"))
    nome = projeto.get("nome") or Path(args.projeto).stem
    pasta_saida = PASTA_BASE / "saida" / nome
    pasta_temp = pasta_saida / "temp"
    pasta_temp.mkdir(parents=True, exist_ok=True)

    print("1/3 Áudio da narração")
    if args.audio:
        audio = Path(args.audio)
    else:
        audio = baixar_audio_dark_planner(projeto, pasta_temp / "narracao.mp3")
    dur_audio = duracao(audio)
    print(f"  Duração: {dur_audio:.0f}s")

    print("2/3 Cenas do Pexels")
    cenas, creditos = baixar_cenas(projeto, dur_audio, pasta_temp, chave_pexels)

    print("3/3 Montagem")
    saida = montar_video(cenas, audio, pasta_saida / f"{nome}.mp4", pasta_temp,
                         musica=args.musica)
    (pasta_saida / "creditos_pexels.txt").write_text(
        "Vídeos: Pexels (https://www.pexels.com)\n" + "\n".join(creditos) + "\n",
        encoding="utf-8")

    if not args.manter_temp:
        shutil.rmtree(pasta_temp, ignore_errors=True)
    print(f"Pronto: {saida}")


if __name__ == "__main__":
    main()
