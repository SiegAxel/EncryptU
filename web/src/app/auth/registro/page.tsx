import Container from "@/components/layout/ui/Container";
import Card from "@/components/layout/ui/Card";
import Input from "@/components/layout/ui/Input";
import Button from "@/components/layout/ui/Button";
import Link from "next/link";                // ← importa Link

export default function ResetPasswordPage() {
  return (
    <div className="section">
      <Container>
        <div className="mx-auto max-w-2xl">
          <Card>
            <h1 className="mb-4 text-xl font-semibold">Restablecer contraseña</h1>
            <div className="space-y-3">
              <Input label="Email" type="email" placeholder="tu@email.com" />
              <div className="flex gap-3">
                {/* usa Link para rutas internas */}
                <Link href="/" className="btn-outline">Cancelar</Link>
                <Button>Reset Password</Button>
              </div>
            </div>
          </Card>
        </div>
      </Container>
    </div>
  );
}
