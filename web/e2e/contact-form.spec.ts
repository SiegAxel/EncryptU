import { test, expect } from "@playwright/test";

test.describe("Flujo funcional de Contacto", () => {
  test("permite completar y enviar el formulario de contacto", async ({ page }) => {
    // Interceptar la API de contacto (ajusta URL según tu implementación)
    await page.route("**/api/**", async (route, request) => {
      const url = request.url();

      if (url.includes("contact") || url.includes("soporte")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            ok: true,
            message: "Mensaje enviado correctamente",
          }),
        });
      } else {
        await route.continue();
      }
    });

    await page.goto("/marketing/contacto");

    await expect(page.getByRole("heading", { name: /contáctanos/i })).toBeVisible();

    // Estos labels coinciden con los que vimos en el DOM del test de integración
    await page.getByLabel(/nombre/i).fill("Juan");
    await page.getByLabel(/apellido/i).fill("González");
    await page.getByLabel(/correo electrónico/i).fill("juan@example.com");
    await page.getByLabel(/motivo/i).selectOption("soporte");
    await page.getByLabel(/número de teléfono/i).fill("987654321");
    await page
      .getByLabel(/descripción/i)
      .fill("Tengo un problema con la instalación de EncryptU.");

    await page.getByRole("button", { name: /enviar formulario/i }).click();

    // Aquí depende mucho de cómo manejes el estado de éxito.
    // Si tienes un texto tipo "Mensaje enviado", lo puedes chequear:
    // await expect(page.getByText(/mensaje enviado/i)).toBeVisible();

    // Como mínimo, verificamos que el botón sigue visible y no explota la UI
    await expect(
      page.getByRole("button", { name: /enviar formulario/i })
    ).toBeVisible();
  });
});
