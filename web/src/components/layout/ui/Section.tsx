import { PropsWithChildren } from "react";
import { cn } from "@/lib/cn";


export default function Section({ children, className }: PropsWithChildren & {className?: string}){
return <section className={cn("section", className)}>{children}</section>;
}