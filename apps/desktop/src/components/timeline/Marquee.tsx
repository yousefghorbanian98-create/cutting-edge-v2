'use client';

export function Marquee({
  rect,
}: {
  rect: { x: number; y: number; width: number; height: number } | null;
}) {
  if (!rect) return null;
  return (
    <div
      data-testid="marquee"
      className="pointer-events-none absolute top-8 z-10 border border-info bg-info/20"
      style={{
        transform: `translate3d(calc(8rem + ${Math.min(rect.x, rect.x + rect.width)}px), 0, 0)`,
        width: Math.abs(rect.width),
        height: 48,
      }}
    />
  );
}
