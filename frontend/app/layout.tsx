import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Investia",
  description: "Bots de trading cuantitativo en paper y en vivo",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="min-h-screen bg-gradient-to-b from-white via-slate-50 to-white">
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </div>
      </body>
    </html>
  );
}
