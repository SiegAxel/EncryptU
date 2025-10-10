import Container from "@/components/layout/ui/Container";
import Button from "@/components/layout/ui/Button";


export default function Hero() {
    return (
        <div className="relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 text-white">
            <Container>
                <div className="py-20">
                    <h1 className="text-3xl font-semibold md:text-5xl">Gestor de contraseñas <span className="text-brand">simple y seguro</span></h1>
                    <p className="mt-4 max-w-2xl text-slate-300">EncryptU es un gestor portable para proteger tus accesos con cifrado AES-256 y buenas prácticas por defecto. Descarga y usa sin instalación.</p>
                    <div className="mt-8 flex flex-wrap gap-3">
                        <Button>Descargar</Button>
                        <Button variant="outline">Ver más</Button>
                    </div>
                </div>
            </Container>
            <div className="absolute inset-0 -z-10 opacity-20" aria-hidden>
                <svg viewBox="0 0 600 600" className="h-full w-full">
                    <defs>
                        <linearGradient id="grad" x1="0" x2="1">
                            <stop offset="0" stopColor="#e85a70" />
                            <stop offset="1" stopColor="#ffffff" />
                        </linearGradient>
                    </defs>
                    <circle cx="500" cy="120" r="120" fill="url(#grad)" />
                </svg>
            </div>
        </div>
    );
}