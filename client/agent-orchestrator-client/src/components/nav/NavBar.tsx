import { Box, Tab, Tabs } from "@mui/material";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

type NavPageInfo = {
    to: string,
    title: string,
};

type NavBarProps = {
    pages: NavPageInfo[]
};

function locationIsValidPage(locationPath: string, pages: NavPageInfo[]): boolean {
    for (const page of pages) {
        if (locationPath === page.to) {
            return true;
        }
    }
    return false;
}

const NavBar = ({ pages }: NavBarProps) => {
    const location = useLocation();
    const [pageName, setPageName] = useState<string>('/');
    const navigate = useNavigate();

    // This useEffect is needed to update the nav bar UI itself 
    // whenever the location is changed dynamically (for example, by the authentication protected routes).
    useEffect(() => {
        // Check if the current location is a valid page for the nav bar to try to 
        // select.
        if (!locationIsValidPage(location.pathname, pages)) {
            return;
        }

        setPageName(location.pathname);
    }, [location.pathname]);

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
            {pages.map(p => (
                <Tab value={p.to} label={p.title} key={p.title} />
            ))}
        </Tabs>
        </Box>
    );
};

export default NavBar;