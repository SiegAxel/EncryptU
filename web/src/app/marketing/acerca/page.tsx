import Container from "@/components/layout/ui/Container";
import Section from "@/components/layout/ui/Section";
import Card from "@/components/layout/ui/Card";


const team = [
    { name: "Felipe Torres", role: "CEO" },
    { name: "Manuel Miqueles", role: "Analista de datos" },
    { name: "Liam Ley", role: "QA Tester" },
    { name: "Nicolás Fernández", role: "Programador" },
    { name: "Jose Rojas", role: "Desarrollador" },
];


export default function AboutPage() {
    return (
        <>
            <Section>
                <Container>
                    <h1 className="text-3xl font-semibold">Acerca de <span className="text-brand">EncryptU</span></h1>
                    <p className="mt-4 max-w-3xl text-slate-600">Enfocados en soluciones tecnológicas orientadas a la seguridad digital y protección de datos. Nuestro compromiso es ofrecer un gestor de contraseñas confiable, seguro y fácil de implementar, que cumpla con las mejores prácticas de la industria.</p>
                </Container>
            </Section>
            <Section className="bg-slate-50">
                <Container>
                    <h2 className="mb-6 text-xl font-semibold">Conócenos</h2>
                    <div className="grid gap-6 md:grid-cols-5">
                        {team.map(t => (
                            <Card key={t.name}>
                                <div className="flex flex-col items-center gap-3">
                                    <div className="h-20 w-20 rounded-full bg-gradient-to-br from-brand to-pink-300" />
                                    <div className="text-center">
                                        <div className="font-medium">{t.name}</div>
                                        <div className="text-sm text-slate-500">{t.role}</div>
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>
                </Container>
            </Section>
        </>
    );
}