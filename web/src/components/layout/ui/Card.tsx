import { PropsWithChildren } from "react";
import { cn } from "@/lib/cn";


export default function Card({ children }: PropsWithChildren & {className?: string}){
return <div className={cn("card p-6",)}>{children}</div>;
}