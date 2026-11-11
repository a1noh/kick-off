// A small icon button that copies exact text and says so (toast + check icon for a moment).
import { Check, Copy } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { copyText } from "../lib/tryit.js";

export default function CopyButton({ text, label = "text" }) {
  const [done, setDone] = useState(false);
  const copy = async () => {
    const ok = await copyText(text);
    if (ok) {
      setDone(true);
      toast("Copied", { description: text });
      setTimeout(() => setDone(false), 1400);
    } else {
      toast("Couldn't copy. Select the text and copy it by hand.");
    }
  };
  return (
    <button type="button" className="icon-btn" onClick={copy} aria-label={`Copy ${label}`} title={`Copy ${label}`}>
      {done ? <Check size={14} aria-hidden /> : <Copy size={14} aria-hidden />}
    </button>
  );
}
