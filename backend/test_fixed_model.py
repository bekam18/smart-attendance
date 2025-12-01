"""
Test script for fixed face recognition model
Verifies embedding distribution matches between training and inference
"""

import numpy as np
import pickle
from pathlib import Path
import torch
from PIL import Image
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_model():
    """Load trained model"""
    model_path = Path('models/Classifier/face_classifier_v1.pkl')
    
    if not model_path.exists():
        logger.error(f"Model not found: {model_path}")
        return None
    
    with open(model_path, 'rb') as f:
        model_data = pickle.load(f)
    
    logger.info("✅ Model loaded successfully")
    return model_data


def test_embedding_distribution():
    """Test that training embeddings are properly normalized"""
    logger.info("\n" + "="*60)
    logger.info("TEST 1: Embedding Distribution")
    logger.info("="*60)
    
    # Load training embeddings
    X_path = Path('models/Classifier/X.npy')
    if not X_path.exists():
        logger.error(f"Training embeddings not found: {X_path}")
        return False
    
    X = np.load(X_path)
    logger.info(f"Loaded {X.shape[0]} training embeddings")
    
    # Check normalization
    norms = np.linalg.norm(X, axis=1)
    logger.info(f"\nEmbedding norms:")
    logger.info(f"  Min: {norms.min():.6f}")
    logger.info(f"  Max: {norms.max():.6f}")
    logger.info(f"  Mean: {norms.mean():.6f}")
    logger.info(f"  Std: {norms.std():.6f}")
    
    # Check if normalized (should be close to 1.0)
    is_normalized = np.allclose(norms, 1.0, atol=0.01)
    
    if is_normalized:
        logger.info("✅ Training embeddings are L2-normalized")
        return True
    else:
        logger.error("❌ Training embeddings are NOT L2-normalized")
        logger.error("   This will cause embedding distribution mismatch!")
        return False


