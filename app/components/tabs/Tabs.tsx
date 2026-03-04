"use client";

type Step = "upload" | "design";

export default function Tabs({
  active,
  unlocked,
  setActive,
}: {
  active: Step;
  unlocked: Step[];
  setActive: (s: Step) => void;
}) {
  const tabs: Step[] = ["upload", "design"];

  return (
    <div className="flex border-b mb-6">
      {tabs.map(tab => {
        const locked = !unlocked.includes(tab);

        return (
          <button
            key={tab}
            disabled={locked}
            onClick={() => setActive(tab)}
            className={`
              px-6 py-3 capitalize
              ${active === tab && "border-b-2 border-blue-500"}
              ${locked && "opacity-40 cursor-not-allowed"}
            `}
          >
            {tab}
          </button>
        );
      })}
    </div>
  );
}