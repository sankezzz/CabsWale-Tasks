from insightface.app import FaceAnalysis
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import cv2

# Initialize the model
app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0)  # 0 = CPU

# Function to get face embedding
def get_embedding(img_path):
    img = cv2.imread(img_path)
    faces = app.get(img)
    if not faces:
        return None
    return faces[0].embedding

# Get embeddings
e1 = get_embedding("faces/face1.JPG")
e2 = get_embedding("faces/face2.JPG")
e3 = get_embedding("faces/face3.JPG")

# Check if any embedding is None
if any(e is None for e in [e1, e2, e3]):
    print("❌ Face not detected in one of the images.")
else:
    # Compute cosine similarities
    s12 = cosine_similarity([e1], [e2])[0][0]
    s13 = cosine_similarity([e1], [e3])[0][0]
    s23 = cosine_similarity([e2], [e3])[0][0]

    print(f"Similarity 1-2: {s12:.3f}")
    print(f"Similarity 1-3: {s13:.3f}")
    print(f"Similarity 2-3: {s23:.3f}")

    if min(s12, s13, s23) > 0.45:
        print("✅ Same person detected in all 3 images.")
    else:
        print("❌ Different people detected.")
