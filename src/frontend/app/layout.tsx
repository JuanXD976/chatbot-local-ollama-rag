import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Chatbot Local con Ollama - V2.0",
  description: "Frontend premium con Next.js para el chatbot local con FastAPI",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}