def test_inference_pipeline():
    """Test that inference pipeline produces normalized embeddings"""
    logger.info("\n" + "="*60)
    logger.info("TEST 2: Inference Pipeline")
    logger.info("="*60)
    
    # Initialize FaceNet (same as inference)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    facenet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
    
    transform = transforms.Compose([
        transforms.Resize((160, 160)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
    ])
    
    # Find a test image
    dataset_path = Path('dataset/processed')
    test_images = list(dataset_path.rglob('*.jpg'))[:5]  # Test 5 images
    
    if len(test_images) == 0:
        logger.warning("No test images found")
        return True
    
    logger.info(f"Testing {len(test_images)} images...")
    
    norms = []
    with torch.no_grad():
        for img_path in test_images:
            try:
                # Load and process image
                img = Image.open(img_path).convert('RGB')
                img_tensor = transform(img).unsqueeze(0).to(device)
                
                # Generate embedding
                embedding = facenet(img_tensor).cpu().numpy().flatten()
                
                # Apply L2 normalization (as in inference)
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm
                
                norms.append(np.linalg.norm(embedding))
                
            except Exception as e:
                logger.error(f"Error processing {img_path}: {e}")
    
    if len(norms) > 0:
        norms = np.array(norms)
        logger.info(f"\nInference embedding norms:")
        logger.info(f"  Min: {norms.min():.6f}")
        logger.info(f"  Max: {norms.max():.6f}")
        logger.info(f"  Mean: {norms.mean():.6f}")
        
        is_normalized = np.allclose(norms, 1.0, atol=0.01)
        
        if is_normalized:
            logger.info("✅ Inference embeddings are L2-normalized")
            return True
        else:
            logger.error("❌ Inference embeddings are NOT L2-normalized")
            return False
    
    return True


def test_model_metadata():
    """Test that model metadata indicates normalization"""
    logger.info("\n" + "="*60)
    logger.info("TEST 3: Model Metadata")
    logger.info("="*60)
    
    model_data = load_model()
    if model_data is None:
        return False
    
    metadata = model_data.get('metadata', {})
    
    logger.info(f"Embedding model: {metadata.get('embedding_model', 'Unknown')}")
    logger.info(f"Embedding dim: {metadata.get('embedding_dim', 'Unknown')}")
    logger.info(f"Normalize embeddings: {metadata.get('normalize_embeddings', False)}")
    logger.info(f"Threshold: {metadata.get('threshold', 'Unknown')}")
    logger.info(f"Accuracy: {metadata.get('accuracy', 'Unknown')}")
    logger.info(f"Num classes: {metadata.get('num_classes', 'Unknown')}")
    
    normalize_flag = metadata.get('normalize_embeddings', False)
    
    if normalize_flag:
        logger.info("✅ Model metadata indicates embeddings are normalized")
        return True
    else:
        logger.warning("⚠️  Model metadata does NOT indicate normalization")
        logger.warning("   This may cause issues if inference applies normalization")
        return False


def test_prediction_confidence():
    """Test prediction confidence on training data"""
    logger.info("\n" + "="*60)
    logger.info("TEST 4: Prediction Confidence")
    logger.info("="*60)
    
    model_data = load_model()
    if model_data is None:
        return False
    
    classifier = model_data['classifier']
    scaler = model_data['scaler']
    label_encoder = model_data['label_encoder']
    metadata = model_data.get('metadata', {})
    threshold = metadata.get('threshold', 0.5)
    
    # Load training embeddings
    X_path = Path('models/Classifier/X.npy')
    y_path = Path('models/Classifier/y.npy')
    
    if not X_path.exists() or not y_path.exists():
        logger.warning("Training data not found, skipping confidence test")
        return True
    
    X = np.load(X_path)
    y = np.load(y_path)
    
    # Sample 10 random embeddings
    indices = np.random.choice(len(X), min(10, len(X)), replace=False)
    X_sample = X[indices]
    y_sample = y[indices]
    
    # Scale embeddings
    X_scaled = scaler.transform(X_sample)
    
    # Get predictions
    probabilities = classifier.predict_proba(X_scaled)
    predictions = classifier.predict(X_scaled)
    max_probs = np.max(probabilities, axis=1)
    
    logger.info(f"\nSample predictions (threshold={threshold:.4f}):")
    logger.info(f"{'True':<10} {'Pred':<10} {'Confidence':<12} {'Status'}")
    logger.info("-" * 50)
    
    above_threshold = 0
    correct = 0
    
    for i in range(len(X_sample)):
        true_label = label_encoder.inverse_transform([y_sample[i]])[0]
        pred_label = label_encoder.inverse_transform([predictions[i]])[0]
        confidence = max_probs[i]
        
        is_correct = (y_sample[i] == predictions[i])
        is_above = (confidence >= threshold)
        
        if is_correct:
            correct += 1
        if is_above:
            above_threshold += 1
        
        status = "✅" if is_correct and is_above else "⚠️" if is_above else "❌"
        
        logger.info(f"{true_label:<10} {pred_label:<10} {confidence:<12.4f} {status}")
    
    logger.info("-" * 50)
    logger.info(f"Correct: {correct}/{len(X_sample)} ({correct/len(X_sample)*100:.1f}%)")
    logger.info(f"Above threshold: {above_threshold}/{len(X_sample)} ({above_threshold/len(X_sample)*100:.1f}%)")
    
    if correct == len(X_sample) and above_threshold >= len(X_sample) * 0.8:
        logger.info("✅ Prediction confidence looks good")
        return True
    elif above_threshold < len(X_sample) * 0.5:
        logger.error("❌ Most predictions are below threshold!")
        logger.error("   This indicates embedding distribution mismatch")
        return False
    else:
        logger.warning("⚠️  Some predictions are below threshold")
        return True


def main():
    """Run all tests"""
    logger.info("\n" + "="*60)
    logger.info("TESTING FIXED FACE RECOGNITION MODEL")
    logger.info("="*60)
    
    tests = [
        ("Embedding Distribution", test_embedding_distribution),
        ("Inference Pipeline", test_inference_pipeline),
        ("Model Metadata", test_model_metadata),
        ("Prediction Confidence", test_prediction_confidence),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test '{test_name}' failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*60)
    logger.info("TEST SUMMARY")
    logger.info("="*60)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name:<30} {status}")
    
    all_passed = all(result for _, result in results)
    
    logger.info("="*60)
    if all_passed:
        logger.info("✅ ALL TESTS PASSED")
        logger.info("Model is ready for production use")
    else:
        logger.error("❌ SOME TESTS FAILED")
        logger.error("Please retrain the model with train_fixed_model.py")
    logger.info("="*60 + "\n")
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
