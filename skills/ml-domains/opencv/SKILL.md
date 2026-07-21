---
name: opencv
description: Traitement d'images avancé avec OpenCV — filtrage, morphologie, contours, calibrage caméra, stitching, détection de caractéristiques, optique, vidéo, et pipelines HPC. En français.

---

# OpenCV — Traitement d'Images Avancé

OpenCV (Open Source Computer Vision Library) : la bibliothèque de référence pour le traitement d'images et la vision temps réel. Couvre les fondamentaux jusqu'aux pipelines HPC (CUDA, OpenCL, NEON).

---

## 1. Installation et Configuration

```bash
# CPU
pip install opencv-python opencv-contrib-python

# Avec CUDA (compilation depuis source)
git clone https://github.com/opencv/opencv.git
git clone https://github.com/opencv/opencv_contrib.git
cd opencv && mkdir build && cd build

cmake -D CMAKE_BUILD_TYPE=RELEASE \
      -D CMAKE_INSTALL_PREFIX=/usr/local \
      -D WITH_CUDA=ON \
      -D WITH_CUDNN=ON \
      -D OPENCV_DNN_CUDA=ON \
      -D CUDA_ARCH_BIN=8.6 \  # RTX 3090
      -D WITH_CUBLAS=ON \
      -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
      -D BUILD_opencv_python3=ON ..

make -j$(nproc)
sudo make install
```

---

## 2. Opérations Fondamentales

### Chargement, Affichage, Sauvegarde

```python
import cv2
import numpy as np

# Chargement
img = cv2.imread("photo.jpg")                     # BGR par défaut
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)    # Conversion RGB
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # Niveaux de gris

# Dimensions
h, w, c = img.shape                                # (hauteur, largeur, canaux)

# Redimensionnement
resized = cv2.resize(img, (640, 480))              # Taille exacte
scaled = cv2.resize(img, None, fx=0.5, fy=0.5)    # Facteur d'échelle

# Rogner
cropped = img[100:400, 200:500]                    # [y1:y2, x1:x2]

# Rotation
M = cv2.getRotationMatrix2D((w//2, h//2), 45, 1.0)
rotated = cv2.warpAffine(img, M, (w, h))

# ROIs
roi = img[y:y+h, x:x+w]
cv2.imwrite("roi.jpg", roi)
```

### Espaces Colorimétriques

```python
# Conversions
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)
xyz = cv2.cvtColor(img, cv2.COLOR_BGR2XYZ)

# Seuillage couleur (HSV idéal)
lower_red = np.array([0, 50, 50])
upper_red = np.array([10, 255, 255])
mask = cv2.inRange(hsv, lower_red, upper_red)
result = cv2.bitwise_and(img, img, mask=mask)
```

---

## 3. Filtrage et Traitement Spatial

### Filtres Linéaires

```python
# Moyenneur
blur = cv2.blur(img, (5, 5))

# Gaussien
gauss = cv2.GaussianBlur(img, (5, 5), 0)

# Box filter
box = cv2.boxFilter(img, -1, (5, 5))

# Filtre personnalisé (convolution)
kernel = np.array([[-1, -1, -1],
                   [-1,  9, -1],
                   [-1, -1, -1]])  # Sharpen
sharpened = cv2.filter2D(img, -1, kernel)
```

### Filtres Non-Linéaires

```python
# Médian (anti-bruit sel/poivre)
median = cv2.medianBlur(img, 5)

# Bilateral (maintient les bords)
bilateral = cv2.bilateralFilter(img, 9, 75, 75)
```

### Détection de Contours

```python
# Canny (paramètres : seuil bas, seuil haut)
edges = cv2.Canny(img, 50, 150)
edges = cv2.Canny(img, 50, 150, L2gradient=True)  # Norme L2

# Détection de bords par gradient
sobelx = cv2.Sobel(img, cv2.CV_64F, 1, 0, ksize=3)  # Gradient X
sobely = cv2.Sobel(img, cv2.CV_64F, 0, 1, ksize=3)  # Gradient Y
laplacian = cv2.Laplacian(img, cv2.CV_64F)           # Laplacien

# Magnitude du gradient
mag = np.sqrt(sobelx**2 + sobely**2)
```

---

## 4. Morphologie Mathématique

```python
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
# Ou
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
# Ou
kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))

# Opérations de base
eroded = cv2.erode(img, kernel, iterations=1)         # Érosion
dilated = cv2.dilate(img, kernel, iterations=1)       # Dilatation

# Composées
opening = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)      # Ouverture (érosion → dilatation)
closing = cv2.morphologyEx(img, cv2.MORPH_CLOSE, kernel)     # Fermeture (dilatation → érosion)
gradient = cv2.morphologyEx(img, cv2.MORPH_GRADIENT, kernel) # Gradient morphologique
tophat = cv2.morphologyEx(img, cv2.MORPH_TOPHAT, kernel)     # Top-hat
blackhat = cv2.morphologyEx(img, cv2.MORPH_BLACKHAT, kernel) # Black-hat
```

---

