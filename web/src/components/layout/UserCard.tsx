import Card from "@/components/ui/Card";


export default function UserCard({name, role}:{name:string; role:string}){
return (
<Card>
<div className="flex items-center gap-4">
<div className="h-12 w-12 rounded-full bg-gradient-to-br from-brand to-pink-300"/>
<div>
<div className="font-medium">{name}</div>
<div className="text-sm text-slate-500">{role}</div>
</div>
</div>
</Card>
);
}