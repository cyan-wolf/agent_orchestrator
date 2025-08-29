import { Alert, Box, Button, Card, CardContent, Container, Divider, InputLabel, MenuItem, Select, TextField, Typography } from "@mui/material";
import { useEffect, useState } from "react";
import { getTimeZones } from '@vvo/tzdb';

// Get the list of time zones and sort them alphabetically.
const timezones = getTimeZones({ includeUtc: true }).sort((a, b) => {
    if (a.name === "Etc/UTC") {
        return -1;
    }
    if (b.name === "Etc/UTC") {
        return 1;
    }
    return a.name.localeCompare(b.name);
});

const validLanguages = ["English", "Spanish", "French", "German", "Russian", "Chinese", "Arabic"];

type Settings = {
    timezone: string,
    language: string,
    city: string | null,
    country: string | null,
};

export default function Settings() {
    const [timezone, setTimezone] = useState("");
    const [language, setLanguage] = useState("");
    const [city, setCity] = useState("");
    const [country, setCountry] = useState("");

    const [cityValidationErrMsg, setCityValidationErrMsg] = useState("");
    const [countryValidationErrMsg, setCountryValdiationErrMsg] = useState("");
    
    const [confirmationMessage, setConfirmationMessage] = useState("");

    useEffect(() => {
        const fetchCurrentSettings = async () => {
            const resp = await fetch('/api/settings/all/');
            const settings: Settings = await resp.json();

            setTimezone(settings.timezone);
            setLanguage(settings.language);
            setCity(settings.city ?? "");
            setCountry(settings.country ?? "");
        };
        fetchCurrentSettings();
    }, []);

    function validateSettings(newSettings: Settings): boolean {
        if (newSettings.city === null || newSettings.city.length > 100) {
            setCityValidationErrMsg("City field is too long.")
            return false;
        }
        else if (newSettings.country === null || newSettings.country.length > 100) {
            setCountryValdiationErrMsg("Country field is too long.");
            return false;
        }
        setCityValidationErrMsg("");
        setCountryValdiationErrMsg("");
        return true;
    }

    async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        const newSettings: Settings = {
            timezone,
            language,
            city, 
            country,
        };

        if (!validateSettings(newSettings)) {
            setConfirmationMessage("");
            return;
        }

        const resp = await fetch('/api/settings/modify-all/', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newSettings),
        });
        const confirmationMsgJson = await resp.json();
        setConfirmationMessage(confirmationMsgJson['result']);
    }

    return (
        <Container>
            <Card>
                <CardContent>
                    <Typography variant="h1" align="center">Settings</Typography>
                    <Divider />

                    <Box>
                        <form onSubmit={onSubmit}>
                            <InputLabel id="label-timezone">Time Zone</InputLabel>
                            <Select
                                labelId="label-timezone"
                                id="select-timezone"
                                value={timezone}
                                label="timezone"
                                onChange={e => setTimezone(e.target.value as string)}
                            >
                                {timezones.map((tz) => (
                                    <MenuItem key={tz.name} value={tz.name}>
                                        {tz.name} (UTC{tz.currentTimeFormat.split(' ')[0]})
                                    </MenuItem>
                                ))}
                            </Select>

                            <InputLabel id="label-language">Language</InputLabel>
                            <Select
                                labelId="label-language"
                                id="select-langauge"
                                value={language}
                                label="Language"
                                onChange={e => setLanguage(e.target.value as string)}
                            >
                                {validLanguages.map((lang) => (
                                    <MenuItem key={lang} value={lang}>
                                        {lang}
                                    </MenuItem>
                                ))}
                            </Select>

                            <TextField 
                                label="City"
                                type="text"
                                value={city}
                                sx={{ display: "block" }}
                                margin="normal"
                                onChange={e => setCity(e.target.value)}
                                helperText={cityValidationErrMsg}
                            />
                            <TextField 
                                label="Country"
                                type="text"
                                value={country}
                                sx={{ display: "block" }}
                                margin="normal"
                                onChange={e => setCountry(e.target.value)}
                                helperText={countryValidationErrMsg}
                            />

                            <Button type="submit" variant="contained">Submit</Button>
                        </form>
                    </Box>

                    {(confirmationMessage.length === 0) ? <></> : (
                        <Alert severity="success">
                            {confirmationMessage}
                        </Alert>
                    )}
                </CardContent>
            </Card>
        </Container>
    );
}