import express from "express";
import cors from "cors";
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

dotenv.config({ path: path.resolve(__dirname, "..", ".env") });

const app = express();
const port = process.env.PORT ? Number(process.env.PORT) : 3000;

app.use(cors());
app.use(express.json());

/**
 * Health check endpoint for the chat service.
 * @returns {{status: string, service: string, version: string}}
 */
app.get("/health", (_req, res) => {
  res.json({
    status: "ok",
    service: "docforge-chat",
    version: "0.1.0",
  });
});

app.get("/", (_req, res) => {
  res.json({ message: "DocForge chat service is running. Use /health to check status." });
});

app.listen(port, () => {
  // eslint-disable-next-line no-console
  console.log(`DocForge chat service listening on http://localhost:${port}`);
});
