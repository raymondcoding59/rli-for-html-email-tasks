"use client";
import { useState } from "react";

export default function Home() {
  const [html, setHtml] = useState("");
  const [desc, setDesc] = useState("");

  const handleUpload = async (e: any) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("file", file);

    const res = await fetch("http://localhost:8000/generate", {
      method: "POST",
      body: formData,
    });

    const data = await res.json();
    setHtml(data.html);
    setDesc(data.description);
  };

  return (
    <div style={{ padding: 20 }}>
      <h1>UI → HTML (RAG)</h1>

      <input type="file" onChange={handleUpload} />

      <h3>Description</h3>
      <pre>{desc}</pre>

      <h3>Generated HTML</h3>
      <div
        style={{ border: "1px solid #ccc", padding: 10 }}
        dangerouslySetInnerHTML={{ __html: html }}
      />
    </div>
  );
}