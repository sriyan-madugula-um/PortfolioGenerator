import React from 'react';
import { Link } from 'react-router-dom';

const LandingPage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <h1 className="text-4xl font-bold mb-4">Welcome to Our Website</h1>
      <div className="space-x-4">
        <Link to="/upload" className="bg-blue-500 text-white px-4 py-2 rounded">Get Started</Link>
        <a href="#preview-templates" className="bg-green-500 text-white px-4 py-2 rounded">Preview Templates</a>
      </div>
    </div>
  );
};

export default LandingPage;
