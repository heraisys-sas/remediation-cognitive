const fs = require("node:fs");
const path = require("node:path");
module.exports = function sourceInterface() {
  const root = path.resolve(__dirname, "../frontend");
  return [...fs.readFileSync(path.join(root, "index.html"), "utf8")
    .matchAll(/<script src="(src\/[^"?]+)(?:\?[^"]*)?"/g)]
    .map(match => fs.readFileSync(path.join(root, match[1]), "utf8")).join("\n");
};
