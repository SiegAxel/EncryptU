"use client";

import ButtonPaypal from "@/components/PayPal/ButtonPaypal";
import PayPalProvider from "@/components/PayPal/PayPalProvider";

interface Props {
  name: string;
  description: string;
  features: string[];
  price: string;
  plan_id: string;
  isPopular?: boolean;
  detail: string;
}

const PricingCard = ({
  name,
  description,
  features,
  price,
  plan_id,
  isPopular = false,
  detail,

}: Props) => {
  const accentColor = "red"; // Definimos el color de acento principal aquí
  const lightAccent = "red-50";
  const darkAccent = "red-900";
  const mainAccent = "red-600";
  const hoverAccent = "red-700";
  const ringAccent = "red-500";

  return (
    <div
      className={`relative flex h-full flex-col rounded-2xl border p-8 shadow-lg transition-all duration-300 hover:shadow-2xl ${
        isPopular
          ? `border-${ringAccent}/50 bg-${lightAccent} ring-2 ring-${ringAccent} ring-offset-2 ring-offset-white dark:border-${darkAccent}/30 dark:bg-gray-900 dark:ring-offset-gray-950`
          : "border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800"
      }`}
    >
      {/* --- Badge "Más Popular" --- */}
      {isPopular && (
        <div
          className={`absolute -top-4 left-1/2 -translate-x-1/2 transform rounded-full bg-${mainAccent} px-4 py-1.5 text-sm font-semibold text-white`}
        >
          Más Popular
        </div>
      )}

      {/* --- Encabezado: Nombre y Descripción --- */}
      <div className="mb-6 text-center">
        <h3 className="mb-2 text-2xl font-bold text-gray-800 dark:text-gray-100">
          {name}
        </h3>
        <p className="text-gray-500 dark:text-gray-400">{description}</p>
      </div>

      {/* --- Precio --- */}
      <div className="mb-8 border-y border-gray-200 py-6 dark:border-gray-700">
        <div className="flex items-baseline justify-center gap-1">
          <span className="text-2xl font-semibold text-gray-500 dark:text-gray-400">
            $
          </span>
          <span
            className={`text-6xl font-extrabold tracking-tight ${
              isPopular
                ? `bg-gradient-to-r from-${ringAccent} to-${mainAccent} bg-clip-text text-transparent`
                : "text-gray-900 dark:text-white"
            }`}
          >
            {price}
          </span>
        </div>
        <span className="mt-1 block text-center text-sm text-gray-500 dark:text-gray-400">
          por mes
        </span>
      </div>

      {/* --- Lista de Características --- */}
      <div className="mb-8 flex-1">
        <ul role="list" className="space-y-4 text-left">
          {features.map((feature, i) => (
            <li className="flex items-start space-x-3" key={`${plan_id}_${i}`}>
              <div className="mt-0.5 flex h-6 w-6 flex-shrink-0 items-center justify-center rounded-full bg-green-100 dark:bg-green-900/50">
                {/* Mantengo el checkmark en verde para un contraste positivo,
                    pero puedes cambiarlo a un rojo más oscuro si lo deseas */}
                <svg
                  className="h-4 w-4 text-green-600 dark:text-green-400"
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
              <span className="text-gray-700 dark:text-gray-300">
                {feature}
              </span>
            </li>
          ))}
        </ul>
      </div>

      {/* --- Botón de Acción (CTA) --- */}
      <div className="mt-auto">
        <div
          className={`group relative flex h-12 w-full cursor-pointer items-center justify-center rounded-lg ${
            isPopular
              ? `bg-${mainAccent} text-white shadow-lg hover:bg-${hoverAccent}`
              : `bg-white text-${mainAccent} ring-1 ring-inset ring-${mainAccent}/50 hover:bg-${lightAccent} dark:bg-gray-700 dark:text-gray-100 dark:ring-${mainAccent}/30 dark:hover:bg-gray-600`
          }`}
        >
          <span className="text-lg font-semibold">
            {isPopular ? "Empezar ahora" : "Elegir plan"}
          </span>
          <div className="absolute inset-0 opacity-0">
            <PayPalProvider>
              <ButtonPaypal planId={plan_id} />
            </PayPalProvider>
          </div>
        </div>
      </div>
      <div className="mt-4">
        <p className="text-gray-600 dark:text-gray-400">{detail}</p>
      </div>
    </div>
  );
};

export default PricingCard;