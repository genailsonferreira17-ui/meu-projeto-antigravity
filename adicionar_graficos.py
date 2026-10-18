#!/usr/bin/env python3
"""Adiciona motion graphics (textos animados, barras, dados) ao vídeo base."""

import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent
FONT_BOLD = str(BASE / "fonts/Montserrat-ExtraBold.ttf")
FONT_REG = str(BASE / "fonts/Montserrat-Regular.ttf")
# Fallback to Inter if Montserrat missing
FONT_INTER = "/usr/share/fonts/opentype/inter/Inter-Bold.otf"
FONT_INTER_REG = "/usr/share/fonts/opentype/inter/Inter-Regular.otf"


def esc(text):
    """Escape text for ffmpeg drawtext."""
    return text.replace("'", "'\\''").replace(":", "\\:").replace("%", "%%")


def fade(t_in, t_out, dur_fade=0.4):
    """Generate alpha expression with fade in/out."""
    return (f"if(lt(t,{t_in}),0,"
            f"if(lt(t,{t_in + dur_fade}),(t-{t_in})/{dur_fade},"
            f"if(lt(t,{t_out - dur_fade}),1,"
            f"if(lt(t,{t_out}),({t_out}-t)/{dur_fade},0))))")


def slide_up(y_final, t_in, dur_slide=0.5):
    """Y expression: slides up from below."""
    return f"if(lt(t,{t_in}),{y_final + 80},{y_final + 80} - min(80, 80*(t-{t_in})/{dur_slide}))"


