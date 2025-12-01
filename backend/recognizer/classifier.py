import numpy as np
from config import config
from recognizer.loader import model_loader
from recognizer.detector import face_detector
from recognizer.embeddings_facenet import embedding_generator  # Use FaceNet embeddings
from utils.image_tools import decode_image
import logging

logger = logging.getLogger(__name__)

class FaceRecognizer:
    def __init__(self):
        # Override threshold to 0.60 for better recognition
        # This allows faces with confidence 0.60+ to be recognized
        self.threshold = 0.60
        print(f"🎯 [Classifier] Recognition threshold set to: {self.threshold}")
        
    def recognize(self, image_data):
        """
        Main recognition pipeline
        
        Args:
            image_data: image bytes, base64, or numpy array
            
        Returns:
            dict with recognition results
        """
        try:
            print("🔍 [Classifier] Starting recognition pipeline")
            
            # Check if model is loaded
            if not model_loader.is_loaded():
                print("⚠️ [Classifier] Model not loaded, attempting to load...")
                success = model_loader.load_models()
                if not success:
                    print("❌ [Classifier] Model loading failed")
                    return {
                        'status': 'error',
                        'error': 'Recognition model missing',
                        'requires_model': True,
                        'message': 'Please ensure model files are in backend/models/Classifier/'
                    }
                print("✅ [Classifier] Model loaded successfully")
            
            # Decode image
            try:
                if isinstance(image_data, np.ndarray):
                    img = image_data
                    print("✅ [Classifier] Image is numpy array")
                else:
                    img = decode_image(image_data)
                    print(f"✅ [Classifier] Image decoded: {img.shape}")
            except Exception as e:
                print(f"❌ [Classifier] Image decode error: {e}")
                return {
                    'status': 'error',
                    'error': f'Failed to decode image: {str(e)}',
                    'message': 'Invalid image format'
                }
            
            # Detect faces
            try:
                print("🔍 [Classifier] Detecting faces...")
                faces = face_detector.detect_faces(img)
                print(f"✅ [Classifier] Detected {len(faces)} face(s)")
            except Exception as e:
                print(f"❌ [Classifier] Face detection error: {e}")
                return {
                    'status': 'error',
                    'error': f'Face detection failed: {str(e)}',
                    'message': 'Face detection system error'
                }
            
            if len(faces) == 0:
                print("⚠️ [Classifier] No face detected")
                return {
                    'status': 'no_face',
                    'message': 'No face detected in image'
                }
            
            # Use the first (largest) face
            face_bbox = faces[0]
            print(f"✅ [Classifier] Using face at: {face_bbox}")
            
            # Extract face
            try:
                face_img = face_detector.extract_face(img, face_bbox)
                print(f"✅ [Classifier] Face extracted: {face_img.shape}")
            except Exception as e:
                print(f"❌ [Classifier] Face extraction error: {e}")
                return {
                    'status': 'error',
                    'error': f'Face extraction failed: {str(e)}',
                    'message': 'Failed to extract face region'
                }
            
            # Generate embedding
            try:
                print("🔍 [Classifier] Generating embedding...")
                
                # Check if embedding generator is available
                if embedding_generator is None:
                    print("❌ [Classifier] Embedding generator is None")
                    return {
                        'status': 'error',
                        'error': 'Embedding generator not initialized',
                        'message': 'Face recognition system not properly initialized'
                    }
                
                # Check if FaceNet is available
                if not embedding_generator.is_available():
                    print("❌ [Classifier] FaceNet not available")
                    return {
                        'status': 'error',
                        'error': 'FaceNet not available',
                        'message': 'Face recognition model not loaded. Install: pip install torch torchvision facenet-pytorch'
                    }
                
                embedding = embedding_generator.generate_embedding(face_img)
                print(f"✅ [Classifier] Embedding generated: shape {embedding.shape}")
                
                # Verify embedding dimension
                if embedding.shape[0] != 512:
                    print(f"❌ [Classifier] Wrong embedding dimension: {embedding.shape[0]}, expected 512")
                    return {
                        'status': 'error',
                        'error': f'Invalid embedding dimension: {embedding.shape[0]}',
                        'message': 'Embedding dimension mismatch'
                    }
                
            except RuntimeError as e:
                print(f"❌ [Classifier] FaceNet runtime error: {e}")
                logger.error(f"FaceNet error: {e}", exc_info=True)
                return {
                    'status': 'error',
                    'error': f'FaceNet error: {str(e)}',
                    'message': 'Face recognition model error. Try restarting the server.'
                }
            except Exception as e:
                print(f"❌ [Classifier] Embedding generation error: {e}")
                logger.error(f"Embedding error: {e}", exc_info=True)
                import traceback
                traceback.print_exc()
                return {
                    'status': 'error',
                    'error': f'Embedding generation failed: {str(e)}',
                    'message': 'Failed to generate face embedding'
                }
            
            # Classify
            try:
                print("🔍 [Classifier] Classifying...")
                result = self._classify_embedding(embedding)
                print(f"✅ [Classifier] Classification result: {result['status']}")
                return result
            except Exception as e:
                print(f"❌ [Classifier] Classification error: {e}")
                return {
                    'status': 'error',
                    'error': f'Classification failed: {str(e)}',
                    'message': 'Failed to classify face'
                }
            
        except Exception as e:
            print(f"❌ [Classifier] Unexpected error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Recognition system encountered an unexpected error'
            }
    
    def _classify_embedding(self, embedding):
        """
        Classify face embedding using trained classifier
        
        Returns:
            dict with classification results
        """
        try:
            print("🔍 [Classifier] Getting classifier and encoder...")
            classifier = model_loader.get_classifier()
            label_encoder = model_loader.get_label_encoder()
            scaler = model_loader.get_scaler()
            
            if classifier is None:
                print("❌ [Classifier] Classifier is None")
                return {
                    'status': 'error',
                    'error': 'Classifier not loaded',
                    'message': 'Model not properly initialized'
                }
            
            print(f"✅ [Classifier] Classifier loaded, embedding shape: {embedding.shape}")
            
            # Reshape embedding for prediction
            embedding = embedding.reshape(1, -1)
            print(f"✅ [Classifier] Embedding reshaped: {embedding.shape}")

            # Apply scaler if it exists
            # NOTE: Embeddings are already L2-normalized by embeddings_facenet.py
            # We should NOT normalize again after scaling!
            if scaler is not None:
                try:
                    print("🔍 [Classifier] Scaling embedding with saved scaler...")
                    embedding = scaler.transform(embedding)
                    print(f"✅ [Classifier] Embedding scaled")
                except Exception as e:
                    print(f"⚠️ [Classifier] Scaler transform failed: {e}. Proceeding without scaler.")
            
            # DO NOT apply L2 normalization here!
            # Embeddings are already normalized before scaling during training
            # Normalizing again after scaling breaks the distribution
            
            # Get prediction probabilities
            try:
                # Check if classifier is a dict (new model format)
                if isinstance(classifier, dict):
                    print("🔍 [Classifier] Classifier is dict, extracting actual classifier...")
                    actual_classifier = classifier.get('classifier')
                    if actual_classifier is None:
                        print("❌ [Classifier] No 'classifier' key in dict")
                        return {
                            'status': 'error',
                            'error': 'Invalid model format',
                            'message': 'Model file is corrupted'
                        }
                    classifier = actual_classifier
                
                if hasattr(classifier, 'predict_proba'):
                    print("🔍 [Classifier] Using predict_proba...")
                    probabilities = classifier.predict_proba(embedding)[0]
                    max_prob_idx = np.argmax(probabilities)
                    confidence = probabilities[max_prob_idx]
                    print(f"✅ [Classifier] Prediction: class {max_prob_idx}, confidence {confidence:.3f}")
                else:
                    print("🔍 [Classifier] Using predict (no probabilities)...")
                    prediction = classifier.predict(embedding)[0]
                    confidence = 1.0
                    max_prob_idx = int(prediction)
                    print(f"✅ [Classifier] Prediction: class {max_prob_idx}")
            except Exception as e:
                print(f"❌ [Classifier] Prediction error: {e}")
                import traceback
                traceback.print_exc()
                return {
                    'status': 'error',
                    'error': f'Prediction failed: {str(e)}',
                    'message': 'Model prediction error'
                }
            
            # Use production threshold (0.60)
            # Faces with confidence >= 0.60 will be recognized
            NEW_THRESHOLD = 0.60
            print(f"🎯 [Classifier] Using threshold: {NEW_THRESHOLD}")
            print(f"🔍 [Classifier] Checking: confidence {confidence:.3f} >= threshold {NEW_THRESHOLD}")
            print(f"🔍 [Classifier] Top 3 predictions:")
            top_3_indices = np.argsort(probabilities)[-3:][::-1]
            for i, idx in enumerate(top_3_indices, 1):
                prob = probabilities[idx]
                if label_encoder:
                    lbl = label_encoder.inverse_transform([idx])[0]
                elif model_loader.get_classes() is not None:
                    lbl = model_loader.get_classes()[idx]
                else:
                    lbl = f"CLASS_{idx}"
                print(f"    {i}. {lbl}: {prob:.4f}")
            
            if confidence < NEW_THRESHOLD:
                print(f"⚠️ [Classifier] Low confidence: {confidence:.3f} < {NEW_THRESHOLD}")
                return {
                    'status': 'unknown',
                    'message': 'Face not recognized (low confidence)',
                    'confidence': float(confidence),
                    'top_prediction': str(predicted_label) if 'predicted_label' in locals() else 'unknown'
                }
            
            # Decode label
            try:
                if label_encoder:
                    print("🔍 [Classifier] Using label encoder...")
                    predicted_label = label_encoder.inverse_transform([max_prob_idx])[0]
                else:
                    print("🔍 [Classifier] Using class array...")
                    classes = model_loader.get_classes()
                    if classes is not None and max_prob_idx < len(classes):
                        predicted_label = classes[max_prob_idx]
                    else:
                        predicted_label = str(max_prob_idx)
                
                print(f"✅ [Classifier] Predicted label: {predicted_label}")
            except Exception as e:
                print(f"❌ [Classifier] Label decoding error: {e}")
                predicted_label = f"CLASS_{max_prob_idx}"
            
            return {
                'status': 'recognized',
                'student_id': str(predicted_label),
                'confidence': float(confidence)
            }
            
        except Exception as e:
            print(f"❌ [Classifier] Classification error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'status': 'error',
                'error': f'Classification error: {str(e)}',
                'message': 'Failed to classify embedding'
            }

# Global recognizer instance
face_recognizer = FaceRecognizer()
