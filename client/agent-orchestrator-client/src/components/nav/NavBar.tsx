import { Box, Tab, Tabs } from "@mui/material";
import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

type NavPageInfo = {
    to: string,
    title: string,
};

type NavBarProps = {
    pages: NavPageInfo[]
};

const NavBar = (props: NavBarProps) => {
    const location = useLocation();
    const [pageName, setPageName] = useState<string>(location.pathname);
    const navigate = useNavigate();

    const handlePageChange = (newPageName: string) => {
        setPageName(newPageName);
        navigate(newPageName);
    };

    return (
        <Box sx={{ width: '100%' }}>
        <Tabs
            value={pageName}
            onChange={(_, newPageName) => handlePageChange(newPageName)}
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