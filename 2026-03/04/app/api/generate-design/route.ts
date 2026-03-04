import { NextResponse } from "next/server";
import { openai } from "@/lib/openai";

export async function POST(req: Request) {
  const { html } = await req.json();

  if (!html) {
    return NextResponse.json(
      { error: "No HTML provided" },
      { status: 400 }
    );
  }

  const prompt = `
You are a senior design systems engineer.

Analyze this HTML email and create a DESIGN SYSTEM in markdown.

Include:
- Colors
- Typography
- Spacing
- Components
- Buttons
- Layout rules

HTML:
${html.slice(0, 15000)}
`;

  const response = await openai.chat.completions.create({
    model: "gpt-4.1",
    messages: [{ role: "user", content: prompt }],
  });

  return NextResponse.json({
    markdown: response.choices[0].message.content,
  });
}