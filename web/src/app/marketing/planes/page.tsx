"use client";

import { useState, useEffect } from "react";
import Container from "@/components/layout/ui/Container";
import Section from "@/components/layout/ui/Section";
import PricingCard from "@/components/layout/PricingCardSimple";

interface SubscriptionStatus {
  hasActiveSubscription: boolean;
  currentSubscription: {
    id: number;
    planName: string;
    planPrice: string;
    status: string;
    nextBillingDate: string;
  } | null;
}

export default function PricingPage() {
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkSubscription = async () => {
      try {
        const response = await fetch('/api/subscriptions/check-current', {
          method: 'GET',
          credentials: 'include'
        });

        const result = await response.json();
        if (result.ok) {
          setSubscriptionStatus(result);
        }
      } catch (error) {
        console.error("Error checking subscription:", error);
      } finally {
        setLoading(false);
      }
    };

    checkSubscription();
  }, []);

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
        {/* Subscription Status Banner */}
        {subscriptionStatus?.hasActiveSubscription && (
          <div className="mb-8 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-green-800">
                  Suscripción Activa: {subscriptionStatus.currentSubscription?.planName}
                </p>
                <p className="text-sm text-green-700">
                  Tienes una suscripción activa. Puedes actualizar tu plan en cualquier momento.
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-3">
          <PricingCard
            name="Básico"
            description="Para usuarios individuales"
            features={basicFeatures}
            price="Free"
            plan_id="FREE_PLAN"
            databasePlanId={1}
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
            databasePlanId={2}
            isPopular={true}
            detail="La opción más popular para equipos de trabajo"
          />
          <PricingCard
            name="Premium"
            description="Para empresas y organizaciones"
            features={premiumFeatures}
            price="10"
            plan_id="P-5J269540BM416772TNDZ4SEA"
            databasePlanId={3}
            detail="Solución completa para organizaciones grandes"
          />
        </div>
      </Container>
    </Section>
  );
}