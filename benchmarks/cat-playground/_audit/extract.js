const fs = require('fs');
const path = require('path');
const baseDir = path.resolve(__dirname, '..');
const html = fs.readFileSync(path.join(baseDir, 'index.html'), 'utf8');
const re = /<script\b[^>]*>([\s\S]*?)<\/script>/gi;
let match;
const inline = [];
const allSrc = [];
while ((match = re.exec(html)) !== null) {
  const tag = match[0];
  const srcMatch = tag.match(/\bsrc\s*=\s*["']([^"']+)["']/i);
  if (srcMatch) {
    allSrc.push(srcMatch[1]);
  } else {
    inline.push(match[1]);
  }
}
fs.writeFileSync(path.join(__dirname, 'inline.js'), inline.join('\n'));
fs.writeFileSync(path.join(__dirname, 'srcs.json'), JSON.stringify({allSrc, inlineCount: inline.length, inlineBytes: inline.join('\n').length}, null, 2));
console.log('SRC_TAGS:' + JSON.stringify(allSrc));
console.log('INLINE_BLOCKS:' + inline.length);
console.log('INLINE_BYTES:' + inline.join('\n').length);
