import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Main from './main';
import Belarus from './belarus';
import Footer from "./footer";

function App() {
  return (
   <div className="div">
      <Router>
         <Routes>
         <Route path="/" element={<Main />} />
         <Route path="/belarus" element={<Belarus />} />
         </Routes>
      </Router>
      <Footer></Footer>
    </div>
  );
}
// div className="form-group" style={{ width: '100%', padding: '20px', background: '#f5f5f5', borderRadius: '8px', height: '300px', width: '1075px' }}>
export default App;