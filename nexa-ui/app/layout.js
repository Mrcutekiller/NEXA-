import './globals.css';

export const metadata = {
  title: 'NEXA Intelligence Operating System',
  description: 'Future of AI Operating Systems',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark bg-stone-950 text-stone-100">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Geist+Mono:wght@100..900&family=Geist:wght@100..900&family=Outfit:wght@100..900&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased overflow-hidden font-sans">
        {children}
      </body>
    </html>
  );
}
