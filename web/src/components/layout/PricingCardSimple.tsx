"use client";

import ButtonPaypal from "@/components/PayPal/ButtonPaypal";
import PayPalProvider from "@/components/PayPal/PayPalProvider";

interface Props {
  name: string;
  description: string;
  features: string[];
  price: string;
  plan_id: string;
  databasePlanId: number;
  isPopular?: boolean;
  detail: string;
  isFree?: boolean;
  downloadUrl?: string;
}

const PricingCardSimple = ({
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
  const handlePlanClick = () => {
    if (isFree) {
      window.location.href = downloadUrl;
    }
  };

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

export default PricingCardSimple;