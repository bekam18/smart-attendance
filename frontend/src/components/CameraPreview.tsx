import { useEffect, useRef, useState } from 'react';
import { Camera, CameraOff } from 'lucide-react';
import toast from 'react-hot-toast';
import { attendanceAPI } from '../lib/api';

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

export default function CameraPreview({ onCapture, autoCapture = false, captureInterval = 4000 }: CameraPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [isActive, setIsActive] = useState(false);
  const [faceDetected, setFaceDetected] = useState(false);
  const [detectionSpeed, setDetectionSpeed] = useState<number>(0);
  const intervalRef = useRef<number | null>(null);
  const detectionIntervalRef = useRef<number | null>(null);
  const animationFrameRef = useRef<number | null>(null);
  const lastFaceBoxRef = useRef<FaceBox | null>(null);
  const smoothedBoxRef = useRef<FaceBox | null>(null);
  const lastFaceDataRef = useRef<FaceData | null>(null);
  const isActiveRef = useRef<boolean>(false);
  const lastDetectionTime = useRef<number>(0);
  const isProcessing = useRef<boolean>(false);
  const faceDetector = useRef<any>(null);
  const clientSideDetectionRef = useRef<number | null>(null);

  // Client-side face detection using browser API (if available)
  const detectFacesClientSide = async () => {
    if (!videoRef.current || !isActiveRef.current) return;
    
    const video = videoRef.current;
    if (video.readyState !== 4) return;
    
    try {
      // Try to use browser's FaceDetector API if available
      if (faceDetector.current) {
        const faces = await faceDetector.current.detect(video);
        
        if (faces && faces.length > 0) {
          const face = faces[0];
          const bbox = face.boundingBox;
          
          const faceBox = {
            x: bbox.x,
            y: bbox.y,
            w: bbox.width,
            h: bbox.height
          };
          
          lastFaceBoxRef.current = faceBox;
          setFaceDetected(true);
        } else {
          // Only clear if we haven't detected from backend recently
          const timeSinceBackendDetection = Date.now() - lastDetectionTime.current;
          if (timeSinceBackendDetection > 2000) {
            lastFaceBoxRef.current = null;
            setFaceDetected(false);
          }
        }
      }
    } catch (error) {
      // Silently fail - client-side detection is optional
    }
  };

  const detectFacesFromBackend = async () => {
    if (!videoRef.current || !canvasRef.current || !isActiveRef.current || isProcessing.current) return;
    
    // ULTRA-FAST detection - maximum responsiveness (50ms for lightning-fast tracking)
    const now = Date.now();
    if (now - lastDetectionTime.current < 50) return; // 50ms for lightning-fast tracking
    
    isProcessing.current = true;
    const detectionStartTime = now;
    lastDetectionTime.current = now;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const context = canvas.getContext('2d');
    
    if (!context || video.readyState !== 4) {
      isProcessing.current = false;
      return;
    }
    
    try {
      // ULTRA-SMALL resolution for maximum speed
      const targetWidth = 120; // Ultra-small for maximum speed
      const targetHeight = 90; // Ultra-small for maximum speed
      
      canvas.width = targetWidth;
      canvas.height = targetHeight;
      context.drawImage(video, 0, 0, targetWidth, targetHeight);
      
      // ULTRA-LOW quality for maximum speed
      const blob = await new Promise<Blob | null>((resolve) => {
        canvas.toBlob(resolve, 'image/jpeg', 0.3); // Ultra-low quality for maximum speed
      });
      
      if (!blob) {
        console.log('Failed to create blob from canvas');
        isProcessing.current = false;
        return;
      }
      
      // Send to backend for detection using the proper API
      const response = await attendanceAPI.detectFace(blob);
      
      const data = response.data;
      
      if (data.status === 'success' && data.faces && data.faces.length > 0) {
        // Scale bbox back to video dimensions
        const faceData: FaceData = data.faces[0];
        const scaleX = video.videoWidth / targetWidth;
        const scaleY = video.videoHeight / targetHeight;
        
        const scaledBbox = {
          x: faceData.bbox.x * scaleX,
          y: faceData.bbox.y * scaleY,
          w: faceData.bbox.w * scaleX,
          h: faceData.bbox.h * scaleY
        };
        
        lastFaceBoxRef.current = scaledBbox;
        lastFaceDataRef.current = { ...faceData, bbox: scaledBbox };
        setFaceDetected(true);
        
        // Update detection speed
        const detectionTime = Date.now() - detectionStartTime;
        setDetectionSpeed(detectionTime);
      } else {
        lastFaceBoxRef.current = null;
        lastFaceDataRef.current = null;
        setFaceDetected(false);
      }
    } catch (error) {
      console.error('Face detection error:', error);
      // Don't show error toast for detection failures (too noisy)
    } finally {
      isProcessing.current = false;
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
      // Smooth the box movement for better tracking
      if (!smoothedBoxRef.current) {
        smoothedBoxRef.current = { ...lastFaceBoxRef.current };
      } else {
        const alpha = 0.95; // Ultra-high responsiveness for lightning-fast tracking
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
        // Draw main bounding box with animation effect
        const pulseEffect = Math.sin(Date.now() / 200) * 0.1 + 0.9; // Subtle pulse animation
        context.strokeStyle = '#FF6B9D'; // Pink/salmon color like in the image
        context.lineWidth = 3;
        context.globalAlpha = pulseEffect;
        context.strokeRect(x, y, w, h);
        context.globalAlpha = 1.0; // Reset alpha
        
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
          
          // Initialize client-side face detector if available
          try {
            // @ts-ignore - FaceDetector is experimental
            if (window.FaceDetector) {
              // @ts-ignore
              faceDetector.current = new window.FaceDetector({
                maxDetectedFaces: 1,
                fastMode: true
              });
              console.log('✅ Client-side FaceDetector initialized');
              
              // Start client-side detection for LIGHTNING-FAST tracking (120fps)
              clientSideDetectionRef.current = setInterval(() => {
                detectFacesClientSide();
              }, 16); // ~60fps for ultra-smooth tracking
            }
          } catch (error) {
            console.log('⚠️ Client-side FaceDetector not available, using backend only');
          }
          
          // Start overlay animation loop (60fps for smooth tracking)
          console.log('🚀 Starting animation loop...');
          animationFrameRef.current = requestAnimationFrame(updateOverlay);
          
          // Start backend face detection (faster for better tracking)
          setTimeout(() => {
            console.log('🚀 Starting detection interval...');
            detectionIntervalRef.current = setInterval(() => {
              detectFacesFromBackend();
            }, 60);  // LIGHTNING-FAST 60ms intervals for ultra-responsive tracking
            
            // Trigger first detection immediately
            setTimeout(() => detectFacesFromBackend(), 100);
          }, 100);
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
      
      if (clientSideDetectionRef.current) {
        clearInterval(clientSideDetectionRef.current);
        clientSideDetectionRef.current = null;
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
            Face Detected {detectionSpeed > 0 && `(${detectionSpeed}ms)`}
          </div>
        )}
        
        {/* Processing indicator */}
        {isActive && isProcessing && (
          <div className="absolute top-4 left-4 px-3 py-1 bg-blue-500 text-white text-sm rounded-full font-medium animate-pulse">
            Processing...
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
