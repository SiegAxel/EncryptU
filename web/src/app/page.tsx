import Hero from "@/components/layout/Hero";
import Section from "@/components/layout/ui/Section";
import Container from "@/components/layout/ui/Container";
import Button from "@/components/layout/ui/Button";
import ButtonLink from "@/components/layout/ui/ButtonLink";


export default function HomePage() {
    return (
        <>
            <Hero />
            <Section>
                <Container>
                    <h2 className="text-2xl font-semibold">¿Quiénes somos?</h2>
                    <p className="mt-3 max-w-3xl text-slate-600">EncryptU es un gestor automático de contraseñas seguras, diseñado para facilitar el inicio de sesión de credenciales fuertes. Se adapta a personas y equipos con conocimientos técnicos altos y modestos, sin requerir conocimientos técnicos profundos, y lo hace especialmente accesible para personas sin experiencia en seguridad.</p>
                    <div className="mt-4"><ButtonLink variant="outline" href="/marketing/acerca">Ver más</ButtonLink></div>
                </Container>
            </Section>


            <Section className="bg-slate-50">
                <Container>
                    <h2 className="text-2xl font-semibold">¿Cómo descargo EncryptU?</h2>
                    <p className="mt-3 max-w-3xl text-slate-600">Descarga la versión portable según tu sistema operativo y comienza a proteger tus accesos.</p>
                    <div className="mt-4"><ButtonLink href="/marketing/instalacion">Descargar</ButtonLink></div>
                </Container>
            </Section>
        </>
    );
}