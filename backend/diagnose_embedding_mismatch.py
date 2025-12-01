"""
Diagnostic Script: Detect Embedding Distribution Mismatch
Identifies if training and inference use different preprocessing
"""

import numpy as np
import pickle
from pathlib import Path
import torch
from PIL import Image
from torchvision import transforms
from facenet_pytorch import InceptionResnetV1
import logging
import sys

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def diagnose():
    """Run comprehensive diagnosis"""
    
    logger.info("\n" + "="*80)
    logger.info("EMBEDDING DISTRIBUTION MISMATCH DIAGNOSTIC")
    logger.info("="*80)
    
    issues_found = []
    warnings_found = []
    
    # Check 1: Model file exists
    logger.info("\n[1/6] Checking model file...")
    model_path = Path('models/Classifier/face_classifier_v1.pkl')
    
    if not model_path.exists():
        logger.error(f"❌ Model file not found: {model_path}")
        logger.error("   Please train a model first")
        return False
    
    logger.info(f"✅ Model file found: {model_path}")
    
    # Load model
    try:
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        logger.info("✅ Model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        return False
    
    # Check 2: Training embeddings normalization
    logger.info("\n[2/6] Checking training embeddings...")
    X_path = Path('models/Classifier/X.npy')
    
    if not X_path.exists():
        logger.warning(f"⚠️  Training embeddings not found: {X_path}")
        warnings_found.append("Training embeddings file missing")
    else:
        X = np.load(X_path)
        norms = np.linalg.norm(X, axis=1)
        
        logger.info(f"   Loaded {X.shape[0]} embeddings, shape: {X.shape}")
        logger.info(f"   Embedding norms:")
        logger.info(f"     Min:  {norms.min():.6f}")
        logger.info(f"     Max:  {norms.max():.6f}")
        logger.info(f"     Mean: {norms.mean():.6f}")
        logger.info(f"     Std:  {norms.std():.6f}")
        
        # Check if normalized
        is_normalized = np.allclose(norms, 1.0, atol=0.01)
        
        if is_normalized:
            logger.info("   ✅ Training embeddings are L2-normalized (unit length)")
        else:
            logger.error("   ❌ Training embeddings are NOT L2-normalized")
            logger.error("      Expected norm ≈ 1.0, but found varying norms")
            issues_found.append("Training embeddings not normalized")
    
    # Check 3: Model metadata
    logger.info("\n[3/6] Checking model metadata...")
    metadata = model_data.get('metadata', {})
    
    if not metadata:
        logger.warning("⚠️  No metadata found in model")
        warnings_found.append("Missing model metadata")
    else:
        logger.info(f"   Embedding model: {metadata.get('embedding_model', 'Unknown')}")
        logger.info(f"   Pretrained on: {metadata.get('pretrained_on', 'Unknown')}")
        logger.info(f"   Embedding dim: {metadata.get('embedding_dim', 'Unknown')}")
        logger.info(f"   Num classes: {metadata.get('num_classes', 'Unknown')}")
        logger.info(f"   Threshold: {metadata.get('threshold', 'Unknown')}")
        logger.info(f"   Accuracy: {metadata.get('accuracy', 'Unknown')}")
        
        normalize_flag = metadata.get('normalize_embeddings', None)
        
        if normalize_flag is None:
            logger.warning("   ⚠️  'normalize_embeddings' flag not found in metadata")
            logger.warning("      Cannot determine if normalization was applied during training")
            warnings_found.append("Missing normalization flag in metadata")
        elif normalize_flag:
            logger.info("   ✅ Metadata indicates embeddings are normalized")
        else:
            logger.error("   ❌ Metadata indicates embeddings are NOT normalized")
            logger.error("      But inference code applies normalization!")
            issues_found.append("Metadata indicates no normalization")
    
    # Check 4: Inference pipeline
    logger.info("\n[4/6] Checking inference pipeline...")
    
    # Check if embeddings_facenet.py applies normalization
    embeddings_file = Path('recognizer/embeddings_facenet.py')
    
    if embeddings_file.exists():
        with open(embeddings_file, 'r', encoding='utf-8') as f:
            code = f.read()
        
        if 'np.linalg.norm' in code and '/ norm' in code:
            logger.info("   ✅ Inference code applies L2 normalization")
        else:
            logger.warning("   ⚠️  Inference code may not apply L2 normalization")
            warnings_found.append("Inference normalization unclear")
    else:
        logger.warning(f"   ⚠️  Inference file not found: {embeddings_file}")
    
    # Check 5: Test inference on sample image
    logger.info("\n[5/6] Testing inference pipeline...")
    
    dataset_path = Path('dataset/processed')
    test_images = list(dataset_path.rglob('*.jpg'))[:3]
    
    if len(test_images) == 0:
        logger.warning("   ⚠️  No test images found, skipping inference test")
        warnings_found.append("No test images available")
    else:
        try:
            device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
            facenet = InceptionResnetV1(pretrained='vggface2').eval().to(device)
            
            transform = transforms.Compose([
                transforms.Resize((160, 160)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])
            ])
            
            inference_norms = []
            
            with torch.no_grad():
                for img_path in test_images:
                    img = Image.open(img_path).convert('RGB')
                    img_tensor = transform(img).unsqueeze(0).to(device)
                    embedding = facenet(img_tensor).cpu().numpy().flatten()
                    
                    # Apply normalization (as in inference)
                    norm = np.linalg.norm(embedding)
                    if norm > 0:
                        embedding = embedding / norm
                    
                    inference_norms.append(np.linalg.norm(embedding))
            
            inference_norms = np.array(inference_norms)
            
            logger.info(f"   Tested {len(test_images)} images")
            logger.info(f"   Inference embedding norms:")
            logger.info(f"     Min:  {inference_norms.min():.6f}")
            logger.info(f"     Max:  {inference_norms.max():.6f}")
            logger.info(f"     Mean: {inference_norms.mean():.6f}")
            
            is_normalized = np.allclose(inference_norms, 1.0, atol=0.01)
            
            if is_normalized:
                logger.info("   ✅ Inference produces normalized embeddings")
            else:
                logger.error("   ❌ Inference does NOT produce normalized embeddings")
                issues_found.append("Inference embeddings not normalized")
                
        except Exception as e:
            logger.error(f"   ❌ Inference test failed: {e}")
            issues_found.append(f"Inference test error: {e}")
    
    # Check 6: Prediction confidence
    logger.info("\n[6/6] Checking prediction confidence...")
    
    if X_path.exists():
        try:
            X = np.load(X_path)
            y = np.load(Path('models/Classifier/y.npy'))
            
            classifier = model_data['classifier']
            scaler = model_data.get('scaler')
            threshold = metadata.get('threshold', 0.5)
            
            # Sample embeddings
            sample_size = min(20, len(X))
            indices = np.random.choice(len(X), sample_size, replace=False)
            X_sample = X[indices]
            y_sample = y[indices]
            
            # Scale if scaler exists
            if scaler:
                X_scaled = scaler.transform(X_sample)
            else:
                X_scaled = X_sample
            
            # Predict
            probabilities = classifier.predict_proba(X_scaled)
            predictions = classifier.predict(X_scaled)
            max_probs = np.max(probabilities, axis=1)
            
            # Calculate statistics
            correct = (predictions == y_sample).sum()
            above_threshold = (max_probs >= threshold).sum()
            
            logger.info(f"   Tested {sample_size} training samples")
            logger.info(f"   Confidence statistics:")
            logger.info(f"     Min:  {max_probs.min():.4f}")
            logger.info(f"     Max:  {max_probs.max():.4f}")
            logger.info(f"     Mean: {max_probs.mean():.4f}")
            logger.info(f"   Correct predictions: {correct}/{sample_size} ({correct/sample_size*100:.1f}%)")
            logger.info(f"   Above threshold ({threshold:.4f}): {above_threshold}/{sample_size} ({above_threshold/sample_size*100:.1f}%)")
            
            if max_probs.mean() < 0.5:
                logger.error("   ❌ CRITICAL: Average confidence is very low (<0.5)")
                logger.error("      This strongly indicates embedding distribution mismatch!")
                issues_found.append("Very low prediction confidence")
            elif max_probs.mean() < threshold:
                logger.warning(f"   ⚠️  Average confidence ({max_probs.mean():.4f}) is below threshold ({threshold:.4f})")
                logger.warning("      This may indicate embedding distribution mismatch")
                warnings_found.append("Low average confidence")
            else:
                logger.info("   ✅ Prediction confidence looks good")
                
        except Exception as e:
            logger.error(f"   ❌ Confidence test failed: {e}")
            issues_found.append(f"Confidence test error: {e}")
    
    # Summary
    logger.info("\n" + "="*80)
    logger.info("DIAGNOSIS SUMMARY")
    logger.info("="*80)
    
    if len(issues_found) == 0 and len(warnings_found) == 0:
        logger.info("✅ NO ISSUES FOUND")
        logger.info("   Model appears to be correctly trained")
        logger.info("   Training and inference use consistent preprocessing")
        return True
    
    if len(issues_found) > 0:
        logger.error(f"\n❌ CRITICAL ISSUES FOUND ({len(issues_found)}):")
        for i, issue in enumerate(issues_found, 1):
            logger.error(f"   {i}. {issue}")
    
    if len(warnings_found) > 0:
        logger.warning(f"\n⚠️  WARNINGS ({len(warnings_found)}):")
        for i, warning in enumerate(warnings_found, 1):
            logger.warning(f"   {i}. {warning}")
    
    # Recommendations
    logger.info("\n" + "="*80)
    logger.info("RECOMMENDATIONS")
    logger.info("="*80)
    
    if len(issues_found) > 0:
        logger.info("\n🔧 REQUIRED ACTIONS:")
        logger.info("   1. Delete all old model files:")
        logger.info("      - backend/models/Classifier/*")
        logger.info("   2. Retrain model with fixed training script:")
        logger.info("      python backend/train_fixed_model.py")
        logger.info("   3. Test the new model:")
        logger.info("      python backend/test_fixed_model.py")
        logger.info("   4. Restart backend server")
    
    if len(warnings_found) > 0:
        logger.info("\n⚠️  SUGGESTED ACTIONS:")
        logger.info("   - Review warnings above")
        logger.info("   - Consider retraining if confidence is low")
    
    logger.info("\n" + "="*80)
    
    return len(issues_found) == 0


if __name__ == '__main__':
    success = diagnose()
    sys.exit(0 if success else 1)
