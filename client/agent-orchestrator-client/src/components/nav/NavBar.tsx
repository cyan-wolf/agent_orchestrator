import { Box, Tab, Tabs } from "@mui/material";
import { useState } from "react";
import { useNavigate } from "react-router-dom";

type NavPageInfo = {
    to: string,
    title: string,
};

type NavBarProps = {
    pages: NavPageInfo[]
};

const NavBar = (props: NavBarProps) => {
    const [value, setValue] = useState("/");
    const navigate = useNavigate();

    const handleChange = (event: React.SyntheticEvent, newValue: string) => {
        setValue(newValue);
        navigate(newValue);
    };

    return (
        <Box sx={{ width: '100%' }}>
        <Tabs
            value={value}
            onChange={handleChange}
            textColor="primary"
            indicatorColor="primary"
            aria-label="secondary tabs example"
        >
            {props.pages.map(p => (
                <Tab value={p.to} label={p.title} key={p.title} />
            ))}
        </Tabs>
        </Box>
    );
};

export default NavBar;