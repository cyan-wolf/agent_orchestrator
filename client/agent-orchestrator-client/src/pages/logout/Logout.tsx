import { Link } from "react-router-dom";
import { useAuth } from "../../auth/useAuth";

export default function Logout() {
    const { user, logout } = useAuth()!;

    function handleButtonClick() {
        logout();
    }

    const toLogoutView = (
        <div>
            <h2>Logout</h2>
            <button type="button" onClick={handleButtonClick}>Logout (Are you sure?)</button>
        </div>
    );
    
    const alreadyLoggedOutView = (
        <div>
            <h2>Already logged out</h2>
            <Link to={"/login"}>Click here to login</Link>
        </div>
    );

    return (user !== null) ? toLogoutView : alreadyLoggedOutView;
}