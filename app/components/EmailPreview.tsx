"use client";

import { sanitize } from "@/lib/sanitizeHtml";

export default function EmailPreview({ html }) {
  return (
    <div
      className="border mt-6"
      dangerouslySetInnerHTML={{
        __html: sanitize(html),
      }}
    />
  );
}