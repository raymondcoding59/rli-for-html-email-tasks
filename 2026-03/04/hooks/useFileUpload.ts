import { useState } from "react";

export function useFileUpload() {
  const [html, setHtml] = useState<string | null>(null);

  const loadFile = (file: File) => {
    const reader = new FileReader();

    reader.onload = e => {
      setHtml(e.target?.result as string);
    };

    reader.readAsText(file);
  };

  return { html, loadFile };
}