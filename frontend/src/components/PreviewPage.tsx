import React from 'react';

const PreviewPage: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <h1 className="text-4xl font-bold mb-4">Preview Your Website</h1>
      <div className="bg-white p-8 shadow-lg rounded">
        {/* Render preview of the website here */}
      </div>
    </div>
  );
};

export default PreviewPage;
