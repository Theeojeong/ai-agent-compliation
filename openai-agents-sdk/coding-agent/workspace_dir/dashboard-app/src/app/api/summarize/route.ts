import { NextRequest, NextResponse } from "next/server";
import OpenAI from "openai";

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { metrics } = body as { metrics?: string };

    if (!process.env.OPENAI_API_KEY) {
      return NextResponse.json(
        { error: "OPENAI_API_KEY is not configured on the server." },
        { status: 500 },
      );
    }

    if (!metrics) {
      return NextResponse.json(
        { error: "Missing `metrics` in request body." },
        { status: 400 },
      );
    }

    const response = await openai.responses.create({
      model: "gpt-5.1",
      input: [
        "You are a concise analytics assistant.",
        "Summarize the following dashboard metrics for a non-technical stakeholder in 3-5 bullet points.",
        metrics,
      ],
      max_output_tokens: 300,
    });

    const outputText =
      response.output[0]?.content[0]?.type === "output_text"
        ? response.output[0].content[0].text
        : "Unable to generate summary.";

    return NextResponse.json({ summary: outputText });
  } catch (error) {
    console.error("Error summarizing metrics", error);
    return NextResponse.json(
      { error: "Failed to summarize metrics." },
      { status: 500 },
    );
  }
}