## 5. Seuillage et Binarisation

```python
# Global
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
_, binary_inv = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)
_, trunc = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)
_, tozero = cv2.threshold(gray, 127, 255, cv2.THRESH_TOZERO)

# Otsu (automatique)
_, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

# Triangle
_, triangle = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_TRIANGLE)

# Adaptatif
adaptive_mean = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                      cv2.THRESH_BINARY, 11, 2)
adaptive_gauss = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
```

---

## 6. Contours et Analyse de Formes

```python
# Trouver les contours
# RETR_EXTERNAL, RETR_LIST, RETR_TREE, RETR_CCOMP
# CHAIN_APPROX_NONE, CHAIN_APPROX_SIMPLE, CHAIN_APPROX_TC89_L1
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Trier par aire
contours = sorted(contours, key=cv2.contourArea, reverse=True)

# Dessiner
cv2.drawContours(img, contours, -1, (0, 255, 0), 2)        # Tous
cv2.drawContours(img, [contours[0]], -1, (0, 0, 255), 3)   # Premier

# Analyses
for c in contours:
    area = cv2.contourArea(c)                          # Aire
    perimeter = cv2.arcLength(c, True)                 # Périmètre
    approx = cv2.approxPolyDP(c, 0.02 * perimeter, True)  # Approximation polygonale
    hull = cv2.convexHull(c)                           # Enveloppe convexe
    k = cv2.isContourConvex(c)                         # Test convexité

    # Rectangle englobant
    x, y, w, h = cv2.boundingRect(c)
    cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

    # Rectangle orienté (minAreaRect)
    rect = cv2.minAreaRect(c)
    box = cv2.boxPoints(rect)
    box = np.int0(box)
    cv2.drawContours(img, [box], 0, (0, 255, 0), 2)

    # Cercle minimum
    (x, y), radius = cv2.minEnclosingCircle(c)
    cv2.circle(img, (int(x), int(y)), int(radius), (0, 255, 255), 2)

    # Ellipse
    ellipse = cv2.fitEllipse(c)
    cv2.ellipse(img, ellipse, (255, 0, 255), 2)

    # Moments
    moments = cv2.moments(c)
    cx = int(moments['m10'] / (moments['m00'] + 1e-5))
    cy = int(moments['m01'] / (moments['m00'] + 1e-5))
```

---

## 7. Détection de Caractéristiques (Features)

### Détecteurs Classiques

```python
# Harris Corner
gray_f = np.float32(gray)
corners = cv2.cornerHarris(gray_f, 2, 3, 0.04)
img[corners > 0.01 * corners.max()] = [0, 0, 255]

# Shi-Tomasi
corners = cv2.goodFeaturesToTrack(gray, maxCorners=100, qualityLevel=0.01, minDistance=10)

# SIFT (brevet expiré — libre)
sift = cv2.SIFT_create()
kp, desc = sift.detectAndCompute(gray, None)
img_sift = cv2.drawKeypoints(img, kp, None, flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

# SURF (breveté — ne pas utiliser en production sans licence)
# surf = cv2.xfeatures2d.SURF_create(400)

# ORB (libre, rapide, binaire)
orb = cv2.ORB_create(nfeatures=500)
kp, desc = orb.detectAndCompute(gray, None)

# BRISK
brisk = cv2.BRISK_create()
kp, desc = brisk.detectAndCompute(gray, None)

# AKAZE
akaze = cv2.AKAZE_create()
kp, desc = akaze.detectAndCompute(gray, None)
```

### Appariement (Matching)

```python
# Brute-Force (L2 pour SIFT/SURF)
bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
matches = bf.match(desc1, desc2)
matches = sorted(matches, key=lambda x: x.distance)

# Brute-Force (Hamming pour ORB)
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(desc1, desc2)

# FLANN (approximatif, rapide)
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
search_params = dict(checks=50)
flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(desc1, desc2, k=2)

# Ratio test de Lowe
good_matches = []
for m, n in matches:
    if m.distance < 0.75 * n.distance:
        good_matches.append(m)

# Homographie
if len(good_matches) >= 4:
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    h, w = img1.shape[:2]
    warped = cv2.warpPerspective(img1, H, (w, h))
```

---

## 8. Calibrage de Caméra

```python
# Calibrage avec échiquier
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
objp = np.zeros((6*9, 3), np.float32)
objp[:, :2] = np.mgrid[0:9, 0:6].T.reshape(-1, 2)

objpoints = []  # Points 3D monde
imgpoints = []  # Points 2D image

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, (9, 6), None)
    if ret:
        objpoints.append(objp)
        corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)
        imgpoints.append(corners2)

# Obtenir les paramètres
ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
    objpoints, imgpoints, gray.shape[::-1], None, None
)

# Matrice caméra (fx, fy, cx, cy)
# [[fx,  0, cx],
#  [ 0, fy, cy],
#  [ 0,  0,  1]]

# Corriger la distorsion
undistorted = cv2.undistort(img, mtx, dist, None, newcameramtx)

# Récupérer la carte de correction (plus rapide pour la vidéo)
mapx, mapy = cv2.initUndistortRectifyMap(mtx, dist, None, newcameramtx, (w, h), 5)
dst = cv2.remap(img, mapx, mapy, cv2.INTER_LINEAR)
```

