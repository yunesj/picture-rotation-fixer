#!/usr/bin/env python3
"""
Comprehensive pytest test suite for the enhanced picture rotation fixer.
"""

import os
import shutil
import sys
import tempfile
from unittest.mock import Mock, patch

import numpy as np
import pytest
from PIL import Image

# Add parent directory to path to import rotate module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rotate import (
    auto_rotate,
    detect_faces,
    detect_objects_yolo,
    get_model_path,
    process_directory,
    process_single_image,
)


class TestImageCreation:
    """Test utilities for creating test images"""

    @staticmethod
    def create_test_image(width=640, height=480, color=(255, 0, 0)):
        """Create a simple test image"""
        img = Image.new("RGB", (width, height), color)
        return img

    @staticmethod
    def create_cv2_image(width=640, height=480, color=(100, 100, 100)):
        """Create a test image in OpenCV format"""
        img = np.zeros((height, width, 3), dtype=np.uint8)
        img[:] = color
        return img


class TestFaceDetection:
    """Test face detection functionality"""

    def test_detect_faces_empty_image(self):
        """Test face detection on empty image"""
        test_img = TestImageCreation.create_cv2_image()
        result = detect_faces(test_img)
        assert result is False, "Should not detect faces in empty image"

    def test_detect_faces_with_mock_faces(self):
        """Test face detection with mocked face cascade"""
        test_img = TestImageCreation.create_cv2_image()

        with patch("cv2.CascadeClassifier") as mock_cascade_class:
            mock_cascade = Mock()
            mock_cascade.detectMultiScale.return_value = np.array(
                [[10, 10, 50, 50]]
            )  # Mock face detection
            mock_cascade_class.return_value = mock_cascade

            result = detect_faces(test_img)
            assert result is True, "Should detect mocked faces"

    def test_detect_faces_no_faces_found(self):
        """Test face detection when no faces are found"""
        test_img = TestImageCreation.create_cv2_image()

        with patch("cv2.CascadeClassifier") as mock_cascade_class:
            mock_cascade = Mock()
            mock_cascade.detectMultiScale.return_value = np.array([])  # No faces
            mock_cascade_class.return_value = mock_cascade

            result = detect_faces(test_img)
            assert result is False, "Should not detect faces when none found"


class TestYOLODetection:
    """Test YOLO object detection functionality"""

    def test_detect_objects_yolo_with_detections(self):
        """Test YOLO detection with successful object detection"""
        test_img = TestImageCreation.create_cv2_image()

        # Mock YOLO model and results
        mock_model = Mock()
        mock_result = Mock()
        mock_result.boxes = Mock()
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = np.array(
            [0.8, 0.9]
        )  # High confidence
        mock_result.obb = None
        mock_model.return_value = [mock_result]

        result = detect_objects_yolo(test_img, mock_model, confidence_threshold=0.5)
        assert result is True, "Should detect objects with high confidence"

    def test_detect_objects_yolo_low_confidence(self):
        """Test YOLO detection with low confidence detections"""
        test_img = TestImageCreation.create_cv2_image()

        mock_model = Mock()
        mock_result = Mock()
        mock_result.boxes = Mock()
        mock_result.boxes.conf.cpu.return_value.numpy.return_value = np.array(
            [0.2, 0.3]
        )  # Low confidence
        mock_result.obb = None
        mock_model.return_value = [mock_result]

        result = detect_objects_yolo(test_img, mock_model, confidence_threshold=0.5)
        assert result is False, "Should not detect objects with low confidence"

    def test_detect_objects_yolo_with_obb(self):
        """Test YOLO detection with oriented bounding boxes"""
        test_img = TestImageCreation.create_cv2_image()

        mock_model = Mock()
        mock_result = Mock()
        mock_result.boxes = None
        mock_result.obb = Mock()
        mock_result.obb.conf.cpu.return_value.numpy.return_value = np.array(
            [0.7]
        )  # Good confidence
        mock_model.return_value = [mock_result]

        result = detect_objects_yolo(test_img, mock_model, confidence_threshold=0.5)
        assert result is True, "Should detect objects with OBB"

    def test_detect_objects_yolo_exception_handling(self):
        """Test YOLO detection exception handling"""
        test_img = TestImageCreation.create_cv2_image()

        mock_model = Mock()
        mock_model.side_effect = Exception("Test exception")

        result = detect_objects_yolo(test_img, mock_model)
        assert result is False, "Should return False on exception"


class TestModelPath:
    """Test model path functionality"""

    def test_get_model_path_not_frozen(self):
        """Test model path when not running as PyInstaller bundle"""
        with patch("sys.frozen", False, create=True):
            result = get_model_path()
            assert result == "yolo11n.pt", "Should return default model name"

    def test_get_model_path_frozen_with_bundle(self):
        """Test model path when running as PyInstaller bundle with bundled model"""
        with patch("sys.frozen", True, create=True), patch(
            "sys._MEIPASS", "/fake/bundle/path", create=True
        ), patch("os.path.exists") as mock_exists:
            mock_exists.return_value = True
            result = get_model_path()
            expected_path = "/fake/bundle/path/ultralytics/weights/yolo11n.pt"
            assert result == expected_path, "Should return bundled model path"

    def test_get_model_path_frozen_no_bundle(self):
        """Test model path when running as PyInstaller bundle without bundled model"""
        with patch("sys.frozen", True, create=True), patch(
            "sys._MEIPASS", "/fake/bundle/path", create=True
        ), patch("os.path.exists") as mock_exists:
            mock_exists.return_value = False
            result = get_model_path()
            assert (
                result == "yolo11n.pt"
            ), "Should return default model name if bundle not found"


