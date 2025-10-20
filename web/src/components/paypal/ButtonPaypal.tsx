"use client";

import { PayPalButtons, usePayPalScriptReducer } from "@paypal/react-paypal-js";
import {
  PayPalButtonCreateSubscription,
  PayPalButtonOnApprove,
} from "@paypal/paypal-js";
import React from "react";

const onApprove: PayPalButtonOnApprove = async (data, actions) => {
  if (actions.order) {
    const details = await actions.order.capture();

    alert(
      "Transaction completed by " +
        details.payment_source?.paypal?.name?.full_name
    );
  }
};

const ButtonPaypal = ({ planId }: { planId: string }) => {
  const [{ isPending }] = usePayPalScriptReducer();

  const createSubscription: PayPalButtonCreateSubscription = (
    data,
    actions
  ) => {
    return actions.subscription.create({
      plan_id: planId,
    });
  };

  return (
    <>
      {isPending && <div className="spinner">Cargando</div>}
      <PayPalButtons
        fundingSource="paypal"
        style={{ layout: "vertical" }}
        disabled={false}
        createSubscription={createSubscription}
        onApprove={onApprove}
      />
    </>
  );
};

export default ButtonPaypal;
