"use client";

import { PayPalButtons, usePayPalScriptReducer } from "@paypal/react-paypal-js";
import {
  PayPalButtonCreateSubscription,
  PayPalButtonOnApprove,
} from "@paypal/paypal-js";
import React, { useState } from "react";

interface ButtonPaypalProps {
  planId: string;
  planName?: string;
  planPrice?: string;
}

const ButtonPaypal: React.FC<ButtonPaypalProps> = ({
  planId,
  planName = "Plan",
  planPrice = ""
}) => {
  const [{ isPending }] = usePayPalScriptReducer();
  const [isProcessing, setIsProcessing] = useState(false);

  const onApprove: PayPalButtonOnApprove = async (data, actions) => {
    setIsProcessing(true);
    
    try {
      if (data.subscriptionID) {
        console.log(`PayPal subscription created successfully: ${data.subscriptionID}`);
        
        // Optional: Update your backend about the successful subscription creation
        // You could call an API here to create/update the subscription record immediately
        // This is a fallback since the webhook should handle the database updates
        
        alert(`¡Suscripción creada exitosamente!\n\nPlan: ${planName}\nID de Suscripción: ${data.subscriptionID}\n\nRecibirás una confirmación por email en los próximos minutos.`);
      }
    } catch (error) {
      console.error("Error processing PayPal subscription:", error);
      alert("Error al procesar la suscripción. Por favor, contacta al soporte.");
    } finally {
      setIsProcessing(false);
    }
  };

  const createSubscription: PayPalButtonCreateSubscription = (
    data,
    actions
  ) => {
    console.log(`Creating PayPal subscription for plan: ${planId}`);
    
    return actions.subscription.create({
      plan_id: planId,
    });
  };

  if (isProcessing) {
    return (
      <div className="flex items-center justify-center p-4 bg-blue-50 rounded-lg">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-blue-600">Procesando suscripción...</span>
      </div>
    );
  }

  return (
    <div className="w-full">
      {isPending && (
        <div className="mb-4 p-2 bg-yellow-50 border border-yellow-200 rounded text-yellow-800">
          Cargando opciones de pago...
        </div>
      )}
      
      <PayPalButtons
        fundingSource="paypal"
        style={{
          layout: "vertical",
          color: "gold",
          shape: "rect",
          label: "subscribe"
        }}
        disabled={false}
        createSubscription={createSubscription}
        onApprove={onApprove}
        onError={(error) => {
          console.error("PayPal Button Error:", error);
          alert("Error al cargar PayPal. Por favor, intenta de nuevo.");
        }}
        onCancel={() => {
          console.log("PayPal subscription was cancelled by user");
        }}
      />
      
      <p className="text-xs text-gray-500 mt-2 text-center">
        Al suscribirte, aceptas los términos y condiciones de PayPal y nuestra política de privacidad.
      </p>
    </div>
  );
};

export default ButtonPaypal;
