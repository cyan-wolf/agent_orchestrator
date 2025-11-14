import { ThemeProvider } from "@emotion/react";
import { alpha, createTheme, CssBaseline, GlobalStyles, responsiveFontSizes } from "@mui/material";
import { blue, brown, green, purple, red, yellow } from "@mui/material/colors";
import type { Theme } from "@mui/material/styles";
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

type CustomTheme = {
    mainColor: string,
    paperColor: string,
    backgroundColor: string,
    mode?: 'light' | 'dark',
};

export type CustomThemeKind = 
    | "gold-crimson" 
    | "light-blue" 
    | "light-monochrome" 
    | "dark-purple" 
    | "dark-green" 
    | "dark-red"
    | "nature"

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
    "light-monochrome": {
        mainColor: "#3a3a3aff",
        paperColor: "#f5f5f5ff",
        backgroundColor: "#ffffff",
    },
    "dark-purple": {
        mainColor: purple[300],
        paperColor: "#161616ff",
        backgroundColor: "#000000",
        
        mode: 'dark',
    },
    "dark-green": {
        mainColor: green[300],
        paperColor: "#161616ff",
        backgroundColor: "#000000",
        
        mode: 'dark',
    },
    "dark-red": {
        mainColor: red[300],
        paperColor: "#161616ff",
        backgroundColor: "#000000",
        
        mode: 'dark',
    },
    "nature": {
        mainColor: brown[400],
        paperColor: green[100],
        backgroundColor: green[50],
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

    const globalSelectionStyles = (
        <GlobalStyles
            styles={(theme) => {
                // Adjust selection color for dark mode as dark mode themes tend to have 
                // brigher main colors.
                const selectionBgColor = (theme.palette.mode === 'dark') ? 
                    alpha(theme.palette.primary.main, 0.5) : theme.palette.primary.main;

                return {
                    '::selection': {
                        backgroundColor: selectionBgColor, 
                        color: theme.palette.common.white, 
                    },
                    // For Firefox.
                    '::-moz-selection': { 
                        backgroundColor: selectionBgColor,
                        color: theme.palette.common.white,
                    },
                };
            }}
        />
    );

    return (
        <CustomThemeContext.Provider value={value}>
            <ThemeProvider
                theme={createMUIThemeFromCustomTheme(CUSTOM_THEMES[customThemeKind])}
            >
                <CssBaseline />
                {globalSelectionStyles}
                {children}
            </ThemeProvider>
        </CustomThemeContext.Provider>
    );
}

export const useCustomTheme = () => useContext(CustomThemeContext);
