"use client";

import Editor from "@monaco-editor/react";
import { PanelGroup, Panel, PanelResizeHandle } from "react-resizable-panels"

interface Props {
  html: string;
  setHTML: (html: string) => void;
  reset: () => void
}

export default function EditorPreview({ html, setHTML, reset }: Props) {
  return (
    <div className="h-full flex flex-col">
      <div className="flex items-center justify-between px-4 py-2 border-b border-zinc-800 bg-zinc-900">

  <span className="text-sm text-zinc-400">
    generated-email.html
  </span>

  <div className="flex gap-2">

    <button
      onClick={reset}
      className="text-sm bg-zinc-800 px-3 py-1 rounded hover:bg-zinc-700 text-white"
    >
      New Design
    </button>

    <button
      onClick={() => navigator.clipboard.writeText(html)}
      className="text-sm bg-zinc-800 px-3 py-1 rounded hover:bg-zinc-700 text-white"
    >
      Copy HTML
    </button>

  </div>

</div>

      <PanelGroup direction="horizontal">
        {/* HTML Editor */}

        <Panel defaultSize={50} minSize={30}>
          <Editor
            height="100%"
            defaultLanguage="html"
            value={html}
            onChange={(value) => setHTML(value || "")}
            theme="vs-dark"
            options={{
              fontSize: 14,
              minimap: { enabled: false },
              wordWrap: "on",
              automaticLayout: true,
            }}
          />
        </Panel>

        <PanelResizeHandle className="w-1 bg-zinc-800 hover:bg-blue-500 transition" />

        {/* Preview */}

        <Panel defaultSize={50} minSize={30}>
          <iframe key={html} srcDoc={html} className="w-full h-full bg-white" />
        </Panel>
      </PanelGroup>
    </div>
  );
}
