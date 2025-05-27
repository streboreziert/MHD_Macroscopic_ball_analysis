# MHD_Macroscopic_ball_analysis

**Macroscopic Tracking of Magnetic Particle Dynamics**  
Developed for analyzing rotational dynamics of magnetized spheres in viscous fluid under rotating magnetic fields. 

---

##  Overview

This repository provides image processing and vector analysis tools for experiments involving a rotating magnetic sphere inside a glycerin container. The goal is to extract the 3D direction of the magnetic moment over time, and compare it with the applied magnetic field.

It consists of:
- Frame-by-frame video/image processing to detect the sphere and its dividing line
- Estimation of the magnetic moment vector direction
- Comparison with time-synchronized coil field vectors

---

##  File Descriptions

### `process_ball_images.py`

**Purpose**: Extracts the orientation of the magnetic moment in each frame from video/image data.

**Input**:
- A folder containing grayscale images of the sphere, named sequentially like:  
  `frame_0000.png`, `frame_0001.png`, ..., `frame_NNNN.png`

**What it does**:
1. Uses Hough Circle Transform to detect the spherical contour.
2. Identifies the dividing line between the black and white hemispheres.
3. Extracts a direction vector perpendicular to the dividing line — approximating the magnetic moment.
4. Stores time-stamped vectors in a CSV or TXT file.

**Output**:
- A CSV file with columns: `timestamp`, `x`, `y`, `z` (normalized magnetic moment direction vector)
- Optional debug visualization (e.g., overlays on frames)

---

### `align_coil_vector_with_ball.py`

**Purpose**: Aligns the extracted moment vector with the time-synchronized magnetic field applied by the Helmholtz coils.

**Input**:
- The CSV output from `process_ball_images.py`
- A second CSV file containing the coil magnetic field vectors for each frame (must be time-aligned)

**What it does**:
1. Reads both files and ensures synchronization.
2. Computes the angle between the magnetic moment vector and the applied field vector (lag angle α).
3. Optionally computes inclination (θ) and azimuth (ϕ).
4. Produces plots and data for dynamic analysis.

**Output**:
- Lag angle over time plot
- CSV with computed angles

---

##  Input File Format

### Frame Images
- Grayscale PNG or JPG
- Recommended size: ≥640×480
- Must show clear division between black/white hemispheres
- Naming convention: `frame_0000.png`, `frame_0001.png`, etc.

###  Magnetic Field File
- CSV format
- Columns: `timestamp`, `Bx`, `By`, `Bz`
- Units: typically in microteslas or milliteslas
- Must be **time-synchronized** with video

### Frame Timing
- Frame rate is assumed **constant** (default: 30 fps)
- Adjust `process_ball_images.py` to match your actual frame rate if different

---

##  Installation

Install dependencies:

```bash
pip install numpy opencv-python pandas matplotlib
