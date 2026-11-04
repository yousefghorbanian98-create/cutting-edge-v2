import { ThemeProvider } from "next-themes"
import { cn } from "@/lib/utils"
import "./globals.css"

export const metadata = {
  title: "Cutting Edge V2",
  description: "Style Match-first video editor for sports content creators",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="fa" dir="rtl">
      <body className={cn("min-h-screen bg-background font-sans antialiased")}>
        <ThemeProvider attribute="class" defaultTheme="system" enableSystem>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
