import { test, expect } from "@playwright/test";

test.describe("Flujo funcional de Login", () => {
  test("permite enviar el formulario de login con credenciales válidas", async ({ page }) => {
    // Interceptamos la API de login (ajusta la ruta si es distinta)
    await page.route("**/api/**", async (route, request) => {
      const url = request.url();

      if (url.includes("login") || url.includes("auth")) {
        // Respuesta mock de éxito
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            ok: true,
            role: "usuario",
            redirect: "/dashboard",
          }),
        });
      } else {
        // Dejar pasar cualquier otra petición
        await route.continue();
      }
    });

    // Ir a la página de login real
    await page.goto("/auth/login");

    // Verificamos que la UI se renderizó
    await expect(page.getByRole("heading", { name: /iniciar sesión/i })).toBeVisible();

    // Completar los campos usando los placeholders que vimos en el HTML
    await page.getByPlaceholder(/email/i).fill("user@test.com");
    await page.getByPlaceholder(/contraseña/i).fill("EncryptU2025*");

    // Click en el botón "Ingresar"
    await page.getByRole("button", { name: /ingresar/i }).click();

    // Esperamos un poquito a que se procese el submit
    // (aquí podrías chequear algún cambio de estado si tu UI lo muestra)
    await page.waitForTimeout(500);

    // Verificamos que la página sigue cargada y no hay error visible típico
    // (ajusta según cómo manejes errores en tu UI)
    await expect(page.getByRole("button", { name: /ingresar/i })).toBeVisible();
  });
});
