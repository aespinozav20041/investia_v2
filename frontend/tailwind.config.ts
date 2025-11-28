import type { Config } from "tailwindcss";
import { fontFamily } from "tailwindcss/defaultTheme";

const config: Config = {
  darkMode: ["class"],
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#f5f8ff",
          100: "#e5edff",
          200: "#cddaff",
          300: "#99b6ff",
          400: "#648fff",
          500: "#3563ff",
          600: "#1d45d8",
          700: "#1736aa",
          800: "#11287c",
          900: "#0a1b4f"
        }
      },
      fontFamily: {
        sans: ["Inter", ...fontFamily.sans]
      }
    }
  },
  plugins: [require("tailwindcss-animate")]
};

export default config;
