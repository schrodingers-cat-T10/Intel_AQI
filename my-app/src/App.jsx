import React from 'react';
import { BrowserRouter as Router, Route, Routes, Link } from 'react-router-dom';
import { FaHome, FaCloud, FaChartLine, FaRobot } from 'react-icons/fa'; // Add FaRobot for the chatbot icon
import Home from './Home.jsx';
import PageOne from './pageone.jsx';
import PageTwo from './pagetwo.jsx';
import Chatbot from './chatbot.jsx'; // Import Chatbot component

function App() {
  return (
    <Router>
      <div className="App" style={styles.app}>
        {/* Navigation Bar */}
        <nav style={styles.navbar}>
          <ul style={styles.navLinks}>
            <li style={styles.navItem}>
              <Link to="/" style={styles.link}>
                <FaHome style={styles.icon} />
                <span style={styles.label}>Home</span>
              </Link>
            </li>
            <li style={styles.navItem}>
              <Link to="/page-one" style={styles.link}>
                <FaCloud style={styles.icon} />
                <span style={styles.label}>Cloud</span>
              </Link>
            </li>
            <li style={styles.navItem}>
              <Link to="/page-two" style={styles.link}>
                <FaChartLine style={styles.icon} />
                <span style={styles.label}>Graph</span>
              </Link>
            </li>
            <li style={styles.navItem}>
              <Link to="/chatbot" style={styles.link}>
                <FaRobot style={styles.icon} /> {/* Robot icon for chatbot */}
                <span style={styles.label}>Chatbot</span>
              </Link>
            </li>
          </ul>
        </nav>

        {/* Routes that will switch between components */}
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/page-one" element={<PageOne />} />
          <Route path="/page-two" element={<PageTwo />} />
          <Route path="/chatbot" element={<Chatbot />} /> {/* Chatbot Route */}
        </Routes>
      </div>
    </Router>
  );
}

const styles = {
  app: {
    backgroundColor: '#E0F7FA',
    height: '100vh',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  },
  navbar: {
    display: 'flex',
    justifyContent: 'flex-end', // Align items to the right
    padding: '15px',
    backgroundColor: '#fff',
    borderRadius: '30px',
    boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
    position: 'absolute', // Position at the top right
    top: '20px', // Adjust the distance from the top
    right: '20px', // Adjust the distance from the right
    width: 'auto', // Adjust to fit content
  },
  navLinks: {
    display: 'flex',
    justifyContent: 'space-between', // Creates space between items
    gap: '70px', // Add more space between each item
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  navItem: {
    position: 'relative',
  },
  link: {
    textDecoration: 'none',
    color: '#6c757d',
    fontSize: '14px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px',
    transition: 'color 0.3s',
  },
  icon: {
    fontSize: '27px',
  },
  label: {
    fontSize: '12px',
  },
};

export default App;