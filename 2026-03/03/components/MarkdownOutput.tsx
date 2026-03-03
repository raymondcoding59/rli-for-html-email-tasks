"use client";

import ReactMarkdown from "react-markdown";

export default function MarkdownOutput({ markdown }) {
  return (
    <pre className="bg-black text-green-400 p-6 mt-6 overflow-auto">
      <ReactMarkdown>{markdown}</ReactMarkdown>
    </pre>
  );
}