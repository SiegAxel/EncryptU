"use client";

import { useState, useEffect } from "react";
import ButtonPaypal from "@/components/PayPal/ButtonPaypal";
import PayPalProvider from "@/components/PayPal/PayPalProvider";

interface Props {
  name: string;
  description: string;
  features: string[];
  price: string;
  plan_id: string;
  databasePlanId: number; // ID del plan en nuestra base de datos
  isPopular?: boolean;
  detail: string;
  isFree?: boolean;
  downloadUrl?: string;
}

interface SubscriptionCheck {
  hasActiveSubscription: boolean;
  currentSubscription: {
    id: number;
    planName: string;
    planPrice: string;
    status: string;
    nextBillingDate: string;
  } | null;
  availablePlans: Array<{
    id: number;
    name: string;
    price: string;
    paypalPlanId: string;
    isFree: boolean;
  }>;
}

const PricingCard = ({
  name,
  description,
  features,
  price,
  plan_id,
  databasePlanId,
  isPopular = false,
  detail,
  isFree = false,
  downloadUrl = "/marketing/instalacion",

}: Props) => {
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionCheck | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  // Verificar estado de suscripción al cargar
  useEffect(() => {
    const checkSubscription = async () => {
      try {
        const response = await fetch('/api/subscriptions/check-current', {
          method: 'GET',
          credentials: 'include' // Include cookies in the request
        });

        const result = await response.json();
        
        if (result.ok) {
          setSubscriptionStatus(result);
        } else if (result.error?.includes("no autenticado")) {
          setError("Debes iniciar sesión para suscribirte");
        } else {
          setError(result.error || "Error al verificar suscripción");
        }
      } catch (error) {
        console.error("Error checking subscription:", error);
        setError("Error de conexión");
      } finally {
        setLoading(false);
      }
    };

    if (!isFree) {
      checkSubscription();
    } else {
      setLoading(false);
    }
  }, [isFree]);

  const handlePlanClick = () => {
    if (isFree) {
      window.location.href = downloadUrl;
    }
  };

  // Mostrar estado de carga
  if (loading) {
    return (
      <div className={`relative flex h-full flex-col rounded-2xl border border-gray-200 bg-white p-8 shadow-lg ${
        isPopular ? "ring-2 ring-red-500 ring-offset-2" : ""
      }`}>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Verificando suscripción...</span>
        </div>
      </div>
    );
  }

  // Mostrar error de autenticación
  if (error && !isFree) {
    return (
      <div className={`relative flex h-full flex-col rounded-2xl border border-gray-200 bg-white p-8 shadow-lg ${
        isPopular ? "ring-2 ring-red-500 ring-offset-2" : ""
      }`}>
        <div className="flex items-center justify-center h-64 flex-col">
          <p className="text-red-600 mb-4">{error}</p>
          <button
            onClick={() => window.location.href = '/auth/login?next=/marketing/planes'}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Iniciar Sesión
          </button>
        </div>
      </div>
    );
  }

  // Verificar si usuario ya tiene suscripción activa
  const hasActiveSubscription = subscriptionStatus?.hasActiveSubscription;
  const currentSubscription = subscriptionStatus?.currentSubscription;

  return (
    <div
      className={`relative flex h-full flex-col rounded-2xl border border-gray-200 bg-white p-8 shadow-lg transition-all duration-300 hover:shadow-2xl ${
        isPopular ? "ring-2 ring-red-500 ring-offset-2" : ""
      }`}
    >
      {/* --- Badge "Más Popular" --- */}
      {isPopular && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2 transform rounded-full bg-red-600 px-4 py-1.5 text-sm font-semibold text-white">
          Más Popular
        </div>
      )}

      {/* --- Encabezado: Nombre y Descripción --- */}
      <div className="mb-6 text-center">
        <h3 className="mb-2 text-2xl font-bold text-black">
          {name}
        </h3>
        <p className="text-gray-600">{description}</p>
      </div>

      {/* --- Precio --- */}
      <div className="mb-8 border-y border-gray-200 py-6">
        <div className="flex items-baseline justify-center gap-1">
          <span className="text-2xl font-semibold text-gray-800">
            $
          </span>
          <span
            className={`text-6xl font-extrabold tracking-tight ${
              isPopular ? "text-red-600" : "text-black"
            }`}
          >
            {price}
          </span>
        </div>
        <span className="mt-1 block text-center text-sm text-gray-600">
          por mes
        </span>
      </div>

      {/* --- Lista de Características --- */}
      <div className="mb-8 flex-1">
        <ul role="list" className="space-y-4 text-left">
          {features.map((feature, i) => (
            <li className="flex items-start space-x-3" key={`${plan_id}_${i}`}>
              <div className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-red-100">
                <svg
                  className="h-4 w-4 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2.5}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <span className="text-black">
                {feature}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* --- Botón de Acción (CTA) --- */}
      <div className="mt-auto">
        {isFree ? (
          <button
            onClick={handlePlanClick}
            className={`group relative flex h-12 w-full cursor-pointer items-center justify-center rounded-lg transition-all duration-300 ${
              isPopular
                ? "bg-red-600 text-white shadow-lg hover:bg-red-700"
                : "bg-white text-red-600 ring-1 ring-red-600 hover:bg-red-50"
            }`}
          >
            <span className="text-lg font-semibold">
              Descargar Gratis
            </span>
          </button>
        ) : hasActiveSubscription ? (
          <div className="text-center">
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 font-semibold">
                Suscripción Activa: {currentSubscription?.planName}
              </p>
              <p className="text-green-600 text-sm">
                Ya tienes una suscripción activa
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <PayPalProvider>
              <ButtonPaypal
                planId={plan_id}
                planName={name}
                databasePlanId={databasePlanId}
              />
            </PayPalProvider>
          </div>
        )}
      </div>
      <div className="mt-4">
        <p className="text-gray-700">{detail}</p>
      </div>
    </div>
  );
};

export default PricingCard;