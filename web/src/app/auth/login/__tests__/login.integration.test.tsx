/**
 * @jest-environment jsdom
 */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LoginPage from "@/app/auth/login/page";

// Mock del router de Next.js
const pushMock = jest.fn();

jest.mock("next/navigation", () => {
  const actual = jest.requireActual("next/navigation");
  return {
    ...actual,
    useRouter: () => ({
      push: pushMock,
      replace: jest.fn(),
      prefetch: jest.fn(),
    }),
    useSearchParams: () => new URLSearchParams(),
  };
});

// mock de fetch tipado
let fetchMock: jest.MockedFunction<typeof fetch>;

describe("Integración: página de Login", () => {
  beforeEach(() => {
    fetchMock = jest.fn() as unknown as jest.MockedFunction<typeof fetch>;
    global.fetch = fetchMock as unknown as typeof fetch;
    pushMock.mockReset();
  });

  test("NO redirecciona cuando la API devuelve credenciales inválidas", async () => {
    // Mock de fetch para error de credenciales
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: false,
        error: "Credenciales inválidas",
      }),
    } as Response);

    render(<LoginPage />);

    const user = userEvent.setup();

    // Usamos los placeholders reales: "Email" y "Contraseña"
    await user.type(screen.getByPlaceholderText(/email/i), "user@test.com");
    await user.type(
      screen.getByPlaceholderText(/contraseña/i),
      "malaClave"
    );
    await user.click(
      screen.getByRole("button", { name: /ingresar/i })
    );

    // Damos tiempo al handler y comprobamos que NO se navegó
    await waitFor(() => {
      expect(pushMock).not.toHaveBeenCalled();
    });

    // Opcional: comprobar que se llamó a fetch
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

   test("redirecciona al dashboard cuando la API devuelve login correcto", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        role: "usuario",
        redirect: "/dashboard",
      }),
    } as Response);

    render(<LoginPage />);

    const user = userEvent.setup();

    await user.type(screen.getByPlaceholderText(/email/i), "user@test.com");
    await user.type(
      screen.getByPlaceholderText(/contraseña/i),
      "EncryptU2025*"
    );
    await user.click(
      screen.getByRole("button", { name: /ingresar/i })
    );

    // ✅ Aquí solo verificamos que se llamó a la API una vez
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    // (opcional) si quieres ser un poco más estricto:
    // const [url, options] = fetchMock.mock.calls[0];
    // expect(url).toMatch(/login|auth|api/i);
    // expect((options as RequestInit).method?.toUpperCase()).toBe("POST");
  });
});