"use client";

import { useDropzone } from "react-dropzone";

export default function FileDropzone({ onFile }) {
  const { getRootProps, getInputProps } = useDropzone({
    accept: { "text/html": [".html"] },
    onDrop: files => onFile(files[0]),
  });

  return (
    <div
      {...getRootProps()}
      className="border p-10 text-center cursor-pointer"
    >
      <input {...getInputProps()} />
      Drop HTML Email or Click
    </div>
  );
}