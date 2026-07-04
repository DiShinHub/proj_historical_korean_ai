import React, { createContext, useContext, ReactNode, useState, useEffect } from "react";
import { CustomTheme as Theme, lightTheme, darkTheme } from ".";

// Context
export const ThemeContext = createContext<{
  theme: Theme;
  toggleTheme: () => void;
}>({
  theme: lightTheme,
  toggleTheme: () => {},
});

// Hook
export const useTheme = () => useContext(ThemeContext);

export const AppThemeProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(lightTheme);
  const [mode, setMode] = useState<"light" | "dark">("light");

  // 초기 로드
  useEffect(() => {
    const stored = localStorage.getItem("theme") as "light" | "dark" | null;

    const initial = stored ?? "light";
    setMode(initial);
    setTheme(initial === "dark" ? darkTheme : lightTheme);
  }, []);

  // body class sync
  useEffect(() => {
    document.body.classList.remove("light", "dark");
    document.body.classList.add(mode);
  }, [mode]);

  // toggle
  const toggleTheme = () => {
    setMode((prev) => {
      const next = prev === "light" ? "dark" : "light";

      setTheme(next === "dark" ? darkTheme : lightTheme);
      localStorage.setItem("theme", next);

      return next;
    });
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};