import Card from "@/components/layout/ui/Card";
import Button from "@/components/layout/ui/Button";

type Interval = "mensual" | "trimestral" | "anual";

export default function PricingCard({
  title,
  price,
  features,
  highlight = false,
  interval = "mensual",
}: {
  title: string;
  price: string | number;
  features: string[];
  highlight?: boolean;
  interval?: Interval;
}) {
  const intervalLabel: Record<Interval, string> = {
    mensual: "mes",
    trimestral: "trimestre",
    anual: "año",
  };

  return (
    <Card>
      <div className={highlight ? "rounded-xl bg-slate-900 p-6 text-white" : "p-0"}>
        <div className="space-y-2 p-6">
          <h3 className="text-lg font-semibold">{title}</h3>
          <div className="text-4xl font-bold">
            {price}
            <span className={`text-base font-normal ${highlight ? "text-slate-300" : "text-slate-500"}`}>
              /{intervalLabel[interval]}
            </span>
          </div>
        </div>

        <ul className="space-y-2 p-6 pt-0 text-sm">
          {features.map((f) => (
            <li key={f} className="flex items-start gap-2">
              <span>•</span><span>{f}</span>
            </li>
          ))}
        </ul>

        <div className="p-6 pt-0">
          <Button className="w-full">Pagar</Button>
          {/* Si quieres que vaya al checkout: 
          <Link href={`/checkout?plan=${interval}`} className="w-full inline-block text-center rounded bg-brand text-white py-2 mt-2">
            Pagar {interval}
          </Link> */}
        </div>
      </div>
    </Card>
  );
}
