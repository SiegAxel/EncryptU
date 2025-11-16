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
  databasePlanId: number;
}

const ButtonPaypal: React.FC<ButtonPaypalProps> = ({
  planId,
  planName = "Plan",
  databasePlanId
}) => {
  const [{ isPending }] = usePayPalScriptReducer();
  const [isProcessing, setIsProcessing] = useState(false);
  const [authError, setAuthError] = useState<string>("");

  const onApprove: PayPalButtonOnApprove = async (data) => {
    setIsProcessing(true);
    
    try {
      if (data.subscriptionID) {
        console.log(`PayPal subscription approved: ${data.subscriptionID}`);
        alert(`¡Suscripción creada exitosamente!\n\nPlan: ${planName}\nID de Suscripción: ${data.subscriptionID}\n\nRecibirás una confirmación por email en los próximos minutos.`);
        // Refresh page to show updated subscription
        setTimeout(() => {
          window.location.reload();
        }, 2000);
      }
    } catch {
      console.error("Error processing PayPal subscription");
      alert("Error al procesar la suscripción. Por favor, contacta al soporte.");
    } finally {
      setIsProcessing(false);
    }
  };

  const createSubscription: PayPalButtonCreateSubscription = async (
    data,
    actions
  ) => {
    console.log(`🚀 Starting PayPal subscription for plan: ${planName} (ID: ${databasePlanId})`);
    
    try {
      // Pre-authorize right before creating the subscription
      console.log(`🔍 Pre-authorizing subscription for plan: ${planName} (ID: ${databasePlanId})`);
      
      const response = await fetch('/api/subscriptions/pre-authorize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ planId: databasePlanId })
      });

      console.log(`📡 Pre-auth response status: ${response.status}`);
      const result = await response.json();
      console.log(`📋 Pre-auth response:`, result);
      
      if (!result.ok) {
        throw new Error(result.error || "Error al pre-autorizar suscripción");
      }

      console.log(`✅ Pre-authorized: ${result.planName} - Creating PayPal subscription`);
      
      return actions.subscription.create({
        plan_id: planId
      });
    } catch (error) {
      console.error("❌ Pre-authorization or subscription creation failed:", error);
      throw error;
    }
  };

  if (authError) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800">
        <p className="text-sm mb-2">{authError}</p>
        <button
          onClick={() => window.location.href = '/auth/login?next=/marketing/planes'}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm"
        >
          Iniciar Sesión
        </button>
      </div>
    );
  }

  // No pre-authorization state needed - it's handled in createSubscription

  if (isProcessing) {
    return (
      <button
        disabled
        className="w-full h-12 bg-blue-600 text-white rounded-lg cursor-not-allowed flex items-center justify-center"
      >
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white mr-2"></div>
        Procesando suscripción...
      </button>
    );
  }

  return (
    <div className="w-full space-y-4">
      {isPending && (
        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-800 text-center">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-yellow-600 mr-2"></div>
            Cargando opciones de pago...
          </div>
        </div>
      )}
      
      <div className="space-y-2">
        <PayPalButtons
          fundingSource="paypal"
          style={{ 
            layout: "vertical",
            color: "gold",
            shape: "rect",
            label: "subscribe",
            height: 45
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
      </div>
    </div>
  );
};

export default ButtonPaypal;
