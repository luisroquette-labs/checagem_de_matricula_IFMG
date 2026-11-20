const fs = require('node:fs');
const acorn = require('acorn');

const source = fs.readFileSync(0, 'utf8');
const lines = [];
acorn.parse(source, {
  ecmaVersion: 'latest',
  locations: true,
  onComment: (_block, _text, _start, _end, start) => lines.push(start.line),
});
process.stdout.write(JSON.stringify(lines));
