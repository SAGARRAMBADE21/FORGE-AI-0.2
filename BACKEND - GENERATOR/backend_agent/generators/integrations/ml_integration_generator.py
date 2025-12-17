"""
ML Integration Generator Agent
Generates ML model endpoints and integration code.
"""

from typing import Dict, Any, List
from jinja2 import Template


class MLIntegrationGeneratorAgent:
    """Generates ML integration endpoints."""
    
    def __init__(self, framework: str, llm_config: Dict[str, Any]):
        self.framework = framework
    
    def generate(self, ml_features: List[str]) -> Dict[str, str]:
        """Generate ML integration code."""
        
        if self.framework == "fastapi":
            return self._generate_fastapi_ml()
        elif self.framework == "express":
            return self._generate_express_ml()
        else:
            return {}
    
    def _generate_fastapi_ml(self) -> Dict[str, str]:
        """Generate FastAPI ML endpoints."""
        
        ml_files = {}
        
        # ML Service
        ml_service_template = '''"""Machine Learning service."""

import pickle
import numpy as np
from pathlib import Path
from typing import List, Dict, Any


class MLService:
    """ML Model service for predictions."""
    
    def __init__(self):
        self.model = None
        self.model_path = Path("models/model.pkl")
        self.load_model()
    
    def load_model(self):
        """Load ML model from disk."""
        try:
            if self.model_path.exists():
                with open(self.model_path, 'rb') as f:
                    self.model = pickle.load(f)
                print(f"Model loaded from {self.model_path}")
            else:
                print(f"Model file not found at {self.model_path}")
                # Initialize with dummy model for development
                self.model = None
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def predict(self, features: List[float]) -> Dict[str, Any]:
        """Make prediction."""
        if self.model is None:
            # Return dummy prediction for development
            return {
                "prediction": 0,
                "probability": 0.5,
                "message": "Using dummy model - train and save model first"
            }
        
        try:
            # Convert to numpy array
            X = np.array(features).reshape(1, -1)
            
            # Make prediction
            prediction = self.model.predict(X)[0]
            
            # Get probability if available
            probability = None
            if hasattr(self.model, 'predict_proba'):
                probability = self.model.predict_proba(X)[0].tolist()
            
            return {
                "prediction": int(prediction) if isinstance(prediction, np.integer) else float(prediction),
                "probability": probability
            }
        except Exception as e:
            raise ValueError(f"Prediction error: {str(e)}")
    
    def batch_predict(self, features_list: List[List[float]]) -> List[Dict[str, Any]]:
        """Make batch predictions."""
        return [self.predict(features) for features in features_list]


# Global ML service instance
ml_service = MLService()
'''
        
        # ML Routes
        ml_routes_template = '''"""Machine Learning API routes."""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List

from app.services.ml_service import ml_service

router = APIRouter(
    prefix="/ml",
    tags=["machine-learning"]
)


class PredictionRequest(BaseModel):
    """Prediction request schema."""
    features: List[float] = Field(..., description="Input features for prediction")
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": [5.1, 3.5, 1.4, 0.2]
            }
        }


class PredictionResponse(BaseModel):
    """Prediction response schema."""
    prediction: float | int
    probability: List[float] | None = None
    message: str | None = None


class BatchPredictionRequest(BaseModel):
    """Batch prediction request schema."""
    batch: List[List[float]] = Field(..., description="Batch of feature arrays")


class BatchPredictionResponse(BaseModel):
    """Batch prediction response schema."""
    predictions: List[PredictionResponse]


@router.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Make ML prediction.
    
    - **features**: List of numerical features for the model
    """
    try:
        result = ml_service.predict(request.features)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )


@router.post("/predict/batch", response_model=BatchPredictionResponse)
async def batch_predict(request: BatchPredictionRequest):
    """
    Make batch ML predictions.
    
    - **batch**: List of feature arrays
    """
    try:
        results = ml_service.batch_predict(request.batch)
        return {"predictions": results}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch prediction failed: {str(e)}"
        )


@router.get("/model/info")
async def model_info():
    """Get model information."""
    return {
        "model_loaded": ml_service.model is not None,
        "model_path": str(ml_service.model_path),
        "model_type": type(ml_service.model).__name__ if ml_service.model else None
    }
'''
        
        # Training script template
        train_script_template = '''"""ML model training script."""

import pickle
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report


def train_model():
    """Train and save ML model."""
    
    # TODO: Load your actual dataset
    # Example with dummy data
    print("Generating dummy training data...")
    X = np.random.rand(1000, 4)
    y = np.random.randint(0, 3, 1000)
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train model
    print("Training model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))
    
    # Save model
    model_path = Path("models/model.pkl")
    model_path.parent.mkdir(exist_ok=True)
    
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    
    print(f"\nModel saved to {model_path}")


if __name__ == "__main__":
    train_model()
'''
        
        ml_files['app/services/ml_service.py'] = ml_service_template
        ml_files['app/api/routes/ml.py'] = ml_routes_template
        ml_files['scripts/train_model.py'] = train_script_template
        
        return ml_files
    
    def _generate_express_ml(self) -> Dict[str, str]:
        """Generate Express ML endpoints."""
        
        ml_files = {}
        
        # ML Service
        ml_service_template = '''const tf = require('@tensorflow/tfjs-node');
const path = require('path');

/**
 * Machine Learning Service
 */
class MLService {
  constructor() {
    this.model = null;
    this.modelPath = path.join(__dirname, '../../models/model.json');
  }

  async loadModel() {
    try {
      this.model = await tf.loadLayersModel(`file://${this.modelPath}`);
      console.log('Model loaded successfully');
    } catch (error) {
      console.error('Error loading model:', error);
      this.model = null;
    }
  }

  async predict(features) {
    if (!this.model) {
      throw new Error('Model not loaded');
    }

    try {
      const inputTensor = tf.tensor2d([features]);
      const prediction = this.model.predict(inputTensor);
      const result = await prediction.data();
      
      inputTensor.dispose();
      prediction.dispose();
      
      return Array.from(result);
    } catch (error) {
      throw new Error(`Prediction error: ${error.message}`);
    }
  }

  async batchPredict(featuresList) {
    const predictions = [];
    for (const features of featuresList) {
      const result = await this.predict(features);
      predictions.push(result);
    }
    return predictions;
  }
}

module.exports = new MLService();
'''
        
        # ML Routes
        ml_routes_template = '''const express = require('express');
const router = express.Router();
const mlService = require('../services/mlService');

// Initialize model on startup
mlService.loadModel();

/**
 * POST /api/ml/predict
 * Make ML prediction
 */
router.post('/predict', async (req, res) => {
  try {
    const { features } = req.body;
    
    if (!features || !Array.isArray(features)) {
      return res.status(400).json({ error: 'Features array required' });
    }
    
    const prediction = await mlService.predict(features);
    
    res.json({
      prediction,
      features
    });
  } catch (error) {
    console.error('Prediction error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * POST /api/ml/predict/batch
 * Make batch ML predictions
 */
router.post('/predict/batch', async (req, res) => {
  try {
    const { batch } = req.body;
    
    if (!batch || !Array.isArray(batch)) {
      return res.status(400).json({ error: 'Batch array required' });
    }
    
    const predictions = await mlService.batchPredict(batch);
    
    res.json({
      predictions,
      count: predictions.length
    });
  } catch (error) {
    console.error('Batch prediction error:', error);
    res.status(500).json({ error: error.message });
  }
});

/**
 * GET /api/ml/model/info
 * Get model information
 */
router.get('/model/info', (req, res) => {
  res.json({
    modelLoaded: mlService.model !== null,
    modelPath: mlService.modelPath
  });
});

module.exports = router;
'''
        
        ml_files['src/services/mlService.js'] = ml_service_template
        ml_files['src/routes/ml.js'] = ml_routes_template
        
        return ml_files
