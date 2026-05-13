import syncusCreamLogo from "../../components/syncus-cream.png";

interface SyncUsMarkProps {
  compact?: boolean;
}

export function SyncUsMark({ compact = false }: SyncUsMarkProps) {
  return (
    <img
      src={syncusCreamLogo}
      alt="SyncUs"
      className={compact ? "h-8 w-auto" : "h-11 w-auto"}
    />
  );
}
