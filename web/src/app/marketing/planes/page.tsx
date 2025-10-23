import Container from "@/components/layout/ui/Container";
import Section from "@/components/layout/ui/Section";
import PricingCard from "@/components/layout/PricingCard";

export default function PricingPage() {
  const basicFeatures = [
    "Basic encryption features",
    "1 GB storage",
    "Email support"
  ];

  const standardFeatures = [
    "All Basic features",
    "5 GB storage",
    "Priority email support",
    "Advanced encryption options"
  ];

  const premiumFeatures = [
    "All Standard features",
    "Unlimited storage",
    "24/7 phone support",
    "Custom encryption solutions",
    "API access"
  ];

  return (
    <Section>
      <Container>
        <div className="grid gap-6 md:grid-cols-3">
          <PricingCard
            name="Básico"
            description="Perfect for getting started"
            features={basicFeatures}
            price="Free"
            plan_id="P-3PR04716U1599892MNDZ4RTA"
            detail="Start securing your data today"
          />
          <PricingCard
            name="Estándar"
            description="Great for growing needs"
            features={standardFeatures}
            price="6"
            plan_id="P-3M132065FH7874447NDZ4R6Q"
            detail="Most popular choice for small teams"
          />
          <PricingCard
            name="Premium"
            description="For enterprise requirements"
            features={premiumFeatures}
            price="10"
            plan_id="P-5J269540BM416772TNDZ4SEA"
            detail="Complete solution for large organizations"
          />
        </div>
      </Container>
    </Section>
  );
}