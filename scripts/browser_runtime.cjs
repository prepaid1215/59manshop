const path = require('path');
let playwright;
try { playwright = require('playwright'); }
catch (error) {
  const bundled = path.join(process.env.USERPROFILE || process.env.HOME || '', '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright');
  playwright = require(process.env.PLAYWRIGHT_MODULE || bundled);
}
module.exports = playwright;
