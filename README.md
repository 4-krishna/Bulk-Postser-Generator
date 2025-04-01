# Bulk Poster Generator

A utility for generating personalized posters from CSV data and template images.

## Overview

This tool automates the creation of customized posters by combining:
- Data from a CSV file (names, IDs, categories)
- A template poster image
- Individual photos

The generator supports rounded photo corners, custom fonts, and placeholder images for missing photos.

## Features

- Batch processing of multiple entries from CSV
- Automatic photo matching using various naming patterns
- Customizable text positioning and styling
- Rounded corners for photos
- Placeholder images for missing photos
- Summary report of processed items
- Helper script for manually mapping missing photos

## Requirements

- Python 3.6+
- Required packages:
  - PIL (Pillow)
  - OpenCV (cv2)
  - NumPy

## Installation

1. Clone or download this repository
2. Install required packages: