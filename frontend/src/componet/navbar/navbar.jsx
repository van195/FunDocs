import './navbar.css';
import Logo from '../../assets/10a13612-0bc8-430b-94cc-5c13e677e765.png';
import EastOutlinedIcon from '@mui/icons-material/EastOutlined';
import { Link } from 'react-router-dom';

const Navbar = ()=>{
    return(
        <div className="navbar">
            <div className="navbarContainer">
                <div className="theTopPart">
                    <img src={Logo} alt="" />
                </div>
                <div className="theCenterPart">
                    <span className="menuItems">Blog</span>
                    <span className="menuItems">Service</span>
                    <span className="menuItems">Pricing</span>
                    <span className="menuItems">Blog</span>
                    <span className="menuItems">Contact</span>
                </div>
                <div className="theBottomPart">
                    <Link to='/register'>
                        <div className="callOfAction">
                            <span >Join</span> 
                            <span className='theArrow'><EastOutlinedIcon style={{color:'#fff'}}/></span> 
                        </div>
                    </Link>
                </div>
            </div>
        </div>
    )
}
export default Navbar;