import path from 'node:path';
import { defineConfig } from 'vitest/config';

export default defineConfig({
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') },
  },
  test: {
    environment: 'node',
    include: ['src/**/*.test.ts', 'tests/pngDiff.test.ts'],
    reporters: [
      'default',
      ['junit', { outputFile: path.resolve(__dirname, '../../reports/junit-visual.xml') }],
    ],
    coverage: {
      provider: 'v8',
      reporter: ['text'],
      include: ['src/domain/timeline.ts'],
      thresholds: {
        lines: 90,
      },
    },
  },
});
