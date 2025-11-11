import { ThemeProvider } from "@emotion/react";
import { createTheme, responsiveFontSizes } from "@mui/material";
import { blue, purple, red, yellow } from "@mui/material/colors";
import type { Theme } from "@mui/material/styles";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type CustomTheme = {
    mainColor: string,
    paperColor: string,
    backgroundColor: string,
    mode?: 'light' | 'dark',
};

export type CustomThemeKind = "gold-crimson" | "light-blue" | "dark-purple";

export const CUSTOM_THEMES: Record<CustomThemeKind, CustomTheme> = {
    "gold-crimson": {
        mainColor: red[500],
        paperColor: yellow[100],
        backgroundColor: yellow[50],
    },
    "light-blue": {
        mainColor: blue[900],
        paperColor: "#e0e0e0ff",
        backgroundColor: "#ffffff",
    },
    "dark-purple": {
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

const CUSTOM_THEME_STORAGE_KEY = "agent-orchestrator-custom-theme-kind";

const DEFAULT_CUSTOM_THEME_KIND: CustomThemeKind = "gold-crimson";

export function CustomThemeProvider({ children }: { children: ReactNode }) {
    const [customThemeKind, setCustomThemeKind] = useState<CustomThemeKind>(() => {
        try {
            const storedThemeKind = localStorage.getItem(CUSTOM_THEME_STORAGE_KEY);
            
            if (! Object.hasOwn(CUSTOM_THEMES, storedThemeKind as CustomThemeKind)) {
                return DEFAULT_CUSTOM_THEME_KIND;
            }
            return storedThemeKind as CustomThemeKind;
        }
        catch (err) {
            console.error("Error while saving app theme: ", err);
            return DEFAULT_CUSTOM_THEME_KIND;
        }
    });

    useEffect(() => {
        try {
            localStorage.setItem(CUSTOM_THEME_STORAGE_KEY, customThemeKind);
        }
        catch (err) {
            console.error("Error while saving app theme: ", err);
        }
    }, [customThemeKind]);

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