def build_filters():
    """Build the complete ffmpeg filter chain.

    drawtext uses w/h for video dimensions.
    drawbox uses iw/ih for video dimensions.
    We use absolute pixels (1920x1080) in drawtext to avoid issues.
    """
    W, H = 1920, 1080
    filters = []

    # (sem barras permanentes em cima/baixo — visual limpo)

    # ── 2. TITLE CARD: "PARIS" (0-3.5s) ──
    filters.append(
        "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.55:t=fill:"
        "enable='between(t,0,3.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_BOLD}:text='{esc('P A R I S')}':"
        f"fontsize=120:fontcolor=white:"
        f"x=(w-text_w)/2:y=420:"
        f"alpha='{fade(0.3, 3.5, 0.6)}':"
        f"enable='between(t,0,3.5)'"
    )
    filters.append(
        "drawbox=x=810:y=550:w=300:h=3:color=0xE63946@0.9:t=fill:"
        "enable='between(t,0.5,3.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_REG}:text='{esc('Die Stadt der Liebe')}':"
        f"fontsize=36:fontcolor=0xCCCCCC:"
        f"x=(w-text_w)/2:y=580:"
        f"alpha='{fade(0.8, 3.5, 0.5)}':"
        f"enable='between(t,0.5,3.5)'"
    )

    # ── 3. LOWER THIRD: Eiffelturm (3.5-8s) ──
    filters.append(
        "drawbox=x=80:y=850:w=6:h=100:color=0xE63946:t=fill:"
        "enable='between(t,3.8,7.8)'"
    )
    filters.append(
        "drawbox=x=96:y=845:w=800:h=110:color=black@0.65:t=fill:"
        "enable='between(t,3.8,7.8)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_BOLD}:text='{esc('DER EIFFELTURM')}':"
        f"fontsize=46:fontcolor=white:"
        f"x=115:y=855:"
        f"alpha='{fade(3.8, 7.8)}':"
        f"enable='between(t,3.8,7.8)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_REG}:"
        f"text='{esc('Champs-Élysées · Louvre · Montmartre')}':"
        f"fontsize=28:fontcolor=0xAAAAAA:"
        f"x=115:y=910:"
        f"alpha='{fade(4.2, 7.8)}':"
        f"enable='between(t,4.0,7.8)'"
    )

    # ── 4. BIG STAT: 30 Millionen Touristen (8-14s) ──
    filters.append(
        "drawbox=x=660:y=450:w=600:h=180:color=black@0.7:t=fill:"
        "enable='between(t,8.5,13.5)'"
    )
    filters.append(
        "drawbox=x=660:y=450:w=600:h=4:color=0xE63946:t=fill:"
        "enable='between(t,8.5,13.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_BOLD}:text='{esc('30 MILLIONEN')}':"
        f"fontsize=64:fontcolor=0xE63946:"
        f"x=(w-text_w)/2:y=475:"
        f"alpha='{fade(8.8, 13.5, 0.5)}':"
        f"enable='between(t,8.5,13.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_REG}:text='{esc('TOURISTEN JÄHRLICH')}':"
        f"fontsize=28:fontcolor=0xDDDDDD:"
        f"x=(w-text_w)/2:y=560:"
        f"alpha='{fade(9.2, 13.5, 0.5)}':"
        f"enable='between(t,9.0,13.5)'"
    )

    # ── 5. TRANSITION TEXT: "Doch..." (14-19s) ──
    filters.append(
        "drawbox=x=0:y=890:w=iw:h=100:color=black@0.6:t=fill:"
        "enable='between(t,14.5,19)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_REG}:"
        f"text='{esc('Doch abseits der Postkartenmotive...')}':"
        f"fontsize=40:fontcolor=white:"
        f"x=(w-text_w)/2:y=915:"
        f"alpha='{fade(14.5, 19)}':"
        f"enable='between(t,14.5,19)'"
    )

    # ── 6. IMPACT: "BERGE VON MÜLL" (20-26s) ──
    filters.append(
        "drawbox=x=0:y=490:w=iw:h=100:color=0xE63946@0.85:t=fill:"
        "enable='between(t,20.5,25.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_BOLD}:text='{esc('BERGE VON MÜLL')}':"
        f"fontsize=68:fontcolor=white:"
        f"x=(w-text_w)/2:y=500:"
        f"alpha='{fade(20.8, 25.5, 0.3)}':"
        f"enable='between(t,20.5,25.5)'"
    )

    # ── 7. LOWER THIRD: Ratten (26-31s) ──
    filters.append(
        "drawbox=x=80:y=850:w=6:h=100:color=0xE63946:t=fill:"
        "enable='between(t,26.5,30.5)'"
    )
    filters.append(
        "drawbox=x=96:y=845:w=750:h=110:color=black@0.65:t=fill:"
        "enable='between(t,26.5,30.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_BOLD}:text='{esc('RATTEN AUF DEN GEHWEGEN')}':"
        f"fontsize=44:fontcolor=white:"
        f"x=115:y=855:"
        f"alpha='{fade(26.5, 30.5)}':"
        f"enable='between(t,26.5,30.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_REG}:"
        f"text='{esc('Mülleimer tagelang unberührt')}':"
        f"fontsize=26:fontcolor=0xAAAAAA:"
        f"x=115:y=910:"
        f"alpha='{fade(27, 30.5)}':"
        f"enable='between(t,26.8,30.5)'"
    )

    # ── 8. STAT BOX: Streik (31-36s) ──
    filters.append(
        "drawbox=x=635:y=460:w=650:h=160:color=black@0.7:t=fill:"
        "enable='between(t,31.5,35.5)'"
    )
    filters.append(
        "drawbox=x=635:y=460:w=650:h=4:color=0xE63946:t=fill:"
        "enable='between(t,31.5,35.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_BOLD}:"
        f"text='{esc('STREIK DER MÜLLABFUHR')}':"
        f"fontsize=44:fontcolor=0xE63946:"
        f"x=(w-text_w)/2:y=480:"
        f"alpha='{fade(31.8, 35.5, 0.4)}':"
        f"enable='between(t,31.5,35.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_REG}:"
        f"text='{esc('Das Problem verschärft sich regelmäßig')}':"
        f"fontsize=22:fontcolor=0xCCCCCC:"
        f"x=(w-text_w)/2:y=545:"
        f"alpha='{fade(32.2, 35.5, 0.4)}':"
        f"enable='between(t,32,35.5)'"
    )

    # ── 9. SOCIAL MEDIA style (36-41s) ──
    filters.append(
        "drawbox=x=710:y=480:w=500:h=120:color=0x1a1a2e@0.8:t=fill:"
        "enable='between(t,36.5,40.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_BOLD}:"
        f"text='{esc('#ParisIstDreckig')}':"
        f"fontsize=42:fontcolor=0x1DA1F2:"
        f"x=(w-text_w)/2:y=495:"
        f"alpha='{fade(36.8, 40.5, 0.3)}':"
        f"enable='between(t,36.5,40.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_REG}:"
        f"text='{esc('Schockierte Touristen in sozialen Medien')}':"
        f"fontsize=18:fontcolor=0x999999:"
        f"x=(w-text_w)/2:y=550:"
        f"alpha='{fade(37.2, 40.5)}':"
        f"enable='between(t,37,40.5)'"
    )

    # ── 10. GOVERNMENT STAT (41-46s) ──
    filters.append(
        "drawbox=x=610:y=450:w=700:h=180:color=black@0.7:t=fill:"
        "enable='between(t,41.5,46)'"
    )
    filters.append(
        "drawbox=x=610:y=450:w=700:h=4:color=0xE63946:t=fill:"
        "enable='between(t,41.5,46)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_BOLD}:"
        f"text='{esc('MILLIONEN € INVESTIERT')}':"
        f"fontsize=48:fontcolor=white:"
        f"x=(w-text_w)/2:y=475:"
        f"alpha='{fade(41.8, 46, 0.4)}':"
        f"enable='between(t,41.5,46)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_REG}:"
        f"text='{esc('DAS PROBLEM BLEIBT')}':"
        f"fontsize=28:fontcolor=0xE63946:"
        f"x=(w-text_w)/2:y=555:"
        f"alpha='{fade(42.3, 46, 0.4)}':"
        f"enable='between(t,42,46)'"
    )

    # ── 11. CLOSING TITLE (48-55s) ──
    filters.append(
        "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.6:t=fill:"
        "enable='between(t,49,55.5)'"
    )
    filters.append(
        "drawbox=x=760:y=470:w=400:h=3:color=0xE63946:t=fill:"
        "enable='between(t,49.5,55.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_BOLD}:"
        f"text='{esc('DIE STADT DER LICHTER')}':"
        f"fontsize=52:fontcolor=white:"
        f"x=(w-text_w)/2:y=490:"
        f"alpha='{fade(49.5, 55.5, 0.6)}':"
        f"enable='between(t,49,55.5)'"
    )
    filters.append(
        f"drawtext=fontfile={FONT_BOLD}:"
        f"text='{esc('VERSINKT IM DRECK')}':"
        f"fontsize=52:fontcolor=0xE63946:"
        f"x=(w-text_w)/2:y=550:"
        f"alpha='{fade(50, 55.5, 0.6)}':"
        f"enable='between(t,49.5,55.5)'"
    )
    filters.append(
        "drawbox=x=760:y=620:w=400:h=3:color=0xE63946:t=fill:"
        "enable='between(t,50,55.5)'"
    )

    # ── TOP BAR: thin red progress line ──
    filters.append(
        "drawbox=x=0:y=0:w='iw*(t/55.5)':h=3:color=0xE63946:t=fill:"
        "enable='between(t,0,55.5)'"
    )

    return ",".join(filters)


def main():
    video_in = BASE / "saida/paris_lixo/paris_lixo.mp4"
    video_out = BASE / "saida/paris_lixo/paris_lixo_graficos.mp4"

    if not video_in.exists():
        sys.exit(f"Vídeo base não encontrado: {video_in}")

    filtro = build_filters()

    cmd = [
        "ffmpeg", "-y", "-i", str(video_in),
        "-vf", filtro,
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(video_out),
    ]

    print(f"Renderizando motion graphics...")
    print(f"Filtros: {len(filtro)} caracteres")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("STDERR:", result.stderr[-3000:])
        sys.exit(1)

    print(f"Pronto: {video_out}")
    print(f"Tamanho: {video_out.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
