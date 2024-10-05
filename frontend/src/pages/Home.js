import React, { useEffect } from 'react';
import '../styles/Home.css';

function Home() {
  useEffect(() => {
    document.title = "PetBnB - Home";
  }, []);

  return (
    <div className="home"> 
      <h1>Welcome to PetBnB</h1>
      <p>Find a sitter for your beloved...</p>
      <img src="/luna.jpeg" alt="Luna" />
      <p>This is Luna btw... She is not pleased...</p>
    </div>
  );
}

export default Home;