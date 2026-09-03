import './globals.css';

export const metadata = { title: 'Cutting Edge', description: 'AI powered video workspace' };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body>{children}</body></html>;
}
