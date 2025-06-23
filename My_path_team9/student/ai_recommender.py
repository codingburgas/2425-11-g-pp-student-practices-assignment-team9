import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from datetime import datetime
from .. import db
from .models import Survey, VideoSubmission
from ..teacher.models import MotivationalVideo, VideoRating


class VideoRecommender:
    """
    A logistic regression-based recommendation system for educational videos
    based on student survey responses and video ratings.
    """

    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_names = [
            'memory_method', 'online_learning', 'video_helpful',
            'videos_for_tests', 'interest_level', 'confidence',
            'study_time', 'ideal_length', 'review_before_class'
        ]
        # Use absolute paths for model files
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, 'recommendation_model.joblib')
        self.scaler_path = os.path.join(current_dir, 'scaler.joblib')
        self.encoders_path = os.path.join(current_dir, 'encoders.joblib')

    def prepare_survey_features(self, survey):
        """
        Convert survey data into numerical features for the model.

        Args:
            survey: Survey object from database

        Returns:
            numpy array of features
        """
        features = []

        # Memory method encoding
        memory_method_map = {
            'notes': 0, 'videos': 1, 'repetition': 0.5, 'discussion': 0.3
        }
        features.append(memory_method_map.get(survey.memory_method, 0))

        # Online learning frequency
        online_learning_map = {
            'daily': 1, 'few_times': 0.75, 'rarely': 0.25, 'never': 0
        }
        features.append(online_learning_map.get(survey.online_learning, 0))

        # Video helpfulness
        video_helpful_map = {
            'very': 1, 'somewhat': 0.7, 'not_much': 0.3, 'not_at_all': 0
        }
        features.append(video_helpful_map.get(survey.video_helpful, 0))

        # Videos for tests
        videos_for_tests_map = {
            'always': 1, 'sometimes': 0.7, 'only_if_needed': 0.4, 'never': 0
        }
        features.append(videos_for_tests_map.get(survey.videos_for_tests, 0))

        # Interest level
        interest_level_map = {
            'very_high': 1, 'high': 0.8, 'medium': 0.5, 'low': 0.2, 'very_low': 0
        }
        features.append(interest_level_map.get(survey.interest_level, 0.5))

        # Confidence level
        confidence_map = {
            'very_confident': 1, 'confident': 0.8, 'neutral': 0.5,
            'not_confident': 0.2, 'very_not_confident': 0
        }
        features.append(confidence_map.get(survey.confidence, 0.5))

        # Study time
        study_time_map = {
            'more_than_4_hours': 1, '2_4_hours': 0.75, '1_2_hours': 0.5,
            'less_than_1_hour': 0.25, 'no_time': 0
        }
        features.append(study_time_map.get(survey.study_time, 0.5))

        # Ideal video length
        ideal_length_map = {
            'less_than_5_min': 0.2, '5_10_min': 0.4, '10_15_min': 0.6,
            '15_30_min': 0.8, 'more_than_30_min': 1
        }
        features.append(ideal_length_map.get(survey.ideal_length, 0.6))

        # Review before class
        review_map = {
            'always': 1, 'sometimes': 0.7, 'rarely': 0.3, 'never': 0
        }
        features.append(review_map.get(survey.review_before_class, 0.5))

        return np.array(features)

    def generate_training_data(self):
        """
        Generate synthetic training data based on survey responses and video ratings.
        This creates realistic training examples for the logistic regression model.

        Returns:
            tuple: (X_train, y_train) - features and labels for training
        """
        # Get all surveys and video ratings
        surveys = Survey.query.all()
        video_ratings = VideoRating.query.all()

        X_train = []
        y_train = []

        # Create training examples from existing data
        for survey in surveys:
            features = self.prepare_survey_features(survey)

            # Get user's video ratings to create positive/negative examples
            user_ratings = VideoRating.query.filter_by(student_id=survey.user_id).all()

            if user_ratings:
                for rating in user_ratings:
                    # Positive example if rating >= 4, negative if <= 2
                    if rating.rating >= 4:
                        X_train.append(features)
                        y_train.append(1)  # Positive recommendation
                    elif rating.rating <= 2:
                        X_train.append(features)
                        y_train.append(0)  # Negative recommendation

        # Generate synthetic data if we don't have enough training examples
        if len(X_train) < 50:
            X_train, y_train = self._generate_synthetic_data(X_train, y_train)

        return np.array(X_train), np.array(y_train)

    def _generate_synthetic_data(self, X_existing, y_existing):
        """
        Generate synthetic training data to ensure sufficient training examples.

        Args:
            X_existing: Existing feature arrays
            y_existing: Existing labels

        Returns:
            tuple: (X_combined, y_combined) - combined real and synthetic data
        """
        X_synthetic = []
        y_synthetic = []

        # Generate synthetic examples based on common patterns
        synthetic_patterns = [
            # High video preference pattern
            [1, 1, 1, 1, 0.8, 0.8, 0.75, 0.6, 0.7],  # Features for video lovers
            # Low video preference pattern
            [0, 0.25, 0.3, 0, 0.5, 0.5, 0.5, 0.4, 0.3],  # Features for non-video learners
            # Moderate video preference pattern
            [0.5, 0.75, 0.7, 0.7, 0.6, 0.6, 0.6, 0.6, 0.5],  # Balanced learners
            # High confidence, low video need
            [0, 0.5, 0.3, 0.4, 0.8, 1, 0.75, 0.4, 0.7],
            # Low confidence, high video need
            [1, 1, 1, 1, 0.4, 0.2, 0.5, 0.8, 0.7],
        ]

        for pattern in synthetic_patterns:
            # Add some noise to make it more realistic
            for _ in range(10):
                noisy_pattern = pattern + np.random.normal(0, 0.1, len(pattern))
                noisy_pattern = np.clip(noisy_pattern, 0, 1)  # Keep values between 0 and 1

                X_synthetic.append(noisy_pattern)

                # Determine label based on video preference features
                video_preference_score = (noisy_pattern[0] + noisy_pattern[2] + noisy_pattern[3]) / 3
                if video_preference_score > 0.6:
                    y_synthetic.append(1)  # Positive
                else:
                    y_synthetic.append(0)  # Negative

        # Combine existing and synthetic data
        X_combined = np.vstack([X_existing, X_synthetic]) if len(X_existing) > 0 else np.array(X_synthetic)
        y_combined = np.concatenate([y_existing, y_synthetic]) if len(y_existing) > 0 else np.array(y_synthetic)

        return X_combined, y_combined

    def train_model(self):
        """
        Train the logistic regression model on survey and rating data.

        Returns:
            bool: True if training was successful
        """
        try:
            # Generate training data
            X_train, y_train = self.generate_training_data()

            if len(X_train) == 0:
                print("No training data available")
                return False

            # Split data for validation
            X_train_split, X_val, y_train_split, y_val = train_test_split(
                X_train, y_train, test_size=0.2, random_state=42
            )

            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train_split)
            X_val_scaled = self.scaler.transform(X_val)

            # Train logistic regression model
            self.model = LogisticRegression(
                random_state=42,
                max_iter=1000,
                C=1.0,
                solver='liblinear'
            )

            self.model.fit(X_train_scaled, y_train_split)

            # Evaluate model
            y_pred = self.model.predict(X_val_scaled)
            accuracy = accuracy_score(y_val, y_pred)

            print(f"Model trained successfully. Validation accuracy: {accuracy:.3f}")

            # Save the model
            self.save_model()

            return True

        except Exception as e:
            print(f"Error training model: {str(e)}")
            return False

    def predict_video_preference(self, survey):
        """
        Predict whether a student would like a video based on their survey.

        Args:
            survey: Survey object from database

        Returns:
            float: Probability of positive preference (0-1)
        """
        if self.model is None:
            self.load_model()

        if self.model is None:
            # Fallback to simple heuristic if model not available
            return self._fallback_prediction(survey)

        # Prepare features
        features = self.prepare_survey_features(survey)
        features_scaled = self.scaler.transform(features.reshape(1, -1))

        # Get prediction probability
        prob_positive = self.model.predict_proba(features_scaled)[0][1]

        return prob_positive

    def _fallback_prediction(self, survey):
        """
        Fallback prediction method when model is not available.

        Args:
            survey: Survey object

        Returns:
            float: Simple heuristic score
        """
        # Simple heuristic based on key video preference indicators
        memory_method_map = {'notes': 0, 'videos': 1, 'repetition': 0.5, 'discussion': 0.3}
        video_helpful_map = {'very': 1, 'somewhat': 0.7, 'not_much': 0.3, 'not_at_all': 0}
        videos_for_tests_map = {'always': 1, 'sometimes': 0.7, 'only_if_needed': 0.4, 'never': 0}

        score = (
                memory_method_map.get(survey.memory_method, 0) * 0.4 +
                video_helpful_map.get(survey.video_helpful, 0) * 0.4 +
                videos_for_tests_map.get(survey.videos_for_tests, 0) * 0.2
        )

        return score

    def get_recommendations(self, survey, videos, top_k=5):
        """
        Get top video recommendations for a student based on their survey.

        Args:
            survey: Survey object from database
            videos: List of available videos
            top_k: Number of top recommendations to return

        Returns:
            list: List of dictionaries with video, score, and reason
        """
        if not videos:
            return []

        # Get base preference score
        base_score = self.predict_video_preference(survey)

        recommendations = []

        for video in videos:
            # Calculate video-specific score
            video_score = self._calculate_video_score(video, survey, base_score)

            # Generate recommendation reason
            reason = self._generate_recommendation_reason(video, survey, video_score)

            recommendations.append({
                'video': video,
                'score': video_score,
                'reason': reason
            })

        # Sort by score and return top_k
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:top_k]

    def _calculate_video_score(self, video, survey, base_score):
        """
        Calculate a specific score for a video based on survey and video characteristics.

        Args:
            video: Video object
            survey: Survey object
            base_score: Base preference score from model

        Returns:
            float: Final recommendation score
        """
        score = base_score

        # Subject matching bonus
        if survey.hardest_subject.lower() in video.video_link.lower():
            score += 0.2

        if survey.favorite_subject.lower() in video.video_link.lower():
            score += 0.1

        # Video rating bonus (if available)
        if hasattr(video, 'ratings') and video.ratings:
            avg_rating = sum(r.rating for r in video.ratings) / len(video.ratings)
            score += (avg_rating - 3) * 0.05  # Bonus for high ratings

        # Length preference matching
        ideal_length_map = {
            'less_than_5_min': 0.2, '5_10_min': 0.4, '10_15_min': 0.6,
            '15_30_min': 0.8, 'more_than_30_min': 1
        }
        length_preference = ideal_length_map.get(survey.ideal_length, 0.6)

        # Add small variation based on video ID to avoid identical scores
        unique_offset = (video.id % 100) * 0.001

        # Final score with caps
        final_score = min(max(score + unique_offset, 0), 1)

        return final_score

    def _generate_recommendation_reason(self, video, survey, score):
        """
        Generate a human-readable reason for the recommendation.

        Args:
            video: Video object
            survey: Survey object
            score: Recommendation score

        Returns:
            str: Explanation for the recommendation
        """
        reasons = []

        if score > 0.8:
            reasons.append("This video highly matches your learning preferences")
        elif score > 0.6:
            reasons.append("This video aligns well with your study habits")
        else:
            reasons.append("This video may be helpful for your learning style")

        # Add specific reasons based on survey data
        if survey.memory_method == 'videos':
            reasons.append("and your preference for video-based learning")

        if survey.video_helpful in ['very', 'somewhat']:
            reasons.append("and your positive experience with educational videos")

        if survey.hardest_subject.lower() in video.video_link.lower():
            reasons.append(f"and may help with your challenging subject ({survey.hardest_subject})")

        if survey.favorite_subject.lower() in video.video_link.lower():
            reasons.append(f"and relates to your favorite subject ({survey.favorite_subject})")

        # Add rating-based reason if available
        if hasattr(video, 'ratings') and video.ratings:
            avg_rating = sum(r.rating for r in video.ratings) / len(video.ratings)
            if avg_rating >= 4:
                reasons.append("and has received excellent ratings from other students")

        return " ".join(reasons)

    def save_model(self):
        """Save the trained model and scaler to disk."""
        try:
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            joblib.dump(self.label_encoders, self.encoders_path)
            print("Model saved successfully")
        except Exception as e:
            print(f"Error saving model: {str(e)}")

    def load_model(self):
        """Load the trained model and scaler from disk."""
        try:
            if os.path.exists(self.model_path):
                self.model = joblib.load(self.model_path)
                self.scaler = joblib.load(self.scaler_path)
                self.label_encoders = joblib.load(self.encoders_path)
                print("Model loaded successfully")
                return True
            else:
                print("No saved model found")
                return False
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False


# Global recommender instance
recommender = VideoRecommender()