/** @type {import('jest').Config} */
module.exports = {
  // jsdom por defecto (para tests de React)
  testEnvironment: "jsdom",

  transform: {
    "^.+\\.(t|j)sx?$": [
      "ts-jest",
      {
        tsconfig: "<rootDir>/tsconfig.jest.json",
      },
    ],
  },

  moduleNameMapper: {
    "^@/(.*)$": "<rootDir>/src/$1",
  },

  setupFilesAfterEnv: ["<rootDir>/jest.setup.ts"],

  // 👇 MUY IMPORTANTE: Jest NO debe tocar la carpeta de Playwright
  testPathIgnorePatterns: ["<rootDir>/e2e/"],
};
