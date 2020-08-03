from flask import Flask, request
import cv2
import numpy as np
import datetime

app = Flask(__name__)

def chromakey(img, background):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    patch = hsv[0:20, 0:20, :]
    minH = np.min(patch[:, :, 0]) * 0.9
    maxH = np.max(patch[:, :, 0]) * 1.1
    minS = np.min(patch[:, :, 1]) * 0.9
    maxS = np.max(patch[:, :, 1]) * 1.1
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    dest = img.copy()

    for r in range(img.shape[0]):
        for c in range(img.shape[1]):
            if h[r, c] >= minH and h[r, c] <= maxH and s[r, c] >= minS and s[r, c] <= maxS:
                dest[r, c, :] = background[r, c, :]
            else:
                dest[r, c, :] = img[r, c, :]
    return dest


@app.route('/')
def index():
    html = """
        <form action=/upload method=post enctype="multipart/form-data">
            <input type=file name=file1> <accept="images/*" capture="camera">
            <input type=submit value="전송">
        </form>

        <select name=backimg>
          <option value=ocean.jpg>Ocean</option>
          <option value=city.jpg>City</option>
          <option value=forest.jpg>Forest</option>
        </select>

        <img src=/static/ocean.jpg width=100>
        <img src=/static/city.jpg width=100>
        <img src=/static/forest.jpg width=100>

    """
    return html


@app.route('/upload', methods=["post"])
def upload():
    f = request.files['file1']
    filename = "./static/" + f.filename
    f.save(filename)

    backimg = request.form.get("backimg")

    img = cv2.imread(filename)
    img = cv2.resize(img, dsize=(320, 240))

    background = cv2.imread("./static/" + backimg)
    background = cv2.resize(background, dsize=(320, 240))
    img = chromakey(img, background)
    cv2.imwrite(filename, img)

    return "<img src=/static/" + f.filename + "?" + datetime.datetime.now().strftime('%H%M%S') + ">"

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)