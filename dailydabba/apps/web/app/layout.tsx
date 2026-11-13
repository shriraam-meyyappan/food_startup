import type { ReactNode } from 'react';
import './globals.css';
export const metadata = { title: 'DailyDabba — A little taste of home', description: 'Everyday Indian meals and meal subscriptions. A little taste of home.' };
export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
