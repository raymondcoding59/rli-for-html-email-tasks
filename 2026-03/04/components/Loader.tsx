"use client";

export default function Loader() {
  return (
    <span className="flex items-center gap-2">
      <span className="animate-spin h-4 w-4 border-2 border-white border-t-transparent rounded-full" />
      Generating Design System...
    </span>
  );
}