import Container from "@/components/layout/ui/Container";
import SocialBar from "./SocialBar";


export default function Footer(){
return (
<footer className="mt-16 border-t bg-white">
<Container>
<div className="flex flex-col items-center justify-between gap-6 py-10 md:flex-row">
<p className="text-sm text-slate-600">© {new Date().getFullYear()} EncryptU — Syntec</p>
<SocialBar />
</div>
</Container>
</footer>
);
}