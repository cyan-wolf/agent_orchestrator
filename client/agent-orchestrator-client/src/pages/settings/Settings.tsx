import { Alert, Box, Button, Card, CardContent, Container, FormControl, InputLabel, MenuItem, Paper, Select, TextField, Typography } from "@mui/material";
import { useEffect, useRef, useState } from "react";
import { getTimeZones } from '@vvo/tzdb';
import Loading from "../../components/loading/Loading";

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

type EditableUserProfile = {
    email: string,
    full_name: string,
};

type Settings = {
    timezone: string,
    language: string,
    city: string,
    country: string,

    profile: EditableUserProfile,
};

export default function Settings() {
    const [timezone, setTimezone] = useState("");
    const [language, setLanguage] = useState("");
    const [city, setCity] = useState("");
    const [country, setCountry] = useState("");

    const [fullName, setFullName] = useState("");
    const [email, setEmail] = useState("");

    const [cityValidationErrMsg, setCityValidationErrMsg] = useState("");
    const [countryValidationErrMsg, setCountryValdiationErrMsg] = useState("");

    const [fullNameValidationErrMsg, setFullNameValdiationErrMsg] = useState("");
    const [emailValidationErrMsg, setEmailValdiationErrMsg] = useState("");
    
    const [confirmationMessage, setConfirmationMessage] = useState("");

    const [waitingForServer, setWaitingForServer] = useState(false);

    // For scrolling to the success alert box.
    const successAlertRef = useRef<HTMLDivElement>(null);
    useEffect(() => {
        if (successAlertRef?.current !== null) {
            // Scrolls to the the success alert box.
            successAlertRef.current!.scrollIntoView({ behavior: "smooth" });
        }
    }, [waitingForServer]);

    useEffect(() => {
        const fetchCurrentSettings = async () => {
            const resp = await fetch('/api/settings/all/');
            const settings: Settings = await resp.json();

            setTimezone(settings.timezone);
            setLanguage(settings.language);
            setCity(settings.city ?? "");
            setCountry(settings.country ?? "");

            setFullName(settings.profile.full_name);
            setEmail(settings.profile.email);
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
        else if (newSettings.profile.full_name === null || newSettings.profile.full_name.length > 100) {
            setFullNameValdiationErrMsg("Full name field is too long.");
            return false;
        }
        else if (newSettings.profile.email === null || newSettings.profile.email.length > 100) {
            setEmailValdiationErrMsg("Email field is too long.");
            return false;
        }
        
        setCityValidationErrMsg("");
        setCountryValdiationErrMsg("");
        setFullNameValdiationErrMsg("");
        setEmailValdiationErrMsg("");
        return true;
    }

    async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();

        setConfirmationMessage("");

        const newSettings: Settings = {
            timezone,
            language,
            city, 
            country,
            profile: {
                email,
                full_name: fullName,
            }
        };

        if (!validateSettings(newSettings)) {
            return;
        }

        setWaitingForServer(true);

        const resp = await fetch('/api/settings/modify-all/', {
            method: "POST",
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(newSettings),
        });
        const confirmationMsgJson = await resp.json();
        setConfirmationMessage(confirmationMsgJson['result']);

        setWaitingForServer(false);
    }

    return (
        <Container>
            <Card>
                <CardContent>
                    <Typography variant="h1" align="center">Settings</Typography>

                    <Box>
                        <Paper
                            elevation={8}
                            sx={{
                                ml: { xs: 0, md: 12 }, // 0 margin on 'xs' screens, 12 on 'md' and up
                                mr: { xs: 0, md: 12 }, // 0 margin on 'xs' screens, 12 on 'md' and up

                                // Padding all sides
                                p: { xs: 2, md: 5 },            
                            }}
                        >
                            <form onSubmit={onSubmit}>
                                <FormControl fullWidth margin="normal">
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
                                </FormControl>

                                <FormControl fullWidth margin="normal">
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
                                </FormControl>

                                <TextField 
                                    label="City"
                                    type="text"
                                    value={city}
                                    sx={{ display: "block" }}
                                    margin="normal"
                                    onChange={e => setCity(e.target.value)}
                                    helperText={cityValidationErrMsg}
                                    error={!!cityValidationErrMsg}
                                />
                                <TextField 
                                    label="Country"
                                    type="text"
                                    value={country}
                                    sx={{ display: "block" }}
                                    margin="normal"
                                    onChange={e => setCountry(e.target.value)}
                                    helperText={countryValidationErrMsg}
                                    error={!!countryValidationErrMsg}
                                />

                                <TextField 
                                    label="Full Name"
                                    type="text"
                                    value={fullName}
                                    sx={{ display: "block" }}
                                    margin="normal"
                                    onChange={e => setFullName(e.target.value)}
                                    helperText={fullNameValidationErrMsg}
                                    error={!!fullNameValidationErrMsg}
                                />

                                <TextField 
                                    label="Email"
                                    type="email"
                                    value={email}
                                    sx={{ display: "block" }}
                                    margin="normal"
                                    onChange={e => setEmail(e.target.value)}
                                    helperText={emailValidationErrMsg}
                                    error={!!emailValidationErrMsg}
                                />

                                {(waitingForServer) ? <Loading /> : <></>}
                                <Box textAlign="center">
                                    <Button type="submit" variant="contained" fullWidth>
                                        Submit
                                    </Button>
                                </Box>
                            </form>
                        </Paper>
                    </Box>

                    {(confirmationMessage.length === 0) ? <></> : (
                        <Alert severity="success" sx={{ mt: 2 }} ref={successAlertRef}>
                            {confirmationMessage}
                        </Alert>
                    )}
                </CardContent>
            </Card>
        </Container>
    );
}