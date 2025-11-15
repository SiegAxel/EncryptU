import Container from "@/components/layout/ui/Container";
import Section from "@/components/layout/ui/Section";
import PricingCard from "@/components/layout/PricingCard";

export default function PricingPage() {
  const basicFeatures = [
    "Gestión de contraseñas segura",
    "Sincronización entre dispositivos",
    "Generador de contraseñas",
    "Vault cifrado local"
  ];

  const standardFeatures = [
    "Todas las funciones de Básico",
    "Vault compartido en equipo",
    "Historial de contraseñas",
    "2FA y autenticación biométrica",
    "Alertas de seguridad"
  ];

  const premiumFeatures = [
    "Todas las funciones de Estándar",
    "Vault ilimitado",
    "API para integraciones",
    "Administrador dedicado",
    "Cumplimiento empresarial"
  ];

  return (
    <Section>
      <Container>
        <div className="grid gap-6 md:grid-cols-3">
          <PricingCard
            name="Básico"
            description="Para usuarios individuales"
            features={basicFeatures}
            price="Free"
            plan_id="P-3PR04716U1599892MNDZ4RTA"
            isFree={true}
            downloadUrl="/marketing/instalacion"
            detail="Comienza a gestionar tus contraseñas de forma segura"
          />
          <PricingCard
            name="Estándar"
            description="Para equipos pequeños"
            features={standardFeatures}
            price="6"
            plan_id="P-3M132065FH7874447NDZ4R6Q"
            isPopular={true}
            detail="La opción más popular para equipos de trabajo"
          />
          <PricingCard
            name="Premium"
            description="Para empresas y organizaciones"
            features={premiumFeatures}
            price="10"
            plan_id="P-5J269540BM416772TNDZ4SEA"
            detail="Solución completa para organizaciones grandes"
          />
        </div>
      </Container>
    </Section>
  );
}