const { execSync } = require("child_process");
const path = require("path");

const req = path.join(__dirname, "requirements.txt");
try {
  execSync(`pip install -r "${req}"`, { stdio: "inherit" });
} catch (e) {
  console.warn("[prompt-optimizer-mcp] Python dependencies not installed. Run: pip install -r requirements.txt");
}
