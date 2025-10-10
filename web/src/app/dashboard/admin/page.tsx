import Container from "@/components/layout/ui/Container";
import Section from "@/components/layout/ui/Section";
import UserCard from "@/components/layout/UserCard";
import Button from "@/components/layout/ui/Button";


const users = [
{ name: "Freddy Cárdenas", role: "Owner" },
{ name: "Ariel Escobar", role: "Admin" },
{ name: "Felipe Valenzuela", role: "User" },
{ name: "Felipe Valenzuela 2", role: "User" },
];


export default function AdminPage(){
return (
<Section>
<Container>
<div className="mb-6 flex items-center justify-between">
<h1 className="text-2xl font-semibold">Administración de cuentas</h1>
<div className="flex gap-2">
<Button>Nuevo usuario</Button>
<Button variant="outline">Guardar cambios</Button>
</div>
</div>
<div className="grid gap-4 md:grid-cols-2">
{users.map(u => (<UserCard key={u.name} name={u.name} role={u.role} />))}
</div>
</Container>
</Section>
);
}