// Turn a plan "Try it" line into steps the guide can act on. Plain parsing, no rules: the plan's own syntax.
//   `input` → "expected reply" → `next input` → "next reply" · panel notes …
// Each `input` is paired with the next "quoted" text after it. Lines without an input are a manual check.

export function parseTryIt(line) {
  const tokens = [...line.matchAll(/`([^`]+)`|"([^"]+)"/g)];
  const steps = [];
  for (const m of tokens) {
    if (m[1] !== undefined) steps.push({ input: m[1], expect: null });
    else if (steps.length && steps[steps.length - 1].expect === null) steps[steps.length - 1].expect = m[2];
  }
  const firstQuote = line.indexOf('"');
  const head = (firstQuote > 0 ? line.slice(0, firstQuote) : line).split(" (")[0]; // drop "(every check …" asides
  const summary = head.replace(/,?\s*e\.g\.\s*$/, "").replace(/[→·,:\s]+$/, "").replaceAll("`", "");
  return { steps, summary: summary.trim(), full: line.replaceAll("`", "") };
}

// Every input mentioned in the lines, in order, without duplicates (chat suggestion chips).
export function allInputs(lines) {
  return [...new Set(lines.flatMap((l) => parseTryIt(l).steps.map((s) => s.input)))];
}

export async function copyText(text) {
  try {
    await navigator.clipboard.writeText(text);
    return true;
  } catch {
    const area = document.createElement("textarea"); // fallback where the Clipboard API is blocked
    area.value = text;
    area.setAttribute("readonly", "");
    area.style.position = "fixed";
    area.style.opacity = "0";
    document.body.appendChild(area);
    area.select();
    const ok = document.execCommand?.("copy") ?? false;
    area.remove();
    return ok;
  }
}
