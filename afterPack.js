const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

module.exports = async function(context) {
  const appOutDir = context.appOutDir;
  const resourcesDir = path.join(appOutDir, 'Contents', 'Resources');
  const archValue = typeof context.arch === 'number'
    ? context.arch
    : typeof context.arch === 'string'
      ? context.arch
      : (context.arch && context.arch.name) ? context.arch.name : process.arch;
  const sourceVenvName = archValue === 'x64' || archValue === 1 ? 'venv-embedded-x64' : 'venv-embedded';
  const sourceVenv = path.resolve(__dirname, sourceVenvName);
  const destVenv = path.join(resourcesDir, 'venv-embedded');

  if (!fs.existsSync(sourceVenv)) {
    throw new Error(`afterPack: source venv not found at ${sourceVenv}`);
  }

  if (fs.existsSync(destVenv)) {
    await fs.promises.rm(destVenv, { recursive: true, force: true });
  }

  execFileSync('ditto', ['-V', sourceVenv, destVenv]);
  console.log(`afterPack: copied venv from ${sourceVenv} to ${destVenv}`);
};
