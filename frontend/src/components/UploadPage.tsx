import React from 'react';

const UploadPage: React.FC = () => {
  const handleUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // You can process the file here, e.g., read its content, send it to the backend, etc.
      console.log('File uploaded:', file.name);

      // Example: Create a FormData object to send the file to a backend
      const formData = new FormData();
      formData.append('resume', file);

      // Send the file to the backend (replace with your API endpoint)
      fetch('/api/upload', {
        method: 'POST',
        body: formData,
      })
      .then(response => response.json())
      .then(data => {
        console.log('File upload successful:', data);
      })
      .catch(error => {
        console.error('File upload failed:', error);
      });
    }
  };

  return (
    <div className="flex flex-col items-center justify-center h-screen bg-gray-100">
      <h1 className="text-4xl font-bold mb-4">Upload Your Resume</h1>
      <input 
        type="file" 
        onChange={handleUpload} 
        className="mb-4 p-2 border rounded"
      />
    </div>
  );
};

export default UploadPage;