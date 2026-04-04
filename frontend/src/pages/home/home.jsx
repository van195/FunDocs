import Hero from '../../componet/hero/hero';
import Navbar from '../../componet/navbar/navbar';
import './home.css';
const Home = ({allowPage})=>{
    
    return(
        <div className="home">
            <Navbar/>
            <Hero/>
        </div>
    )
}
export default Home;