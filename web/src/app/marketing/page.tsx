import PricingCard from "@/components/layout/PricingCard";

export default function HomePage() {
  return (
    <section>
      <div className="grid md:grid-cols-3 gap-6">
        <PricingCard
            name="Básico"
            description="Plan Básico"
            features={[]}
            price="3"
            plan_id="P-3PR04716U1599892MNDZ4RTA"
          />
          <PricingCard
            name="Estándar"
            description="Plan Estándar"
            features={[]}
            price="6"
            plan_id="P-3M132065FH7874447NDZ4R6Q"
          />
          <PricingCard
            name="Premium"
            description="Plan Premium"
            features={[]}
            price="10"
            plan_id="P-5J269540BM416772TNDZ4SEA"
          />
      </div>

    </section>
  );
}
