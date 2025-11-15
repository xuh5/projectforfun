import './globals.css';
import Navigation from '../components/Navigation';
import { AppProviders } from '../components/AppProviders';
import { Inter, Poppins } from 'next/font/google';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const poppins = Poppins({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-poppins',
  display: 'swap',
});

export const metadata = {
  title: 'Project For Fun',
  description: 'A fun project to explore and experiment',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${poppins.variable}`}>
      <body>
        <AppProviders>
          <Navigation />
          {children}
        </AppProviders>
      </body>
    </html>
  );
}