---

## 9. Stitching (Panoramas)

```python
# Approche manuelle
stitcher = cv2.Stitcher.create(cv2.Stitcher_PANORAMA)
status, pano = stitcher.stitch(images)

if status == cv2.Stitcher_OK:
    cv2.imwrite("panorama.jpg", pano)
elif status == cv2.Stitcher_ERR_NEED_MORE_IMGS:
    print("Pas assez d'images")
elif status == cv2.Stitcher_ERR_HOMOGRAPHY_EST_FAIL:
    print("Échec estimation homographie")

# Approche manuelle détaillée
# 1. Features (SIFT/ORB)
# 2. Matching
# 3. Homographie (RANSAC)
# 4. Warping + blending
```

---

## 10. Traitement Vidéo

```python
# Lecture
cap = cv2.VideoCapture("video.mp4")
# cap = cv2.VideoCapture(0)  # Webcam

fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# Écriture
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Codec
out = cv2.VideoWriter("output.mp4", fourcc, fps, (width, height))

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    # Traitement...
    processed = cv2.Canny(frame, 100, 200)
    processed_bgr = cv2.cvtColor(processed, cv2.COLOR_GRAY2BGR)
    out.write(processed_bgr)

cap.release()
out.release()
```

### Background Subtraction

```python
# MOG2
backSub = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=True)

# KNN
backSub = cv2.createBackgroundSubtractorKNN(history=500, dist2Threshold=400.0, detectShadows=True)

# GSOC (BGSLib)
# backSub = cv2.bgsegm.createBackgroundSubtractorGSOC()

while cap.isOpened():
    ret, frame = cap.read()
    fgMask = backSub.apply(frame)
    # fgMask = 255 = mouvement, 0 = fond
```

---

## 11. DNN (Deep Neural Networks) dans OpenCV

```python
# Charger un modèle ONNX
net = cv2.dnn.readNetFromONNX("model.onnx")
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)     # CUDA
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)        # GPU

# Charger depuis Caffe/TensorFlow/Darknet
net = cv2.dnn.readNetFromCaffe("deploy.prototxt", "weights.caffemodel")
net = cv2.dnn.readNetFromTensorflow("frozen_graph.pb")
net = cv2.dnn.readNetFromDarknet("yolov3.cfg", "yolov3.weights")

# Blob
blob = cv2.dnn.blobFromImage(img, scalefactor=1/255.0, size=(416, 416),
                             mean=(0, 0, 0), swapRB=True, crop=False)
net.setInput(blob)

# Inférence
outputs = net.forward()

# Post-traitement YOLO
for detection in outputs:
    scores = detection[5:]
    class_id = np.argmax(scores)
    confidence = scores[class_id]
    if confidence > 0.5:
        center_x = int(detection[0] * width)
        center_y = int(detection[1] * height)
        w = int(detection[2] * width)
        h = int(detection[3] * height)
        x = int(center_x - w / 2)
        y = int(center_y - h / 2)
```

---

## 12. Optimisation CUDA et HPC

```python
# Vérifier OpenCV CUDA
print(cv2.cuda.getCudaEnabledDeviceCount())
cv2.cuda.setDevice(0)

# UMat (transparent compute)
img_umat = cv2.UMat(img)
gray_umat = cv2.cvtColor(img_umat, cv2.COLOR_BGR2GRAY)
edges_umat = cv2.Canny(gray_umat, 50, 150)
edges_cpu = edges_umat.get()

# GPU-accelerated
gpu_gray = cv2.cuda.cvtColor(img_umat, cv2.COLOR_BGR2GRAY)
gpu_edges = cv2.cuda.createCannyEdgeDetector(50, 150)
edges = gpu_edges.detect(gpu_gray)

# Super-resolution (dnn_superres)
sr = cv2.dnn_superres.DnnSuperResImpl_create()
sr.readModel("EDSR_x4.pb")
sr.setModel("edsr", 4)
upscaled = sr.upsample(img)
```

---

## 13. Traitement Temps Réel

```python
import time
from collections import deque

fps_buffer = deque(maxlen=30)
prev_time = time.time()

while True:
    ret, frame = cap.read()
    current_time = time.time()
    
    # Calcul FPS
    fps = 1.0 / (current_time - prev_time)
    fps_buffer.append(fps)
    fps_avg = np.mean(fps_buffer)
    prev_time = current_time
    
    # Afficher FPS
    cv2.putText(frame, f"FPS: {fps_avg:.1f}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
```

---

## Références
- OpenCV Docs : https://docs.opencv.org/4.x/
- OpenCV CUDA : https://docs.opencv.org/4.x/d1/d39/group__cuda.html
- LearnOpenCV : https://learnopencv.com/
- PyImageSearch : https://pyimagesearch.com/
- OpenCV Contrib : https://github.com/opencv/opencv_contrib