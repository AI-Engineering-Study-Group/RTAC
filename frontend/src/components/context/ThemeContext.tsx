import { createContext, useState, useEffect,ReactNode } from "react";

type Theme = "light" | "dark";

interface ThemeContextType {
    theme: Theme;
    toggleTheme: () => void;
}

export const ThemeContext = createContext<ThemeContextType>({
    theme: "light",
    toggleTheme: () => {},

});

interface ThemeProviderProps {
    children: ReactNode;
}

export const ThemeProvider:React.FC<ThemeProviderProps> = ({children}) => {
    const [theme, setTheme] =useState<Theme>("light")
    ;
    useEffect(() => {
    const savedTheme = localStorage.getItem("chat-app-theme") as Theme;
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.setAttribute("data-theme", savedTheme);
    }
  }, []);

  const toggleTheme = () => {
    const newTheme = theme === "light" ? "dark" : "light";
    setTheme(newTheme);
    localStorage.setItem("chat-app-theme", newTheme);
    document.documentElement.setAttribute("data-theme", newTheme);
  };
   return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};











