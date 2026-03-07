"use client"

import { useState } from "react"

export default function Sidebar() {

  const [open, setOpen] = useState(true)

  async function uploadSample(file: File) {

    const formData = new FormData()
    formData.append("file", file)

    await fetch("http://127.0.0.1:8000/upload-sample", {
      method: "POST",
      body: formData
    })

    alert("Sample uploaded")
  }

  return (

    <aside
      className={`
      bg-zinc-900 border-r border-zinc-800
      transition-all duration-300
      ${open ? "w-72" : "w-12"}
      `}
    >

      <button
        className="p-2 text-sm text-white"
        onClick={() => setOpen(!open)}
      >
        ☰
      </button>

      {open && (

        <div className="p-4 space-y-4 text-white">

          <h2 className="font-semibold">
            HTML Style Samples
          </h2>

          <input
            type="file"
            accept=".html"
            onChange={(e) => {
              if (!e.target.files) return
              uploadSample(e.target.files[0])
            }}
          />

        </div>

      )}

    </aside>
  )
}