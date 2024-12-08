import React, { useCallback, useRef, useEffect, useState } from 'react';
import Webcam from 'react-webcam';
import { Camera, Square } from 'lucide-react';
import { DetectionResults } from '../types/api';

interface WebcamCaptureProps {
  onCapture: (imageSrc: string) => void;
  isCapturing: boolean;
  onToggleCapture: () => void;
  detections?: DetectionResults;
}

export const WebcamCapture: React.FC<WebcamCaptureProps> = ({
  onCapture,
  isCapturing,
  onToggleCapture,
  detections
}) => {
  const webcamRef = useRef<Webcam>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 });
  const intervalRef = useRef<number>();

  const capture = useCallback(() => {
    const imageSrc = webcamRef.current?.getScreenshot();
    if (imageSrc) {
      onCapture(imageSrc);
    }
  }, [onCapture]);

  useEffect(() => {
    if (isCapturing) {
      intervalRef.current = window.setInterval(capture, 500);
    }
    return () => {
      if (intervalRef.current) {
        window.clearInterval(intervalRef.current);
      }
    };
  }, [isCapturing, capture]);

  const updateDimensions = useCallback(() => {
    if (webcamRef.current?.video && containerRef.current) {
      const video = webcamRef.current.video;
      const container = containerRef.current;
      const containerWidth = container.clientWidth;
      
      // Calculate height while maintaining aspect ratio
      const videoAspectRatio = video.videoWidth / video.videoHeight;
      const height = Math.floor(containerWidth / videoAspectRatio);

      setDimensions({
        width: containerWidth,
        height: height
      });
    }
  }, []);

  useEffect(() => {
    const video = webcamRef.current?.video;
    if (video) {
      video.addEventListener('loadedmetadata', updateDimensions);
      window.addEventListener('resize', updateDimensions);
    }
    return () => {
      if (video) {
        video.removeEventListener('loadedmetadata', updateDimensions);
      }
      window.removeEventListener('resize', updateDimensions);
    };
  }, [updateDimensions]);

  useEffect(() => {
    if (!canvasRef.current || !detections || !webcamRef.current?.video) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const video = webcamRef.current.video;
    if (!ctx) return;

    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Get the actual rendered dimensions of the video element
    const videoRect = video.getBoundingClientRect();
    
    // Calculate scale factors based on the actual rendered size vs original video size
    const scaleX = 1.0; // videoRect.width / video.videoWidth;
    const scaleY = 1.0;  // videoRect.height / video.videoHeight;

    // Draw bounding boxes
    detections.result.forEach((detection) => {
      const { x, y, w, h } = detection.bounding_box;
      
      // Scale the coordinates using the actual video render dimensions
      const scaledX = x * scaleX;
      const scaledY = y * scaleY;
      const scaledW = w * scaleX;
      const scaledH = h * scaleY;

      // Draw box
      ctx.strokeStyle = '#00ff00';
      ctx.lineWidth = 2;
      ctx.strokeRect(scaledX, scaledY, scaledW, scaledH);

      // Draw confidence score
      ctx.font = '16px Arial';
      const confidence = (detection.confidence * 100).toFixed(1);
      const text = `${confidence}%`;
      const textWidth = ctx.measureText(text).width;
      
      // Background for text
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.fillRect(scaledX, scaledY - 25, textWidth + 10, 20);
      
      // Text
      ctx.fillStyle = '#00ff00';
      ctx.fillText(text, scaledX + 5, scaledY - 10);
    });
  }, [detections, dimensions]);

  return (
    <div className="relative" ref={containerRef}>
      <Webcam
        audio={false}
        ref={webcamRef}
        screenshotFormat="image/jpeg"
        className="w-full rounded-lg"
        videoConstraints={{
          width: 640,
          height: 640,
          facingMode: "user"
        }}
      />
      <canvas
        ref={canvasRef}
        width={dimensions.width}
        height={dimensions.height}
        className="absolute top-0 left-0 w-full h-full pointer-events-none rounded-lg"
      />
      <button
        onClick={onToggleCapture}
        className={`absolute bottom-4 left-1/2 -translate-x-1/2 ${
          isCapturing ? 'bg-red-500 hover:bg-red-600' : 'bg-blue-500 hover:bg-blue-600'
        } text-white px-4 py-2 rounded-full flex items-center gap-2 transition-colors`}
      >
        {isCapturing ? (
          <>
            <Square size={20} />
            Stop
          </>
        ) : (
          <>
            <Camera size={20} />
            Start Recognition
          </>
        )}
      </button>
    </div>
  );
};