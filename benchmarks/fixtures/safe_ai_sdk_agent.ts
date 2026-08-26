// Vercel AI SDK tool loop with an explicit stop condition.
import { generateText, stepCountIs } from "ai";

export async function resolveTicket(ticket: string) {
  const result = await generateText({
    model: openai("gpt-4o"),
    prompt: ticket,
    stopWhen: stepCountIs(6),
    tools: {
      lookupAccount: lookupAccountTool,
      issueRefund: issueRefundTool,
    },
  });

  return result.text;
}
