#!/usr/bin/env node
const { spawn } = require("child_process");
const path = require("path");

const script = path.join(__dirname, "mcp_server.py");
const child = spawn("python", [script], { stdio: "inherit" });

process.on("SIGINT", () => { child.kill("SIGINT"); process.exit(0); });
process.on("SIGTERM", () => { child.kill("SIGTERM"); process.exit(0); });
child.on("exit", (code) => process.exit(code));
