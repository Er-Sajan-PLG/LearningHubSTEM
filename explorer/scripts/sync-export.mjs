import { copyFileSync, existsSync, mkdirSync } from 'fs';
import { join, resolve } from 'path';

const EXPLORER_ROOT = resolve(import.meta.dirname, '..');
const LHS_ROOT = resolve(EXPLORER_ROOT, '..');
const SOURCE = join(LHS_ROOT, 'exports', 'knowledge.json');
const TARGET_DIR = join(EXPLORER_ROOT, 'public', 'exports');
const TARGET = join(TARGET_DIR, 'knowledge.json');

if (!existsSync(SOURCE)) {
  console.error(`✗ Knowledge export not found: ${SOURCE}`);
  process.exit(1);
}

mkdirSync(TARGET_DIR, { recursive: true });
copyFileSync(SOURCE, TARGET);
console.log(`✓ Copied ${SOURCE} → ${TARGET}`);
