import Card from "@/components/layout/ui/Card";
import Button from "@/components/layout/ui/Button";


export default function PricingCard({ title, price, features, highlight = false }: {
    title: string;
    price: string;
    features: string[];
    highlight?: boolean;
}) {
    return (
        <Card>
            <div className={highlight ? "rounded-xl bg-slate-900 p-6 text-white" : "p-0"}>
                <div className="space-y-2 p-6">
                    <h3 className="text-lg font-semibold">{title}</h3>
                    <div className="text-4xl font-bold">{price}<span className="text-base font-normal text-slate-500">/mes</span></div>
                </div>
                <ul className="space-y-2 p-6 pt-0 text-sm">
                    {features.map((f) => (<li key={f} className="flex items-start gap-2"><span>•</span><span>{f}</span></li>))}
                </ul>
                <div className="p-6 pt-0">
                    <Button className="w-full">Una paga {highlight ? "trimestral" : "mensual"}</Button>
                </div>
            </div>
        </Card>
    );
}