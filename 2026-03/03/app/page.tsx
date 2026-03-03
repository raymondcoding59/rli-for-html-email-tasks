"use client";

import { useState } from "react";
import FileDropzone from "@/components/FileDropzone";
import EmailPreview from "@/components/EmailPreview";
import MarkdownOutput from "@/components/MarkdownOutput";
import { useFileUpload } from "@/hooks/useFileUpload";

export default function Home() {
  const { html, loadFile } = useFileUpload();

  const [confirmed, setConfirmed] = useState(false);
  const [markdown, setMarkdown] = useState("");
  const [loading, setLoading] = useState(false);

  async function generate() {
    setLoading(true);

    const res = await fetch("/api/generate-design", {
      method: "POST",
      body: JSON.stringify({ html }),
    });

    const data = await res.json();

    setMarkdown(data.markdown);
    setLoading(false);
  }

  return (
    <main className="p-10 max-w-4xl mx-auto">
      {!html && <FileDropzone onFile={loadFile} />}

      {html && !confirmed && (
        <>
          <EmailPreview html={html} />

          <button
            onClick={() => setConfirmed(true)}
            className="mt-4 bg-blue-500 text-white p-2"
          >
            Confirm File
          </button>
        </>
      )}

      {confirmed && (
        <button
          onClick={generate}
          className="bg-green-600 text-white p-3"
        >
          Generate Design System
        </button>
      )}

      {loading && <p>Processing...</p>}

      {markdown && <MarkdownOutput markdown={markdown} />}
    </main>
  );
}