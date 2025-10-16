// src/lib/cn.ts
export const cn = (...classes: string[]) => classes.filter(Boolean).join(" ");
