"use client";

import ButtonPaypal from "../paypal/ButtonPaypal";
import PayPalProvider from "../paypal/PayPalProvider";

interface Props {
  name: string;
  description: string;
  features: string[];
  price: string;
  plan_id: string;
  isPopular?: boolean;
}

const PricingCard = ({
  name,
  description,
  features,
  price,
  plan_id,
  isPopular = false,
}: Props) => {
  return (
    <div
      className={`relative flex flex-col p-8 mx-auto max-w-lg text-center rounded-2xl border shadow-xl transition-all duration-300 hover:scale-105 hover:shadow-2xl ${
        isPopular
          ? "border-blue-500 bg-gradient-to-br from-blue-50 to-white dark:from-blue-900/20 dark:to-gray-900"
          : "border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800"
      }`}
    >
      {isPopular && (
        <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-red-300 text-white px-4 py-1 rounded-full text-sm font-semibold">
          Más Popular
        </div>
      )}

      <div className="mb-6">
        <h3 className="mb-3 text-3xl font-bold bg-gradient-to-r from-red-300 to-red-600 bg-clip-text text-transparent">
          {name}
        </h3>
        <p className="text-gray-600 dark:text-gray-400 text-base leading-relaxed">
          {description}
        </p>
      </div>

      <div className="mb-8 py-6 border-y border-gray-200 dark:border-gray-700">
        <div className="flex justify-center items-baseline gap-2">
          <span className="text-2xl font-semibold text-gray-500 dark:text-gray-400">
            $
          </span>
          <span className="text-6xl font-extrabold bg-gradient-to-r from-red-300 to-red-600 bg-clip-text text-transparent">
            {price}
          </span>
        </div>
        <span className="text-gray-500 dark:text-gray-400 text-sm mt-2 block">
          por mes
        </span>
      </div>

      <div className="flex-1 mb-8">
        <ul role="list" className="space-y-4 text-left">
          {features.map((f, i) => (
            <li
              className="flex items-start space-x-3 group"
              key={`${plan_id}_${i}_${f}`}
            >
              <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mt-0.5">
                <svg
                  className="w-4 h-4 text-green-600 dark:text-green-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <span className="text-gray-700 dark:text-gray-300 group-hover:text-gray-900 dark:group-hover:text-white transition-colors">
                {f}
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div className="mt-auto">
        <PayPalProvider>
          <ButtonPaypal planId={plan_id} />
        </PayPalProvider>
      </div>
    </div>
  );
};

export default PricingCard;
