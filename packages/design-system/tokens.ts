/**
 * Design tokens — S-007.
 *
 * This object is the JS/TS side (framer-motion springs, inline values). The CSS
 * side is the `@theme` block in `apps/desktop/src/app/globals.css`, which is
 * what generates the Tailwind utilities. **Keep the two in sync**: `cssTheme`
 * below lists the `@theme` variable name for every colour/typography token so a
 * reviewer (or the S-008 static gate) can diff them mechanically.
 */
export const designTokens = {
  colors: {
    primary: {
      50:'#eef2ff',100:'#e0e7ff',200:'#c7d2fe',300:'#a5b4fc',
      400:'#818cf8',500:'#6366f1',600:'#4f46e5',700:'#4338ca',
      800:'#3730a3',900:'#312e81',950:'#1e1b4b'
    },
    ai: { glow:'#8b5cf6', pulse:'#a78bfa', soft:'#c4b5fd', deep:'#6d28d9' },
    surface: {
      base:'#09090b', raised:'#18181b', overlay:'#27272a',
      border:'rgb(255 255 255 / 0.06)', hover:'rgb(255 255 255 / 0.04)'
    },
    success:'#10b981', warning:'#f59e0b', error:'#ef4444', info:'#3b82f6',
    muscle: { warm:'#f97316', hot:'#ef4444', cool:'#3b82f6', def:'#eab308' },
    energy: { low:'#22c55e', medium:'#eab308', high:'#f97316', peak:'#ef4444' }
  },
  typography: {
    sans: "'Inter Variable', 'Vazirmatn', system-ui, sans-serif",
    mono: "'JetBrains Mono', ui-monospace, monospace"
  },
  radius: { sm:'6px', md:'10px', lg:'16px', xl:'24px', full:'9999px' },
  motion: {
    spring: { type:'spring' as const, stiffness:300, damping:30 },
    smooth: { duration:0.3, ease:[0.25,0.1,0.25,1] }
  },
  shadows: {
    glow:'0 0 20px rgba(139,92,246,0.3)',
    card:'0 4px 24px rgba(0,0,0,0.4)'
  }
} as const;

/**
 * Token path → CSS custom property declared in the `@theme` block of
 * `apps/desktop/src/app/globals.css` (S-007).
 *
 * The `@theme` block is what actually generates Tailwind utilities, so this map
 * is the mechanical link between the TS tokens above and the CSS mirror. Every
 * entry must exist in both places; a token that is only here has no utility.
 */
export const cssTheme = {
  'colors.surface.base': '--color-surface-base',
  'colors.surface.raised': '--color-surface-raised',
  'colors.surface.overlay': '--color-surface-overlay',
  'colors.surface.border': '--color-surface-border',
  'colors.surface.hover': '--color-surface-hover',
  'colors.ai.glow': '--color-ai-glow',
  'colors.ai.pulse': '--color-ai-pulse',
  'colors.ai.soft': '--color-ai-soft',
  'colors.ai.deep': '--color-ai-deep',
  'colors.success': '--color-success',
  'colors.warning': '--color-warning',
  'colors.error': '--color-error',
  'colors.info': '--color-info',
  'colors.muscle.warm': '--color-muscle-warm',
  'colors.muscle.hot': '--color-muscle-hot',
  'colors.muscle.cool': '--color-muscle-cool',
  'colors.muscle.def': '--color-muscle-def',
  'colors.energy.low': '--color-energy-low',
  'colors.energy.medium': '--color-energy-medium',
  'colors.energy.high': '--color-energy-high',
  'colors.energy.peak': '--color-energy-peak',
  'typography.sans': '--font-sans',
  'typography.mono': '--font-mono',
  'radius.sm': '--radius-sm',
  'radius.md': '--radius-md',
  'radius.lg': '--radius-lg',
  'radius.xl': '--radius-xl'
} as const;
