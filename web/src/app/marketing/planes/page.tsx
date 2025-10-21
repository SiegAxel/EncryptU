import Container from "@/components/layout/ui/Container";
import Section from "@/components/layout/ui/Section";
import PricingCard from "@/components/layout/PricingCard";

export default function PricingPage() {
  return (
    <Section>
      <Container>
        <div className="grid gap-6 md:grid-cols-3">
          <PricingCard
            name="Básico"
            description="Plan Básico"
            features={[]}
            price="3"
            plan_id="P-3PR04716U1599892MNDZ4RTA"
            detail="Falta detalles"
          />
          <PricingCard
            name="Estándar"
            description="Plan Estándar"
            features={[]}
            price="6"
            plan_id="P-3M132065FH7874447NDZ4R6Q"
            detail="Falta detalles"
          />
          <PricingCard
            name="Premium"
            description="Plan Premium"
            features={[]}
            price="10"
            plan_id="P-5J269540BM416772TNDZ4SEA"
            detail="Falta detalles"
          />
        </div>
      </Container>
    </Section>
  );
}
