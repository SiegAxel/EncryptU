import Container from "@/components/layout/ui/Container";
import Section from "@/components/layout/ui/Section";
import AdminUsersTable from "./users.client";
import { prisma } from "@/lib/prisma"; // 👈 lee directo de Neon

export default async function AdminPage() {
  const users = await prisma.user.findMany({
    orderBy: { createdAt: "asc" },
    select: { id: true, name: true, email: true, role: true, createdAt: true },
  });

  return (
    <Section>
      <Container>
        <div className="mb-6 flex items-center justify-between">
          <h1 className="text-2xl font-semibold">Administración de cuentas</h1>
        </div>

        <AdminUsersTable initialUsers={users} />
      </Container>
    </Section>
  );
}
