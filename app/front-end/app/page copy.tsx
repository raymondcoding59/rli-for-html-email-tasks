"use client"

import { useState } from "react"
import Sidebar from "@/components/Sidebar"
import GeneratorPanel from "@/components/GeneratorPanel"
import EditorPreview from "@/components/EditorPreview"

export default function Page() {

  const [generatedHTML, setGeneratedHTML] = useState<string | null>(null)

  return (
    <div className="flex h-screen w-screen bg-zinc-950">

      <Sidebar />

      <main className="flex-1 flex flex-col overflow-hidden">

        {!generatedHTML && (
          <div className="flex-1 flex items-center justify-center">
            <GeneratorPanel
              onGenerated={(html) => setGeneratedHTML(html)}
            />
          </div>
        )}

        {generatedHTML && (
          <EditorPreview
            html={generatedHTML}
            setHTML={setGeneratedHTML}
            reset={() => setGeneratedHTML(null)}
          />
        )}

      </main>

    </div>
  )
}