import type { Metadata } from 'next';
export const metadata: Metadata = { title: 'Cutting Edge v2.0', description: 'AI Video Editor' };
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl">
      <body style={{ margin: 0, background: '#09090b', color: 'white', fontFamily: 'Inter,Vazirmatn,system-ui,sans-serif' }}>
        {children}
      </body>
    </html>
  );
}
