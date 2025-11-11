import { ThemeProvider } from "@emotion/react";
import { createTheme, responsiveFontSizes } from "@mui/material";
import { blue, purple, red, yellow } from "@mui/material/colors";
import type { Theme } from "@mui/material/styles";
import { createContext, useContext, useState, type ReactNode } from "react";

type CustomTheme = {
    mainColor: string,
    paperColor: string,
    backgroundColor: string,
    mode?: 'light' | 'dark',
};

type CustomThemeKind = "crimson-gold" | "light" | "dark";

export const CUSTOM_THEMES: Record<CustomThemeKind, CustomTheme> = {
    "crimson-gold": {
        mainColor: red[500],
        paperColor: yellow[100],
        backgroundColor: yellow[50],
    },
    "light": {
        mainColor: blue[900],
        paperColor: "#e0e0e0ff",
        backgroundColor: "#ffffff",
    },
    "dark": {
        mainColor: purple[300],
        paperColor: "#161616ff",
        backgroundColor: "#000000",
        
        mode: 'dark',
    },
};

type CustomThemeData = {
    customThemeKind: CustomThemeKind,
    setCustomThemeKind: (kind: CustomThemeKind) => void,
}

const CustomThemeContext = createContext<CustomThemeData | null>(null);

function createMUIThemeFromCustomTheme(customTheme: CustomTheme): Theme {
    return responsiveFontSizes(createTheme({
      palette: {
        mode: customTheme.mode,
        primary: {
          main: customTheme.mainColor,
        },
        background: {
          default: customTheme.backgroundColor,
          paper: customTheme.paperColor,
        },
      },
    }));
}

export function CustomThemeProvider({ children }: { children: ReactNode }) {
    const [customThemeKind, setCustomThemeKind] = useState<CustomThemeKind>("crimson-gold");

    const value = {
        customThemeKind,
        setCustomThemeKind,
    };

    return (
        <CustomThemeContext.Provider value={value}>
            <ThemeProvider
                theme={createMUIThemeFromCustomTheme(CUSTOM_THEMES[customThemeKind])}
            >
                {children}
            </ThemeProvider>
        </CustomThemeContext.Provider>
    );
}

export const useCustomTheme = () => useContext(CustomThemeContext);
