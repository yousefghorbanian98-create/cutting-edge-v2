import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = { title: 'Cutting Edge v2.0', description: 'AI Video Editor' };

/**
 * Root layout — S-007.
 *
 * The background/colour/font used to be an inline `style` on <body>, which
 * proved nothing about the (then non-existent) stylesheet. They now live in
 * `globals.css` (@layer base), so the styling test can assert the *computed*
 * style comes from CSS while `body.style.backgroundColor` stays empty.
 */
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl">
      <body>{children}</body>
    </html>
  );
}
