"use client";

import React, { PropsWithChildren } from "react";
import { PayPalScriptProvider } from "@paypal/react-paypal-js";

const PayPalProvider = ({ children }: PropsWithChildren) => {
  return (
    <PayPalScriptProvider
      options={{
        clientId: process.env.NEXT_PUBLIC_PAYPAL_CLIENT_ID!,
        components: "buttons",
        currency: "USD",
        vault: true,
      }}
    >
      {children}
    </PayPalScriptProvider>
  );
};

export default PayPalProvider;