class TestAutoRotate:
    """Test auto rotation functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")

        # Create a test image
        test_img = TestImageCreation.create_test_image()
        test_img.save(self.test_image_path)

    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    @patch("rotate.detect_faces")
    @patch("rotate.Image.fromarray")
    def test_auto_rotate_face_detected_at_0_degrees(
        self, mock_fromarray, mock_detect_faces
    ):
        """Test auto rotation when face is detected at 0 degrees"""
        mock_detect_faces.side_effect = [True, False, False, False]  # Face found at 0°
        mock_image = Mock()
        mock_fromarray.return_value = mock_image

        auto_rotate(self.test_image_path)

        mock_image.save.assert_called_once_with(self.test_image_path)

    @patch("rotate.detect_faces")
    @patch("rotate.detect_objects_yolo")
    @patch("rotate.YOLO")
    @patch("rotate.Image.fromarray")
    def test_auto_rotate_object_detected_fallback(
        self, mock_fromarray, mock_yolo, mock_detect_objects, mock_detect_faces
    ):
        """Test auto rotation when no faces but objects detected"""
        mock_detect_faces.return_value = False  # No faces found
        mock_detect_objects.side_effect = [
            True,
            False,
            False,
            False,
        ]  # Object found at 0°
        mock_model = Mock()
        mock_yolo.return_value = mock_model
        mock_image = Mock()
        mock_fromarray.return_value = mock_image

        auto_rotate(self.test_image_path)

        mock_image.save.assert_called_once_with(self.test_image_path)

    @patch("rotate.detect_faces")
    @patch("rotate.detect_objects_yolo")
    @patch("rotate.YOLO")
    def test_auto_rotate_no_detection(
        self, mock_yolo, mock_detect_objects, mock_detect_faces
    ):
        """Test auto rotation when neither faces nor objects are detected"""
        mock_detect_faces.return_value = False
        mock_detect_objects.return_value = False
        mock_model = Mock()
        mock_yolo.return_value = mock_model

        # Should not raise exception, just log and continue
        auto_rotate(self.test_image_path)

    def test_auto_rotate_invalid_image_path(self):
        """Test auto rotation with invalid image path"""
        invalid_path = "/nonexistent/path/image.jpg"

        # Should not raise exception
        auto_rotate(invalid_path)


class TestProcessDirectory:
    """Test directory processing functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()

        # Create test images
        for i, ext in enumerate([".jpg", ".png", ".jpeg"]):
            img_path = os.path.join(self.temp_dir, f"test_image_{i}{ext}")
            test_img = TestImageCreation.create_test_image()
            test_img.save(img_path)

        # Create non-image file (should be ignored)
        txt_path = os.path.join(self.temp_dir, "readme.txt")
        with open(txt_path, "w") as f:
            f.write("test")

    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    @patch("rotate.Pool")
    @patch("rotate.tqdm")
    def test_process_directory_finds_images(self, mock_tqdm, mock_pool):
        """Test that process_directory finds the correct image files"""
        mock_pool_instance = Mock()
        mock_pool.return_value.__enter__.return_value = mock_pool_instance
        mock_pool_instance.imap_unordered.return_value = [None, None, None]
        mock_tqdm.return_value = [None, None, None]

        process_directory(self.temp_dir)

        # Should find 3 image files
        mock_pool_instance.imap_unordered.assert_called_once()
        args, kwargs = mock_pool_instance.imap_unordered.call_args
        assert len(args[1]) == 3, "Should find 3 image files"

    def test_process_directory_empty_directory(self, capsys):
        """Test process_directory with empty directory"""
        empty_dir = os.path.join(self.temp_dir, "empty")
        os.makedirs(empty_dir)

        process_directory(empty_dir)

        captured = capsys.readouterr()
        assert "No images found" in captured.out

    def test_process_directory_nonexistent_directory(self, capsys):
        """Test process_directory with nonexistent directory"""
        nonexistent_dir = "/totally/nonexistent/directory"

        process_directory(nonexistent_dir)

        captured = capsys.readouterr()
        assert "No images found" in captured.out


class TestProcessSingleImage:
    """Test single image processing"""

    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_image_path = os.path.join(self.temp_dir, "test_image.jpg")

        test_img = TestImageCreation.create_test_image()
        test_img.save(self.test_image_path)

    def teardown_method(self):
        """Clean up test fixtures"""
        shutil.rmtree(self.temp_dir)

    @patch("rotate.auto_rotate")
    def test_process_single_image(self, mock_auto_rotate):
        """Test processing a single image"""
        process_single_image(self.test_image_path)

        mock_auto_rotate.assert_called_once_with(self.test_image_path)


class TestIntegration:
    """Integration tests"""

    def test_import_all_functions(self):
        """Test that all functions can be imported successfully"""
        from rotate import (
            auto_rotate,
            detect_faces,
            detect_objects_yolo,
            get_model_path,
            process_directory,
            process_single_image,
        )

        # All functions should be importable
        assert callable(detect_faces)
        assert callable(detect_objects_yolo)
        assert callable(auto_rotate)
        assert callable(get_model_path)
        assert callable(process_single_image)
        assert callable(process_directory)

    def test_model_path_returns_string(self):
        """Test that get_model_path returns a string"""
        result = get_model_path()
        assert isinstance(result, str), "Model path should be a string"
        assert len(result) > 0, "Model path should not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
