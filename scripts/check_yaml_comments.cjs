const fs = require('node:fs');
const yaml = require('yaml');

const source = fs.readFileSync(0, 'utf8');
const lines = [];
function visit(token) {
  if (!token || typeof token !== 'object') return;
  if (token.type === 'comment') lines.push(source.slice(0, token.offset).split('\n').length);
  for (const value of Object.values(token)) {
    if (Array.isArray(value)) value.forEach(visit);
    else if (value && typeof value === 'object') visit(value);
  }
}
for (const token of new yaml.Parser().parse(source)) visit(token);
process.stdout.write(JSON.stringify(lines));
