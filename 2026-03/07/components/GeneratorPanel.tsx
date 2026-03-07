"use client"

import { useState } from "react"
import LoadingSpinner from "./LoadingSpinner"

interface Props {
  onGenerated: (html: string) => void
}

export default function GeneratorPanel({ onGenerated }: Props) {

  const [file, setFile] = useState<File | null>(null)
  const [loading, setLoading] = useState(false)

  async function generate() {

    if (!file) return

    setLoading(true)

    const formData = new FormData()
    formData.append("file", file)

    const res = await fetch(
      "http://127.0.0.1:8000/generate-email",
      {
        method: "POST",
        body: formData
      }
    )

    const data = await res.json()

    setLoading(false)

    onGenerated(data.generated_html)
  }

  return (

    <div className="w-full max-w-xl bg-zinc-900 p-8 rounded-xl shadow-lg border border-zinc-800">

      <h1 className="text-xl font-semibold mb-6 text-white">
        Generate Email
      </h1>

      <input
        type="file"
        accept="image/*"
        onChange={(e) =>
          setFile(e.target.files?.[0] ?? null)
        }
        className="mb-4 block w-full text-sm text-white"
      />

      <button
        disabled={loading}
        onClick={generate}
        className="
        px-4 py-2
        bg-blue-600
        text-white
        rounded
        hover:bg-blue-500
        disabled:opacity-40
        "
      >

        {loading ? <LoadingSpinner /> : "Generate HTML"}

      </button>

    </div>
  )
}