import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

// Whitelist patterns - commands matching ANY of these are allowed
// All others are blocked
const WHITELIST: RegExp[] = [
  /^ls\b/,
  /^grep\b/,
  /^find\b/,
  /^pwd\b/,
  /^whoami\b/,
  /^head\b/,
  /^tail\b/,
  /^cat\b/,
];

export default function (pi: ExtensionAPI) {
  pi.on("tool_call", async (event, ctx) => {
    if (event.toolName !== "bash") return;

    const command = (event.input.command as string).trim();
    const matched = WHITELIST.some((p) => p.test(command));

    if (!matched) {
      return { block: true, reason: `Command not in whitelist: ${command}` };
    }
  });
}
