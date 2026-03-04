"use client";

import { useState, useEffect } from "react";
import Tabs from "@/components/tabs/Tabs";
import UploadStage from "@/components/UploadStage";
import DesignSystemStage from "@/components/DesignSystemStage";

type Step = "upload" | "design";

export default function Home() {
  /* ---------------- STATE ---------------- */

  const [activeTab, setActiveTab] =
    useState<Step>("upload");

  const [unlockedTabs, setUnlockedTabs] =
    useState<Step[]>(["upload"]);

  const [html, setHtml] =
    useState<string | null>(null);

  const [markdown, setMarkdown] =
    useState("");

  const [loading, setLoading] =
    useState(false);

  /* ---------------- RESTORE SAVED DESIGN SYSTEM ---------------- */

  useEffect(() => {
    const savedMarkdown =
      localStorage.getItem("designSystemMarkdown");

    if (savedMarkdown) {
      setMarkdown(savedMarkdown);

      // unlock design tab automatically
      setUnlockedTabs(["upload", "design"]);
      setActiveTab("design");
    }
  }, []);

  /* ---------------- GENERATE DESIGN SYSTEM ---------------- */

  async function generate() {
    if (!html || loading) return;

    setLoading(true);

    try {
      const res = await fetch(
        "/api/generate-design",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ html }),
        }
      );

      const data = await res.json();

      setMarkdown(data.markdown);

      // ✅ SAVE RESULT TO LOCAL STORAGE
      localStorage.setItem(
        "designSystemMarkdown",
        data.markdown
      );

      // unlock next tab
      setUnlockedTabs(prev =>
        prev.includes("design")
          ? prev
          : [...prev, "design"]
      );

      setActiveTab("design");
    } finally {
      setLoading(false);
    }
  }

  /* ---------------- RESET WHEN NEW FILE UPLOADED ---------------- */

  function updateHtml(newHtml: string | null) {
    setHtml(newHtml);

    // reset downstream state
    setMarkdown("");
    localStorage.removeItem(
      "designSystemMarkdown"
    );

    setUnlockedTabs(["upload"]);
    setActiveTab("upload");
  }

  /* ---------------- UI ---------------- */

  return (
    <main className="max-w-5xl mx-auto p-10">
      <Tabs
        active={activeTab}
        unlocked={unlockedTabs}
        setActive={setActiveTab}
      />

      {activeTab === "upload" && (
        <UploadStage
          html={html}
          setHtml={updateHtml}
          generate={generate}
          loading={loading}
        />
      )}

      {activeTab === "design" && (
        <DesignSystemStage
          markdown={markdown}
          loading={loading}
        />
      )}
    </main>
  );
}