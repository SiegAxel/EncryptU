import Container from "@/components/layout/ui/Container";
import Section from "@/components/layout/ui/Section";
import { prisma } from "@/lib/prisma";
import AdminUsersPanel from "./user-panel";
import ReportGenerator from "@/components/admin/ReportGenerator";

// Tipo que vas a pasar al cliente
export type UIUser = {
  id: number;
  name: string;
  email: string;
  role: "usuario" | "soporte" | "admin";
  createdAt: string;            // ← string (ISO)
};

export default async function AdminPage() {
  const rows = await prisma.user.findMany({
    orderBy: { createdAt: "asc" },
    select: { id: true, name: true, email: true, role: true, createdAt: true },
  });

  // serializa Date → string
  const users: UIUser[] = rows.map(u => ({
    ...u,
    createdAt: u.createdAt.toISOString(),
  }));

  return (
    <Section>
      <Container>
        <h1 className="mb-6 text-2xl font-semibold">Administración de cuentas</h1>
        
        {/* Report Generator */}
        <ReportGenerator
          type="users"
          title="Reporte de Usuarios"
          description="Generar informes completos de todos los usuarios con opciones de filtrado"
        />
        
        <AdminUsersPanel initialUsers={users} />
      </Container>
    </Section>
  );
}
