// Vercel AI SDK tool loop with no step ceiling.
import { generateText } from "ai";

export async function resolveTicket(ticket: string) {
  const result = await generateText({
    model: openai("gpt-4o"),
    prompt: ticket,
    tools: {
      lookupAccount: lookupAccountTool,
      issueRefund: issueRefundTool,
    },
  });

  return result.text;
}
