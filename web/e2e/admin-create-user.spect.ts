import { test, expect } from "@playwright/test";

test.describe("Admin - Gestión de usuarios", () => {
  test("permite crear un usuario desde el panel admin", async ({ page }) => {
    // 1️⃣ Interceptar login como admin
    await page.route("**/api/**", async (route, request) => {
      const url = request.url();

      if (url.includes("login")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({
            ok: true,
            role: "admin",
            redirect: "/dashboard/admin",
          }),
        });
        return;
      }

      if (url.includes("crear-user") || url.includes("users")) {
        await route.fulfill({
          status: 200,
          contentType: "application/json",
          body: JSON.stringify({ ok: true, message: "Usuario creado" }),
        });
        return;
      }

      await route.continue();
    });

    // 2️⃣ Login como Admin
    await page.goto("/auth/login");
    await page.getByPlaceholder(/email/i).fill("admin@example.com");
    await page.getByPlaceholder(/contraseña/i).fill("EncryptU2025*");
    await page.getByRole("button", { name: /ingresar/i }).click();

    await expect(page).toHaveURL(/\/dashboard\/admin/);

    // 3️⃣ Ir a Gestión de Usuarios
    await page.getByRole("link", { name: /usuarios|gestión/i }).click();

    // 4️⃣ Abrir formulario de creación
    await page.getByRole("button", { name: /crear usuario/i }).click();

    // 5️⃣ Completar formulario de nuevo usuario
    await page.getByLabel(/nombre/i).fill("Usuario Test");
    await page.getByLabel(/correo|email/i).fill("test@encryptu.com");
    await page.getByLabel(/rol/i).selectOption("usuario");

    // 6️⃣ Enviar
    await page.getByRole("button", { name: /guardar|crear/i }).click();

    // 7️⃣ Confirmar que la petición fue enviada
    await expect(page.getByText(/usuario creado/i)).toBeVisible();
  });
});
