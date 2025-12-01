import { useEffect, useRef, useState } from 'react';
import { Camera, CameraOff } from 'lucide-react';
import toast from 'react-hot-toast';
import api from '../lib/api';

interface CameraPreviewProps {
  onCapture?: (blob: Blob) => void;
  autoCapture?: boolean;
  captureInterval?: number;
}

interface FaceBox {
  x: number;
  y: number;
  w: number;
  h: number;
}

interface FaceData {
  bbox: FaceBox;
  landmarks?: number[][];
  name?: string;
  confidence?: number;
}

export default function CameraPreview({ onCapture, autoCapture = false, captureInterval = 2000 }: CameraPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isActive, setIsActive] = useState(false);
  const [faceDetected, setFaceDetected] = useState(false);
  const intervalRef = useRef<number | null>(null);
  const detectionIntervalRef = useRef<number | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const lastFaceBoxRef = useRef<FaceBox | null>(null);
  const smoothedBoxRef = useRef<FaceBox | null>(null);
  const lastFaceDataRef = useRef<FaceData | null>(null);
  const isActiveRef = useRef<boolean>(false);

  const detectFacesFromBackend = async () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    
    if (!context || video.readyState !== 4) return;
    
    try {
      // Capture current frame
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0);
      
      // Convert to blob
      const blob = await new Promise<Blob | null>((resolve) => {
        canvas.toBlob(resolve, 'image/jpeg', 0.8);
      });
      
      if (!blob) {
        console.log('Failed to create blob from canvas');
        return;
      }
      
      // Send to backend for detection
      const formData = new FormData();
      formData.append('image', blob);
      
      console.log('Sending face detection request...');
      const response = await api.post('/api/attendance/detect-face', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const data = response.data;
      console.log('Face detection response:', data);
      
      if (data.status === 'success' && data.faces && data.faces.length > 0) {
        // Use the first detected face
        const faceData: FaceData = data.faces[0];
        console.log('✅ Face detected at:', JSON.stringify(faceData.bbox));
        lastFaceBoxRef.current = faceData.bbox;
        lastFaceDataRef.current = faceData;
        setFaceDetected(true);
      } else {
        console.log('⚠️ No face detected');
        lastFaceBoxRef.current = null;
        lastFaceDataRef.current = null;
        setFaceDetected(false);
      }
    } catch (error) {
      console.error('Face detection error:', error);
      // Don't show error toast for detection failures (too noisy)
    }
  };

  const updateOverlay = () => {
    if (!overlayCanvasRef.current || !videoRef.current) {
      console.log('❌ updateOverlay: Missing refs');
      return;
    }
    
    const canvas = overlayCanvasRef.current;
    const video = videoRef.current;
    const context = canvas.getContext('2d');
    
    if (!context) {
      console.log('❌ updateOverlay: No context');
      return;
    }
    
    if (video.readyState !== 4) {
      console.log('⏳ updateOverlay: Video not ready, readyState =', video.readyState);
      return;
    }
    
    // Get the ACTUAL DISPLAYED size of the video element
    const displayWidth = video.clientWidth;
    const displayHeight = video.clientHeight;
    
    console.log(`🔍 Video display: ${displayWidth}x${displayHeight}, native: ${video.videoWidth}x${video.videoHeight}`);
    
    // Resize canvas to match the DISPLAYED video size (not native resolution)
    if (canvas.width !== displayWidth || canvas.height !== displayHeight) {
      canvas.width = displayWidth;
      canvas.height = displayHeight;
      console.log(`📐 Canvas resized to DISPLAY size: ${displayWidth}x${displayHeight}`);
    }
    
    // Calculate scaling factors from native resolution to displayed size
    const scaleX = displayWidth / video.videoWidth;
    const scaleY = displayHeight / video.videoHeight;
    
    // Clear previous drawings
    context.clearRect(0, 0, canvas.width, canvas.height);
    
    // Draw face box if detected
    if (lastFaceBoxRef.current) {
      // Smooth the box movement
      if (!smoothedBoxRef.current) {
        smoothedBoxRef.current = { ...lastFaceBoxRef.current };
      } else {
        const alpha = 0.3; // Smoothing factor (0-1, lower = smoother)
        smoothedBoxRef.current.x += alpha * (lastFaceBoxRef.current.x - smoothedBoxRef.current.x);
        smoothedBoxRef.current.y += alpha * (lastFaceBoxRef.current.y - smoothedBoxRef.current.y);
        smoothedBoxRef.current.w += alpha * (lastFaceBoxRef.current.w - smoothedBoxRef.current.w);
        smoothedBoxRef.current.h += alpha * (lastFaceBoxRef.current.h - smoothedBoxRef.current.h);
      }
      
      const { x: rawX, y: rawY, w: rawW, h: rawH } = smoothedBoxRef.current;
      
      // Apply scaling to convert from native video coordinates to display coordinates
      const x = rawX * scaleX;
      const y = rawY * scaleY;
      const w = rawW * scaleX;
      const h = rawH * scaleY;
      
      console.log(`🎨 Drawing box: native(${rawX.toFixed(0)},${rawY.toFixed(0)},${rawW.toFixed(0)},${rawH.toFixed(0)}) → display(${x.toFixed(0)},${y.toFixed(0)},${w.toFixed(0)},${h.toFixed(0)}) | scale(${scaleX.toFixed(2)},${scaleY.toFixed(2)})`);
      
      // Validate coordinates
      if (x >= 0 && y >= 0 && w > 0 && h > 0) {
        // Draw main bounding box
        context.strokeStyle = '#FF6B9D'; // Pink/salmon color like in the image
        context.lineWidth = 3;
        context.strokeRect(x, y, w, h);
        
        // Prepare label text
        let labelText = 'DETECTING...';
        if (lastFaceDataRef.current?.name) {
          const name = lastFaceDataRef.current.name;
          const confidence = lastFaceDataRef.current.confidence;
          if (confidence !== undefined) {
            labelText = `${name} ${(confidence * 100).toFixed(0)}%`;
          } else {
            labelText = name;
          }
        }
        
        // Draw label background at the top
        const labelPadding = 8;
        const fontSize = Math.max(14, Math.min(18, w / 15)); // Responsive font size
        context.font = `bold ${fontSize}px Arial`;
        const textWidth = context.measureText(labelText).width;
        const labelWidth = textWidth + labelPadding * 2;
        const labelHeight = fontSize + labelPadding * 2;
        
        // Draw label background (same color as box)
        context.fillStyle = '#FF6B9D';
        context.fillRect(x, y - labelHeight, labelWidth, labelHeight);
        
        // Draw label text
        context.fillStyle = '#FFFFFF';
        context.textAlign = 'left';
        context.textBaseline = 'top';
        context.fillText(labelText, x + labelPadding, y - labelHeight + labelPadding);
        
        // Draw corner brackets for style
        const cornerLength = Math.min(20 * Math.min(scaleX, scaleY), Math.min(w, h) / 5);
        context.lineWidth = 3;
        context.strokeStyle = '#FF6B9D';
        
        // Top-left corner
        context.beginPath();
        context.moveTo(x, y + cornerLength);
        context.lineTo(x, y);
        context.lineTo(x + cornerLength, y);
        context.stroke();
        
        // Top-right corner
        context.beginPath();
        context.moveTo(x + w - cornerLength, y);
        context.lineTo(x + w, y);
        context.lineTo(x + w, y + cornerLength);
        context.stroke();
        
        // Bottom-left corner
        context.beginPath();
        context.moveTo(x, y + h - cornerLength);
        context.lineTo(x, y + h);
        context.lineTo(x + cornerLength, y + h);
        context.stroke();
        
        // Bottom-right corner
        context.beginPath();
        context.moveTo(x + w - cornerLength, y + h);
        context.lineTo(x + w, y + h);
        context.lineTo(x + w, y + h - cornerLength);
        context.stroke();
      }
    }
    
    // Continue animation loop
    if (isActiveRef.current) {
      animationFrameRef.current = requestAnimationFrame(updateOverlay);
    } else {
      console.log('⏹️ Animation loop stopped (isActiveRef.current = false)');
    }
  };

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, facingMode: 'user' }
      });
      
      // Set active state FIRST so animation loop can continue
      setStream(mediaStream);
      setIsActive(true);
      isActiveRef.current = true; // Set ref immediately for animation loop
      
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        
        // Wait for video to be ready before starting detection
        videoRef.current.onloadedmetadata = () => {
          console.log('✅ Video metadata loaded');
          console.log(`📹 Native: ${videoRef.current?.videoWidth}x${videoRef.current?.videoHeight}`);
          console.log(`📺 Display: ${videoRef.current?.clientWidth}x${videoRef.current?.clientHeight}`);
          
          // Start overlay animation loop (60fps for smooth tracking)
          console.log('🚀 Starting animation loop...');
          animationFrameRef.current = requestAnimationFrame(updateOverlay);
          
          // Start backend face detection (every 500ms)
          setTimeout(() => {
            console.log('🚀 Starting detection interval...');
            detectionIntervalRef.current = setInterval(() => {
              detectFacesFromBackend();
            }, 500);
            
            // Trigger first detection immediately
            detectFacesFromBackend();
          }, 500);
        };
      }
      
      toast.success('Camera started');
      
      // Start auto-capture if enabled
      if (autoCapture && onCapture) {
        intervalRef.current = setInterval(() => {
          captureFrame();
        }, captureInterval);
      }
    } catch (error) {
      console.error('Camera error:', error);
      toast.error('Failed to access camera');
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setIsActive(false);
      isActiveRef.current = false; // Stop animation loop immediately
      setFaceDetected(false);
      
      // Clear all intervals and animation frames
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
        intervalRef.current = null;
      }
      
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current);
        detectionIntervalRef.current = null;
      }
      
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
        animationFrameRef.current = null;
      }
      
      // Reset face tracking state
      lastFaceBoxRef.current = null;
      smoothedBoxRef.current = null;
      
      // Clear the overlay canvas
      if (overlayCanvasRef.current) {
        const context = overlayCanvasRef.current.getContext('2d');
        if (context) {
          context.clearRect(0, 0, overlayCanvasRef.current.width, overlayCanvasRef.current.height);
          console.log('✓ Canvas cleared');
        }
      }
      
      toast.success('Camera stopped');
    }
  };

  const captureFrame = () => {
    if (!videoRef.current || !canvasRef.current) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    
    if (!context) return;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0);
    
    canvas.toBlob((blob) => {
      if (blob && onCapture) {
        onCapture(blob);
      }
    }, 'image/jpeg', 0.95);
  };

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  return (
    <div className="space-y-4">
      <div className="relative mx-auto bg-black rounded-lg overflow-hidden" style={{ maxWidth: '640px' }}>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          muted
          className="w-full h-auto block"
          style={{ 
            position: 'relative',
            zIndex: 1,
            display: 'block'
          }}
        />
        
        {/* Face detection overlay canvas */}
        <canvas
          ref={overlayCanvasRef}
          className="absolute pointer-events-none"
          style={{ 
            position: 'absolute',
            top: 0, 
            left: 0, 
            width: '100%', 
            height: '100%',
            zIndex: 9999
          }}
        />
        
        {!isActive && (
          <div className="absolute inset-0 flex items-center justify-center bg-gray-800">
            <CameraOff className="w-16 h-16 text-gray-400" />
          </div>
        )}
        
        {/* Face detection indicator */}
        {isActive && faceDetected && (
          <div className="absolute top-4 right-4 px-3 py-1 bg-green-500 text-white text-sm rounded-full font-medium">
            Face Detected
          </div>
        )}
      </div>
      
      <canvas ref={canvasRef} className="hidden" />
      
      <div className="flex space-x-4">
        {!isActive ? (
          <button
            onClick={startCamera}
            className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
          >
            <Camera className="w-5 h-5" />
            <span>Start Camera</span>
          </button>
        ) : (
          <>
            <button
              onClick={stopCamera}
              className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
            >
              <CameraOff className="w-5 h-5" />
              <span>Stop Camera</span>
            </button>
            
            {!autoCapture && (
              <button
                onClick={captureFrame}
                className="flex-1 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
              >
                Capture Frame
              </button>
            )}
          </>
        )}
      </div>
      
      {autoCapture && isActive && (
        <div className="text-center text-sm text-gray-600">
          Auto-capturing every {captureInterval / 1000} seconds
        </div>
      )}
    </div>
  );
}
