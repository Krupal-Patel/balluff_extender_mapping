import streamlit as st
import numpy as np
import cv2

width = 400

st.set_page_config(layout="centered")
st.title('Edge detection with OpenCV')

image = st.file_uploader("Upload an image")

if image is not None:
    img = np.asarray(bytearray(image.read()), dtype=np.uint8)
    img = cv2.imdecode(img, cv2.IMREAD_COLOR)
    st.image(image, caption="Original image", width = width)

    st.subheader("Sobel Edge Detection using filter2d()")
    imgCopy1 = img.copy()
    imgCopy1 = cv2.cvtColor(imgCopy1, cv2.COLOR_BGR2GRAY)
    sobel_x = np.array([[-1, 0, 1],
                        [-2, 0, 2],
                        [-1, 0, 1]], dtype=np.float32)
    imgCopy1 = cv2.filter2D(imgCopy1, -1, sobel_x)

    imgCopy2 = img.copy()
    imgCopy2 = cv2.cvtColor(imgCopy2, cv2.COLOR_BGR2GRAY)
    sobel_y = np.array([[-1, -2, -1],
                        [0, 0, 0],
                        [1, 2, 1]], dtype=np.float32)
    imgCopy2 = cv2.filter2D(imgCopy2, -1, sobel_y)
    img1_col1, img1_col2, img1_col3 = st.columns(3)
    with img1_col1:
        st.image(img, caption="Original image", channels = "BGR")
    with img1_col2:
        st.image(imgCopy1, caption="Vertical Edges", channels="GRAY")
    with img1_col3:
        st.image(imgCopy2, caption="Horizontal Edges", channels="GRAY")


    st.subheader("Sobel Edge Detection using Sobel()")
    imgCopy3 = img.copy()
    imgCopy3 = cv2.cvtColor(imgCopy3, cv2.COLOR_BGR2GRAY)
    dx = st.slider(label="Select dx", min_value=1, max_value=10, value=1, step=1)
    ksize_x = max(3, 2 * dx + 1)
    imgCopy3 = cv2.Sobel(imgCopy3, -1, dx=dx, dy = 0, ksize = ksize_x)

    imgCopy4 = img.copy()
    imgCopy4 = cv2.cvtColor(imgCopy4, cv2.COLOR_BGR2GRAY)
    dy = st.slider(label="Select dy", min_value=1, max_value=10, value=1, step=1)
    ksize_y = max(3, 2 * dy + 1)
    imgCopy4 = cv2.Sobel(imgCopy4, -1, dx=0, dy = dy, ksize = ksize_y)

    # Combine the edges (optional: magnitude of gradients)
    edges = cv2.magnitude(imgCopy3.astype(np.float32), imgCopy4.astype(np.float32))
    # Normalize the combined edges for display
    edges = cv2.normalize(edges, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)


    img2_col1, img2_col2, img2_col3 = st.columns(3)

    with img2_col1:
        st.image(imgCopy3, caption="Vertical Edges", channels="GRAY")
    with img2_col2:
        st.image(imgCopy4, caption="Horizontal Edges", channels="GRAY")
    with img2_col3:
        st.image(edges, caption="Horizontal + Vertical", channels="GRAY")


    st.subheader("Canny Edge Detection without Blurring")
    imgCopy5 = img.copy()
    threshold_1 = st.slider(label="Lower Threshold", min_value=1, max_value=500, value=100, step=1)
    threshold_2 = st.slider(label="Upper Threshold", min_value=threshold_1, max_value=500, value=200, step=1)
    imgCopy5 = cv2.cvtColor(imgCopy5, cv2.COLOR_BGR2GRAY)
    imgCopy5 = cv2.Canny(imgCopy5, threshold1 = threshold_1 , threshold2 = threshold_2)

    img3_col1, img3_col2 = st.columns(2)

    with img3_col1:
        st.image(img, caption="Original Image", channels="BGR")
    with img3_col2:
        st.image(imgCopy5, caption="Canny Threshold", channels="GRAY")

    st.subheader("Canny Edge Detection with Blurring")
    imgCopy6 = img.copy()

    col1, col2, col3 = st.columns(3)
    with col1:
        kernel_size_3 = st.slider(label="Gaussian Blur Kernal Size", min_value=3, max_value=21, value=3, step=2)
    with col2:
        sigmaX = st.slider(label="sigmaX", min_value=0, max_value=10, value=0, step=1)
    with col3:
        sigmaY = st.slider(label="sigmaY", min_value=0, max_value=10, value=0, step=1)

    imgCopy6 = cv2.cvtColor(imgCopy6, cv2.COLOR_BGR2GRAY)
    imgCopy7 = cv2.GaussianBlur(imgCopy6, (kernel_size_3, kernel_size_3), sigmaX = sigmaX, sigmaY = sigmaY)

    threshold_3 = st.slider(label="Lower Thresh", min_value=1, max_value=500, value=100, step=1)
    threshold_4 = st.slider(label="Upper Thresh", min_value=threshold_3, max_value=500, value=threshold_3+20, step=1)

    imgCopy8 = cv2.Canny(imgCopy7, threshold1=threshold_3, threshold2=threshold_4)

    img4_col1, img4_col2, img4_col3 = st.columns(3)

    with img4_col1:
        st.image(imgCopy6, caption="Grayscale", channels="GRAY")
    with img4_col2:
        st.image(imgCopy7, caption="Blurred", channels="GRAY")
    with img4_col3:
        st.image(imgCopy8, caption="Blurred", channels="GRAY")
