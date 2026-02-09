# 🧩 Guessing The Code: Bulls and Cows Pro

A sleek, responsive, and modern take on the classic logic game **Bulls and Cows**. Built with Python and Tkinter, this version features dynamic UI scaling, smooth animations, and a polished neon-aesthetic.


---

## 🎮 How to Play

The objective is to decode a hidden sequence of **4 icons** within **5 attempts**.

1.  **Select Icons**: Click the glowing icons at the bottom of the screen to fill your current row.
2.  **Analyze the Feedback**: Once 4 icons are placed, the game provides hints via colored dots:
    * 🟢 **Green Dot**: Correct icon in the correct position.
    * 🔴 **Red Dot**: Correct icon, but in the wrong position.
    * ⚪ **Empty Circle**: This icon is not part of the code.
3.  **Winning**: Match all 4 positions correctly to win!

> **Note**: The order of the feedback dots does **not** correspond to the order of the icons in your guess.

---

## 🛠️ Installation & Setup

### Prerequisites
* Python 3.x
* **Pillow (PIL)** library:
    ```bash
    pip install Pillow
    ```

### Assets
The game is designed to be "plug-and-play." 
* If you have `icon0.png` through `icon9.png`, `logo.png`, and `background.png` in the folder, the game will use them.
* If no images are found, the game **automatically generates** colorful placeholders so you can play immediately.

---

## ⌨️ Controls

| Action | Control |
| :--- | :--- |
| **Select Icon** | Left Mouse Click |
| **Undo Last Icon** | `UNDO` Button or `Backspace` |
| **Reset Game** | `RESTART` Button |

---



---

**Developed with ❤️ by Manaswi Goyal**
