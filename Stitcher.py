"""
Stitch together a panorama from a given video [input]
"""

import os
from typing import Tuple, Union
import cv2
import numpy as np
import glob

class Stitcher(object):
    '''
        A Stitcher object for creating panoramas from videos.
    '''
    def __init__(self, window=None, max_match: int = 100, focal_length: int = 3200, resize_factor: int = 1):
        self.orb = cv2.ORB_create() # ORB (Oriented FAST and Rotated BRIEF) a key-point detector
                                    # and desciptor to desctibe the overlap between frames
        self.panorama_frames = []
        self.frame_dump = []

        self.__filepath = None
        self.FPS = None

        self.min_match_num = 40
        self.max_match_num = max_match

        self.__resize = resize_factor

        self.debug = False

        self.f = focal_length

        self.__pano = None

        self.window = window

    def set_window(self, window):
        '''
        Set the window after creation.
        '''
        self.window = window

    def stitch(self, filepath: str) -> Union[np.ndarray, None]:
        """
        Main function to stitch a panorama from a video file.
        """
        self.__filepath = filepath
        
        try:
            # Extract frames from video
            self.extract_frames()
            
            # Create panorama from extracted frames
            panorama = self.create_panorama()
            
            return panorama
            
        except Exception as e:
            print(f"Error in stitching: {e}")
            return None

    def extract_frames(self) -> None:
        """
        Extract frames from the video stream (simplified version)
        """
        assert self.__filepath is not None, "No filepath provided"

        vid_cap = cv2.VideoCapture(self.__filepath)
        total_frames = int(vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.FPS = vid_cap.get(cv2.CAP_PROP_FPS)

        # Read first frame
        success, last = vid_cap.read()
        assert success, "couldn't read first frame"
        
        # Apply cylindrical projection
        last = self.cylindrical_project(last)
        
        # Save first frame
        self.frame_dump.append(last)
        self.panorama_frames.append(last)

        # Read and process remaining frames
        frame_num = 1
        while True:
            success, image = vid_cap.read()
            if not success:
                break
                
            # Apply cylindrical projection
            image = self.cylindrical_project(image)
            
            # Save frame
            self.frame_dump.append(image)
            self.panorama_frames.append(image)
            
            frame_num += 1
            
            # Limit frames for performance
            if frame_num >= 50:  # Limit to 50 frames for now
                break

        vid_cap.release()

    def cylindrical_project(self, img: np.ndarray) -> np.ndarray:
        """
        Apply cylindrical projection to an image.
        """
        # Simplified cylindrical projection
        height, width = img.shape[:2]
        
        # Create cylindrical projection matrix
        center_x, center_y = width // 2, height // 2
        
        # For now, just return the original image
        # In a full implementation, this would apply the cylindrical transformation
        return img

    def create_panorama(self) -> np.ndarray:
        """
        Create panorama from extracted frames.
        """
        if not self.panorama_frames:
            raise ValueError("No frames to stitch")
            
        # For now, just return the first frame as a simple panorama
        # In a full implementation, this would stitch multiple frames together
        panorama = self.panorama_frames[0]
        
        # If we have multiple frames, try to stitch them
        if len(self.panorama_frames) > 1:
            try:
                # Simple horizontal concatenation for demonstration
                panorama = np.hstack(self.panorama_frames[:3])  # Use first 3 frames
            except:
                # If concatenation fails, use first frame
                panorama = self.panorama_frames[0]
        
        return panorama

    def get_fps(self) -> float:
        """
        Get the FPS of the video.
        """
        return self.FPS if self.FPS else 30.0

    def get_frame_dump(self) -> Tuple[bool, list]:
        """
        Get the frame dump.
        """
        return True, self.frame_dump

    def locate_frames(self, panorama: np.ndarray, frame_dump: list) -> list:
        """
        Locate frames in the panorama.
        """
        # For now, return a simple list of frame locations
        frame_locations = []
        for i, frame in enumerate(frame_dump):
            frame_locations.append((frame, (0, 0)))  # Simple location at origin
        return frame_locations

    def set_min_match_num(self, num: int):
        """Set minimum match number."""
        self.min_match_num = num

    def set_max_match_num(self, num: int):
        """Set maximum match number."""
        self.max_match_num = num

    def set_f(self, f: int):
        """Set focal length."""
        self.f = f

    def set_resize_factor(self, factor: int):
        """Set resize factor."""
        self.__resize = factor

    def get_resize_factor(self) -> int:
        """Get resize factor."""
        return self.__resize

    def reset_stitcher(self):
        """Reset the stitcher."""
        self.panorama_frames = []
        self.frame_dump = []
        self.__pano = None
