import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import Layout from '@/components/Layout';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: 'Selma Stock Prediction - AI-Powered Indonesian Stock Analysis',
  description:
    'Predict Indonesian stock prices using AI and machine learning. Get accurate forecasts for IDX stocks like BBCA, BMDR, TLKM, and more.',
  keywords: ['stock prediction', 'Indonesian stocks', 'IDX', 'AI', 'machine learning', 'BBCA', 'BMDR'],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Layout>{children}</Layout>
      </body>
    </html>
  );
}
