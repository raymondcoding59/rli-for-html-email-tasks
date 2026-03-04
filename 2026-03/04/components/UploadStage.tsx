"use client";

import FileDropzone from "./FileDropzone";
import EmailPreview from "./EmailPreview";
import Loader from "./Loader";

export default function UploadStage({
  html,
  setHtml,
  generate,
  loading,
}) {
  return (
    <>
      {!html && (
        <FileDropzone
          onFile={file => {
            const reader = new FileReader();

            reader.onload = e =>
              setHtml(e.target?.result as string);

            reader.readAsText(file);
          }}
        />
      )}

      {html && (
        <>
          <EmailPreview html={html} />

          <button
            onClick={generate}
            disabled={loading}
            className={`
              mt-6 px-5 py-3 text-white rounded
              transition
              ${
                loading
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-green-600 hover:bg-green-700"
              }
            `}
          >
            {loading ? (
              <Loader />
            ) : (
              "Confirm File & Generate Design System"
            )}
          </button>
        </>
      )}
    </>
  );
}