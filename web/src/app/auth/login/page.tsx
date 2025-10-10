import Container from "@/components/layout/ui/Container";
import Card from "@/components/layout/ui/Card";
import Input from "@/components/layout/ui/Input";
import Button from "@/components/layout/ui/Button";
import Link from "next/link";


export default function LoginPage() {
    return (
        <div className="section bg-slate-50">
            <Container>
                <div className="mx-auto max-w-md">
                    <Card>
                        <h1 className="mb-4 text-xl font-semibold">Iniciar sesión</h1>
                        <div className="space-y-3">
                            <Input label="Email" type="email" placeholder="tu@email.com" />
                            <Input label="Password" type="password" placeholder="••••••••" />
                            <Button className="w-full">Sign in</Button>
                            <Link href="/" className="btn-outline">Cancelar</Link>
                        </div>
                    </Card>
                </div>
            </Container>
        </div>
    );
}