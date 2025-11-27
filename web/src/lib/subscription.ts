import { prisma } from "@/lib/prisma";


export async function assignFreePlanToUser(userId: number) {
  try {
    const freePlan = await prisma.subscriptionPlan.findFirst({
      where: { 
        name: "Básico",
        isActive: true 
      },
      select: { id: true }
    });

    if (!freePlan) {
      console.error("Free plan 'Básico' not found in database");
      return;
    }
    await prisma.userSubscription.create({
      data: {
        userId: userId,
        planId: freePlan.id,
        status: "active",
        startDate: new Date(),
        currency: "USD"
      }
    });

    console.log(` Free plan assigned to user ${userId}`);
  } catch (error) {
    console.error("Error assigning free plan to user:", error);
  }
}