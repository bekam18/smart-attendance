import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import CameraPreview from '../components/CameraPreview';
import { studentAPI } from '../lib/api';
import { ArrowLeft, Upload, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function StudentRegistration() {
  const [capturedImages, setCapturedImages] = useState<Blob[]>([]);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const navigate = useNavigate();

  const handleCapture = (blob: Blob) => {
    setCapturedImages(prev => [...prev, blob]);
    toast.success(`Image ${capturedImages.length + 1} captured`);
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (!files) return;
    
    const blobs: Blob[] = [];
    Array.from(files).forEach(file => {
      blobs.push(file);
    });
    
    setCapturedImages(prev => [...prev, ...blobs]);
    toast.success(`${blobs.length} image(s) added`);
  };

  const handleRemoveImage = (index: number) => {
    setCapturedImages(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (capturedImages.length < 3) {
      toast.error('Please capture at least 3 images');
      return;
    }

    setUploading(true);
    
    try {
      // Convert blobs to files
      const files = capturedImages.map((blob, index) => 
        new File([blob], `face_${index}.jpg`, { type: 'image/jpeg' })
      );
      
      await studentAPI.registerFace(files);
      toast.success('Face registered successfully!');
      navigate('/student');
    } catch (error: any) {
      toast.error(error.response?.data?.error || 'Failed to register face');
    } finally {
      setUploading(false);
    }
  };

  return (
    <Layout title="Register Face">
      <div className="space-y-6">
        <button
          onClick={() => navigate('/student')}
          className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
        >
          <ArrowLeft className="w-5 h-5" />
          <span>Back to Dashboard</span>
        </button>

        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-2xl font-bold mb-4">Register Your Face</h2>
          <p className="text-gray-600 mb-6">
            Capture multiple images of your face from different angles for better recognition accuracy.
            We recommend at least 5-10 images.
          </p>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Camera Section */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Capture from Camera</h3>
              <CameraPreview onCapture={handleCapture} />
            </div>

            {/* Upload Section */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Or Upload Images</h3>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
                <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600 mb-4">
                  Click to upload images or drag and drop
                </p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  multiple
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Choose Files
                </button>
              </div>
            </div>
          </div>

          {/* Captured Images */}
          {capturedImages.length > 0 && (
            <div className="mt-6">
              <h3 className="text-lg font-semibold mb-4">
                Captured Images ({capturedImages.length})
              </h3>
              <div className="grid grid-cols-3 md:grid-cols-5 gap-4">
                {capturedImages.map((blob, index) => (
                  <div key={index} className="relative group">
                    <img
                      src={URL.createObjectURL(blob)}
                      alt={`Capture ${index + 1}`}
                      className="w-full h-32 object-cover rounded-lg"
                    />
                    <button
                      onClick={() => handleRemoveImage(index)}
                      className="absolute top-2 right-2 p-1 bg-red-600 text-white rounded-full opacity-0 group-hover:opacity-100 transition"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Submit Button */}
          <div className="mt-6 flex justify-end space-x-4">
            <button
              onClick={() => setCapturedImages([])}
              className="px-6 py-3 bg-gray-300 rounded-lg hover:bg-gray-400"
              disabled={uploading || capturedImages.length === 0}
            >
              Clear All
            </button>
            <button
              onClick={handleSubmit}
              disabled={uploading || capturedImages.length < 3}
              className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : `Register ${capturedImages.length} Images`}
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
}
