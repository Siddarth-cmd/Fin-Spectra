import type { Metadata } from "next";
import "./globals.css";
import { Sidebar } from "@/components/layout/Sidebar";
import { TopHeader } from "@/components/layout/TopHeader";

export const metadata: Metadata = {
  title: "FinSpectra AML - Intelligent Surveillance Core",
  description: "Financial Crime Alert Investigation - Phase 1 Alert Triage Platform",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark" suppressHydrationWarning>
      <body className="bg-[#080B11] text-slate-100 min-h-screen flex flex-col antialiased" suppressHydrationWarning>
        <div className="flex flex-1">

          {/* Fixed Left Sidebar */}
          <Sidebar />

          {/* Main Content Area */}
          <div className="flex-1 ml-64 flex flex-col min-h-screen bg-[#080B11]">
            <TopHeader />
            <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
              {children}
            </main>

            {/* Global Footer */}
            <footer className="px-6 py-4 border-t border-white/5 bg-[#070A11] flex items-center justify-between text-[11px] text-slate-500 font-mono">
              <div>
                Data source: AMLSim-R synthetic dataset - Phase 1 of 3 - FinSpectra
              </div>
              <div>v2.4.0-sec.9</div>
            </footer>
          </div>
        </div>
      </body>
    </html>
  );
}
