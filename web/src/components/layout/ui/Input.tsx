import { InputHTMLAttributes } from "react";
import { cn } from "@/lib/cn";


export default function Input(props: InputHTMLAttributes<HTMLInputElement> & {label?: string}){
const { label, className, ...rest } = props;
return (
<label className="block space-y-1">
{label && <span className="text-sm text-slate-600">{label}</span>}
<input className={cn("input", className)} {...rest} />
</label>
);
}