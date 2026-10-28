import { Loader2, Sparkles } from "lucide-react";
import type { ButtonHTMLAttributes, InputHTMLAttributes } from "react";

export const cn = (...c: (string | false | undefined)[]) =>
  c.filter(Boolean).join(" ");
export const Spinner = ({ className }: { className?: string }) => (
  <Loader2
    className={cn("h-5 w-5 animate-spin text-mute", className)}
    aria-label="Loading"
  />
);

export function Button({
  variant = "primary",
  className,
  ...p
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: "primary" | "ghost" | "outline";
}) {
  const v = {
    primary:
      "bg-brand text-brand-ink shadow-[0_8px_28px_-10px_rgb(var(--brand)/.9)] hover:brightness-110",
    ghost: "text-mute hover:bg-line/60 hover:text-ink",
    outline: "border border-line hover:bg-line/50",
  }[variant];
  return (
    <button
      {...p}
      className={cn(
        "inline-flex h-10 items-center justify-center gap-2 rounded-full px-5 text-sm font-medium transition disabled:opacity-50",
        v,
        className,
      )}
    />
  );
}
export function Input({
  label,
  className,
  ...p
}: InputHTMLAttributes<HTMLInputElement> & { label: string }) {
  return (
    <label className="block text-sm">
      <span className="mb-1.5 block font-medium">{label}</span>
      <input
        {...p}
        className={cn(
          "h-11 w-full rounded-xl border border-line glass px-3 placeholder:text-mute/70",
          className,
        )}
      />
    </label>
  );
}
export const Card = ({
  className,
  ...p
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    {...p}
    className={cn("rounded-2xl border border-line glass", className)}
  />
);
export const ErrorNote = ({ msg }: { msg: string }) =>
  msg ? (
    <p
      role="alert"
      className="rounded-lg border border-red-500/30 bg-red-500/10 px-3 py-2 text-sm text-red-600 dark:text-red-400"
    >
      {msg}
    </p>
  ) : null;
export const Orb = ({ lg }: { lg?: boolean }) => (
  <span
    aria-hidden
    className={cn(
      "grid shrink-0 place-items-center rounded-full border border-brand/40 bg-brand/15 text-brand-text",
      lg
        ? "orb-glow h-28 w-28 ring-8 ring-brand/10"
        : "h-9 w-9 shadow-[0_0_24px_-6px_rgb(var(--brand)/.7)]",
    )}
  >
    <Sparkles className={lg ? "h-10 w-10" : "h-4 w-4"} />
  </span>
);
export const Empty = ({ title, hint }: { title: string; hint: string }) => (
  <div className="px-6 py-12 text-center">
    <p className="font-display text-lg">{title}</p>
    <p className="mt-1 text-sm text-mute">{hint}</p>
  </div>
);
