// Figma `Icons` 컴포넌트 세트에 대응하는 24x24 아이콘.
// 이름은 Figma 컴포넌트 이름을 그대로 따름.

type IconProps = { size?: number; className?: string };

const base = (size: number) => ({
  width: size,
  height: size,
  viewBox: "0 0 24 24",
  fill: "none",
  xmlns: "http://www.w3.org/2000/svg",
  "aria-hidden": true as const,
});

export function ArrowBackward({ size = 24, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M15 5l-7 7 7 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function ArrowForward({ size = 24, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M9 5l7 7-7 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function ArrowDown({ size = 24, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M6 9l6 6 6-6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Heart({ size = 24, className, selected = false }: IconProps & { selected?: boolean }) {
  return (
    <svg {...base(size)} className={className}>
      <path
        d="M12 20s-7-4.35-7-9a4 4 0 017-2.65A4 4 0 0119 11c0 4.65-7 9-7 9z"
        stroke="currentColor"
        strokeWidth="1.7"
        strokeLinejoin="round"
        fill={selected ? "currentColor" : "none"}
      />
    </svg>
  );
}

export function Share({ size = 24, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <circle cx="17.5" cy="6" r="2.5" stroke="currentColor" strokeWidth="1.7" />
      <circle cx="6.5" cy="12" r="2.5" stroke="currentColor" strokeWidth="1.7" />
      <circle cx="17.5" cy="18" r="2.5" stroke="currentColor" strokeWidth="1.7" />
      <path d="M8.8 10.8l6.4-3.5M8.8 13.2l6.4 3.5" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}

export function MenuHorizontal({ size = 24, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <circle cx="5" cy="12" r="1.6" fill="currentColor" />
      <circle cx="12" cy="12" r="1.6" fill="currentColor" />
      <circle cx="19" cy="12" r="1.6" fill="currentColor" />
    </svg>
  );
}

export function MenuVertical({ size = 24, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <circle cx="12" cy="5" r="1.6" fill="currentColor" />
      <circle cx="12" cy="12" r="1.6" fill="currentColor" />
      <circle cx="12" cy="19" r="1.6" fill="currentColor" />
    </svg>
  );
}

export function ThumbUp({ size = 24, className, filled = false }: IconProps & { filled?: boolean }) {
  return (
    <svg {...base(size)} className={className}>
      <path
        d="M7 10.5V20H4.8A.8.8 0 014 19.2v-7.9a.8.8 0 01.8-.8H7zm0 0l4-6.7a1.6 1.6 0 012.9 1.2L13.4 9h4.9a1.7 1.7 0 011.66 2.05l-1.2 6A1.7 1.7 0 0117.1 18.4H7"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinejoin="round"
        fill={filled ? "currentColor" : "none"}
      />
    </svg>
  );
}

export function Cross({ size = 24, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M6 6l12 12M18 6L6 18" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  );
}

export function Check({ size = 24, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M5 12.5l4.5 4.5L19 7.5" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

export function Report({ size = 24, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <path d="M5 21V4h9l.5 2H20l-1.5 5L20 16h-6l-.5-2H6" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
    </svg>
  );
}

export function Lock({ size = 24, className }: IconProps) {
  return (
    <svg {...base(size)} className={className}>
      <rect x="5" y="10" width="14" height="10" rx="2.5" stroke="currentColor" strokeWidth="1.7" />
      <path d="M8.5 10V7.5a3.5 3.5 0 017 0V10" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" />
    </svg>
  );
}
