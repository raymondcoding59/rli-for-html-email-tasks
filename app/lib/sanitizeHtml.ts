import DOMPurify from "isomorphic-dompurify";

export function sanitize(html: string) {
  return DOMPurify.sanitize(html);
}