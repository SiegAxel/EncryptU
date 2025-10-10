
import Link from "next/link";
import PricingCard from "@/components/layout/PricingCard";

export default function HomePage() {
  return (
    <section>
      <div className="grid md:grid-cols-3 gap-6">
        <PricingCard
          title="Plan Mensual"
          price="$19"
          interval="mensual"
          features={["Autologin de credenciales", "Cifrado local", "Soporte básico"]}
        />

        <PricingCard
          title="Plan Trimestral"
          price="$50"
          interval="trimestral"
          highlight
          features={["Mejor precio por periodo corto", "Funciones avanzadas", "Prioridad media"]}
        />

        <PricingCard
          title="Plan Anual"
          price="$99"
          interval="anual"
          features={["Ahorro máximo", "Todas las funciones", "Soporte prioritario"]}
        />
      </div>

    </section>
  );
}
