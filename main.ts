// news-image-20261120 v4 — "Friday 20 November 2026 — One Image".
// The entry is the PNG beside this file (drawn by draw_v4.py, 1024x1024,
// deterministic). This program copies it to the grader's output directory
// so the judge sees exactly those bytes. Node standard library only.
//
// Local check:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(
  new URL('./entry.png', import.meta.url),
  join(outDir, 'entry.png'),
);
