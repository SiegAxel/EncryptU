import Container from "@/components/layout/ui/Container";
import Section from "@/components/layout/ui/Section";
import PricingCard from "@/components/layout/PricingCard";


export default function PricingPage() {
  return (
    <Section>
      <Container>
        <div className="grid gap-6 md:grid-cols-3">
          <PricingCard title="Mensual" price="$19" features={[
            "Ideal para probar",
            "Acceso completo a funciones básicas",
            "Soporte estándar",
          ]} />
          <PricingCard title="Trimestral" price="$50" highlight features={[
            "Todo lo del plan mensual",
            "Descuento exclusivo (-12%)",
            "Soporte prioritario",
          ]} />
          <PricingCard title="Anual" price="$99" features={[
            "Múltiples dispositivos",
            "Actualizaciones incluidas",
            "Descuento total (-30%)",
          ]} />
        </div>
      </Container>
    </Section>
  );
}