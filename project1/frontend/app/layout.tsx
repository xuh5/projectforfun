import './globals.css';

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
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

