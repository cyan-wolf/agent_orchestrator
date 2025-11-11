import { CUSTOM_THEMES, useCustomTheme, type CustomThemeKind } from "./useCustomTheme";
import { Box, Button, Card, CardContent, Container, Typography } from "@mui/material";

type SquareProps = {
    color: string,
};

function Square({ color }: SquareProps) {
  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Box
        sx={{
          width: 40,
          height: 40,
          bgcolor: color, 
          borderRadius: 1,
        }}
      />
    </Box>
  );
}

export default function Themes() {
    const { customThemeKind, setCustomThemeKind } = useCustomTheme()!;

    console.log(customThemeKind);

    return (
        <Container maxWidth="sm">
            <Card>
                <CardContent sx={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center"
                }}>
                    <Typography 
                        variant="h3"
                        align="center"
                        sx={{ mb: 5 }}
                    >
                        Set Theme
                    </Typography>

                    {Object.keys(CUSTOM_THEMES).map(kind => (
                        <Box 
                            key={kind}
                            sx={{
                                display: "flex",
                                width: "100%",
                            }}
                        >
                            <Box
                                sx={{
                                    display: "flex",
                                }}
                            >
                                <Square color={CUSTOM_THEMES[kind as CustomThemeKind].mainColor} />
                                <Square color={CUSTOM_THEMES[kind as CustomThemeKind].backgroundColor} />
                            </Box>
                            <Button
                                variant="outlined"
                                onClick={() => setCustomThemeKind(kind as CustomThemeKind)}
                            >
                                {kind}
                            </Button>
                        </Box>
                    ))}
                </CardContent>

            </Card>
        </Container>
    );
}
