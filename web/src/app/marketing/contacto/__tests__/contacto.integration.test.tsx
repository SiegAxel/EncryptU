/**
 * @jest-environment jsdom
 */

import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ContactPage from "@/app/marketing/contacto/page";

// mock de fetch tipado
let fetchMock: jest.MockedFunction<typeof fetch>;

describe("Integración: página de Contacto / Soporte", () => {
  beforeEach(() => {
    fetchMock = jest.fn() as unknown as jest.MockedFunction<typeof fetch>;
    global.fetch = fetchMock as unknown as typeof fetch;
  });

  test("envía el formulario (llama a la API) cuando todos los campos son válidos", async () => {
    fetchMock.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        ok: true,
        message: "Mensaje enviado correctamente",
      }),
    } as Response);

    render(<ContactPage />);

    const user = userEvent.setup();

    // Rellenar TODOS los campos obligatorios según tu HTML
    await user.type(screen.getByLabelText(/nombre/i), "Juan Pérez");
    await user.type(screen.getByLabelText(/apellido/i), "González");
    await user.type(
      screen.getByLabelText(/correo electrónico/i),
      "juan.perez@example.com"
    );

    // Motivo: seleccionar "Soporte"
    await user.selectOptions(
      screen.getByLabelText(/motivo/i),
      "soporte"
    );

    // Teléfono: 9 dígitos
    await user.type(
      screen.getByLabelText(/número de teléfono/i),
      "987654321"
    );

    // Descripción
    await user.type(
      screen.getByLabelText(/descripción/i),
      "Tengo un problema con la instalación"
    );

    await user.click(
      screen.getByRole("button", { name: /enviar formulario/i })
    );

    // Esperamos a que se llame a fetch → integración formulario + API
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(1);
    });

    // Si quieres, puedes inspeccionar qué se envió:
    // const [url, options] = fetchMock.mock.calls[0];
    // expect(url).toMatch(/api/i);
    // expect((options as RequestInit).method).toBe("POST");
  });
});
