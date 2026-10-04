import { readFileSync, existsSync, mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const BASE = "https://app.darkplanner.com.br/api/v1/audio";
const POLL_MS = 10_000; // limite da API: 10 requisições/min
const MAX_WAIT_MS = 30 * 60_000;

const loadEnv = () => {
  if (!existsSync(".env")) return;
  for (const line of readFileSync(".env", "utf8").split(/\r?\n/)) {
    const m = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*?)\s*$/);
    if (m && !(m[1] in process.env)) process.env[m[1]] = m[2].replace(/^["']|["']$/g, "");
  }
};

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

const api = async (path, options = {}) => {
  const key = process.env.DARKPLANNER_API_KEY;
  if (!key) throw new Error("Defina DARKPLANNER_API_KEY no arquivo .env");
  const res = await fetch(BASE + path, {
    ...options,
    headers: { "X-API-Key": key, "Content-Type": "application/json" },
  });
  if (res.status === 429) {
    const wait = Number(res.headers.get("Retry-After") ?? 30);
    console.error(`Limite atingido (429). Aguardando ${wait}s...`);
    await sleep(wait * 1000);
    return api(path, options);
  }
  const body = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(`HTTP ${res.status}: ${JSON.stringify(body)}`);
  return body;
};

const flag = (args, name, fallback) => {
  const i = args.indexOf(`--${name}`);
  return i === -1 ? fallback : args[i + 1];
};

const commands = {
  async voices() {
    const { voices } = await api("/voices");
    for (const v of voices) console.log(`${v.id}\t${v.name}\t${v.gender}\t${v.preview_url}`);
  },

  async usage() {
    console.log(await api("/usage"));
  },

  async generate(args) {
    const [textFile, voiceId] = args;
    if (!textFile || !voiceId) {
      throw new Error("Uso: generate <arquivo.txt> <voice_id> [--title nome] [--speed 1.0] [--words 8]");
    }
    const body = { text: readFileSync(textFile, "utf8"), voice_id: voiceId };
    const title = flag(args, "title");
    const speed = flag(args, "speed");
    const words = flag(args, "words");
    if (title) body.title = title;
    if (speed) body.speed = Number(speed);
    if (words) body.subtitle_words = Number(words);

    const { job_id } = await api("/generate", { method: "POST", body: JSON.stringify(body) });
    console.log(`Job criado: ${job_id}`);

    const start = Date.now();
    for (;;) {
      await sleep(POLL_MS);
      const { status } = await api(`/status/${job_id}`);
      console.log(`Status: ${status}`);
      if (status === "completed") break;
      if (!["processing", "queued", "pending"].includes(status)) {
        throw new Error(`Job terminou com status inesperado: ${status}`);
      }
      if (Date.now() - start > MAX_WAIT_MS) throw new Error("Tempo limite excedido");
    }

    const d = await api(`/download/${job_id}`);
    const dir = join("public", "audio", job_id);
    mkdirSync(dir, { recursive: true });
    const files = {
      "audio.mp3": d.audio_url,
      "legenda.srt": d.srt_url,
      "srtsyncpalavra.srt": d.srt_palavra_url,
      "srtsynctempo.srt": d.srt_tempo_url,
    };
    for (const [name, url] of Object.entries(files)) {
      if (!url) continue;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Falha ao baixar ${name}: HTTP ${res.status}`);
      writeFileSync(join(dir, name), Buffer.from(await res.arrayBuffer()));
      console.log(`Salvo: ${join(dir, name)}`);
    }
  },
};

loadEnv();
const [cmd, ...rest] = process.argv.slice(2);
if (!commands[cmd]) {
  console.log("Comandos: voices | usage | generate <arquivo.txt> <voice_id> [--title] [--speed] [--words]");
  process.exit(1);
}
commands[cmd](rest).catch((e) => {
  console.error(e.message);
  process.exit(1);
});
