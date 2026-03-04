"use client";

import ReactMarkdown from "react-markdown";

export default function DesignSystemStage({
  markdown,
  loading,
}) {
  if (loading) return <p>Generating design system...</p>;

  if (!markdown)
    return <p>No design system generated yet.</p>;

  return (
    <div className="bg-black text-green-400 p-6">
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </div>
  );
}