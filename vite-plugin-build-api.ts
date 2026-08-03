/**
 * Vite plugin: POST /api/build-project endpoint.
 * Receives category overrides, deleted pipelines, and category map from the
 * frontend, writes them to src/data/*.json, then runs `npm run build`.
 */
import type { Plugin, ViteDevServer } from "vite";
import { exec } from "child_process";
import { writeFileSync, mkdirSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import type { IncomingMessage, ServerResponse } from "http";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = resolve(__dirname, "src/data");

interface BuildRequestBody {
  categoryOverrides?: Record<string, unknown>;
  deletedPipelines?: string[];
  categoryMap?: Record<string, string>;
}

function ensureDataDir(): void {
  mkdirSync(DATA_DIR, { recursive: true });
}

function writeJson(filename: string, data: unknown): void {
  writeFileSync(resolve(DATA_DIR, filename), JSON.stringify(data, null, 2) + "\n", "utf-8");
}

function parseBody(req: IncomingMessage): Promise<string> {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk: Buffer) => {
      body += chunk.toString();
      if (body.length > 1_000_000) {
        req.destroy();
        reject(new Error("Payload too large"));
      }
    });
    req.on("end", () => resolve(body));
    req.on("error", reject);
  });
}

function sendJson(res: ServerResponse, status: number, data: unknown): void {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.end(JSON.stringify(data));
}

function isLocalhost(req: IncomingMessage): boolean {
  const host = req.headers.host || "";
  const addr = (req.socket?.remoteAddress || "").replace(/^::ffff:/, "");
  return (
    addr === "127.0.0.1" ||
    addr === "::1" ||
    addr === "localhost" ||
    host.startsWith("localhost") ||
    host.startsWith("127.0.0.1")
  );
}

async function handleBuildApi(req: IncomingMessage, res: ServerResponse): Promise<void> {
  // Only POST
  if (req.method !== "POST") {
    sendJson(res, 405, { error: "Method not allowed. Use POST." });
    return;
  }

  // Only localhost
  if (!isLocalhost(req)) {
    sendJson(res, 403, { error: "Forbidden: localhost access only." });
    return;
  }

  // Parse body
  let body: BuildRequestBody;
  try {
    const raw = await parseBody(req);
    body = JSON.parse(raw);
  } catch {
    sendJson(res, 400, { error: "Invalid JSON body." });
    return;
  }

  // Write overrides
  try {
    ensureDataDir();

    if (body.categoryOverrides) {
      writeJson("category-overrides.json", body.categoryOverrides);
    }
    if (body.deletedPipelines) {
      writeJson("deleted-pipelines.json", body.deletedPipelines);
    }
    if (body.categoryMap) {
      writeJson("category-map.json", body.categoryMap);
    }
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    sendJson(res, 500, { error: `Failed to write override files: ${message}` });
    return;
  }

  // Run build
  exec(
    "npm run build",
    {
      cwd: __dirname,
      env: { ...process.env, Path: `C:\\Program Files\\nodejs;${process.env.Path || ""}` },
      maxBuffer: 10 * 1024 * 1024,
      timeout: 300_000,
    },
    (error, stdout, stderr) => {
      if (error) {
        sendJson(res, 500, {
          success: false,
          output: stdout,
          error: stderr || error.message,
        });
      } else {
        sendJson(res, 200, {
          success: true,
          output: stdout,
          error: stderr || undefined,
        });
      }
    }
  );
}

export function buildApiPlugin(): Plugin {
  return {
    name: "vite-plugin-build-api",
    configureServer(server: ViteDevServer) {
      server.middlewares.use("/api/build-project", (req, res) => {
        handleBuildApi(req, res);
      });
    },
  };
}
