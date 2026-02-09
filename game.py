import tkinter as tk
from tkinter import messagebox
import random
import time
import os
from PIL import Image, ImageTk, ImageFilter

# --- CONFIG ---
TOTAL_POOL = 10
ACTIVE_ICONS = 4
BASE_SLOT_SIZE = 60
BASE_GAP = 20
ROWS = 5
BACKGROUND_PATH = "background.png" 
LOGO_PATH = "logo.png" 
GLOW_RADIUS = 8 

class BullsAndCowsPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Guessing The Code")
        self.root.geometry("950x750")
        
        # 1. Initialize variables HERE first
        self.secret_code = []
        self.history = []  
        self.current_guess = []
        self.selected_indices = [] # <--- Add this line here
        self.row_count = 0
        self.is_animating = False 
        
        self.all_icons_pil = []
        self.session_icons = []
        self.glow_icons = [] 
        self.logo_photo = None 
        
        self.canvas = tk.Canvas(root, highlightthickness=0, bg="#2c3e50")
        self.canvas.pack(fill="both", expand=True)
        
        self.load_resources()
        
        # 2. Setup the game state BEFORE binding events
        self.init_game() 
        
        # 3. Now bind the resize event
        self.root.bind("<Configure>", self.on_window_resize)
        self.root.bind("<BackSpace>", lambda e: self.undo_guess())

    def on_window_resize(self, event):
        # We check if the event is for the root window specifically
        if event.widget == self.root and not self.is_animating:
            self.draw_ui()

    def get_scales(self):
        w = self.root.winfo_width()
        h = self.root.winfo_height()
        # Ensure we don't divide by zero if window is minimized
        scale = min(max(w, 100) / 950, max(h, 100) / 750)
        slot = int(BASE_SLOT_SIZE * scale)
        gap = int(BASE_GAP * scale)
        return w, h, slot, gap, scale

    def create_glow_version(self, pil_img, slot_size, scale):
        # Scale the icon inside the glow version
        img_sz = max(int(slot_size - (10 * scale)), 5)
        resized = pil_img.resize((img_sz, img_sz), Image.Resampling.LANCZOS)
        curr_glow = int(GLOW_RADIUS * scale)
        new_size = (resized.width + 2 * curr_glow, resized.height + 2 * curr_glow)
        glow_canvas = Image.new("RGBA", new_size, (225, 210, 0, 0))
        glow_canvas.paste(resized, (curr_glow, curr_glow))
        glow_canvas = glow_canvas.filter(ImageFilter.GaussianBlur(radius=curr_glow))
        glow_canvas.paste(resized, (curr_glow, curr_glow), resized)
        return ImageTk.PhotoImage(glow_canvas)

    def load_resources(self):
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6", 
                  "#1abc9c", "#e67e22", "#95a5a6", "#34495e", "#d35400"]
        for i in range(TOTAL_POOL):
            path = f"icon{i}.png"
            img = Image.open(path).convert("RGBA") if os.path.exists(path) else \
                  Image.new('RGBA', (100, 100), color=colors[i % len(colors)])
            self.all_icons_pil.append(img)

    def init_game(self):
        pool_indices = list(range(TOTAL_POOL))
        random.shuffle(pool_indices)
        self.selected_indices = pool_indices[:ACTIVE_ICONS]
        
        # --- NEW CODE GENERATION LOGIC ---
        # 50% chance to have one repetition
        if random.random() < 0.5:
            # Pick 3 unique icons from our active pool
            # (One will be used twice, the other two once = 4 total slots)
            chosen_icons = random.sample(range(ACTIVE_ICONS), 3)
            # Repeat the first icon in the chosen list
            self.secret_code = [chosen_icons[0], chosen_icons[0], chosen_icons[1], chosen_icons[2]]
            # Shuffle so the pair isn't always at the start
            random.shuffle(self.secret_code)
        else:
            # Standard unique code (1234 style)
            self.secret_code = random.sample(range(ACTIVE_ICONS), 4)
        # ---------------------------------

        self.history, self.current_guess, self.row_count, self.is_animating = [], [], 0, False
        self.draw_ui()

    def draw_ui(self):
        # Safety check: if game isn't initialized yet, don't draw
        if not self.selected_indices:
            return

        w, h, slot, gap, scale = self.get_scales()
        if w < 100: return
        self.canvas.delete("all")

        self.session_icons = []
        self.glow_icons = []
        icon_sz = max(int(slot - (10 * scale)), 5)
        for idx in self.selected_indices:
            pil_img = self.all_icons_pil[idx]
            self.session_icons.append(ImageTk.PhotoImage(pil_img.resize((icon_sz, icon_sz), Image.Resampling.LANCZOS)))
            self.glow_icons.append(self.create_glow_version(pil_img, slot, scale))

        if os.path.exists(BACKGROUND_PATH):
            bg_img = Image.open(BACKGROUND_PATH).resize((w, h), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_img)
            self.canvas.create_image(0, 0, anchor="nw", image=self.bg_photo)

        if os.path.exists(LOGO_PATH):
            l_sz = int(400 * scale)
            img = Image.open(LOGO_PATH).resize((l_sz, l_sz), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(img)
            self.canvas.create_image(w, 0, anchor="ne", image=self.logo_photo)

        # --- Instructions (Dynamic Font Scaling) ---
        instr = ("HOW TO PLAY:\n• Click icons at bottom to guess the correct code.\n"
                 "• Green Dot = Correct icon & spot.\n• Red Dot = Correct icon, wrong spot.\n"
                 "• NOTE: Dot order ≠ Icon order.")
        
        # Calculated Font Size: Base 16 at design resolution
        f_sz = max(int(16 * scale), 8) 
        
        # Scaled shadow offset
        off = max(int(1 * scale), 1)
        self.canvas.create_text(20 + off, 20 + off, text=instr, fill="black", font=("Arial", f_sz, "bold"), anchor="nw")
        self.canvas.create_text(20, 20, text=instr, fill="#7AF0FF", font=("Arial", f_sz, "bold"), anchor="nw")

        grid_w = (4 * slot) + (3 * gap)
        self.start_x = (w - grid_w) // 2
        self.start_y = 130 * scale # Lowered slightly for more room

        for r in range(ROWS): 
            ry = self.start_y + (r * (slot + gap))
            if r == self.row_count:
                pad = 10 * scale
                self.canvas.create_rectangle(self.start_x-pad, ry-pad, self.start_x+grid_w+pad, ry+slot+pad, outline="#6FFFE9", width=max(int(2*scale),1), dash=(6,4))

            for c in range(4):
                x = self.start_x + (c * (slot + gap))
                fill = "#aabac9" if r < len(self.history) else ""
                self.canvas.create_rectangle(x, ry, x+slot, ry+slot, fill=fill, outline="white", width=max(int(2*scale),1), stipple="gray50" if fill else "")

            if r < len(self.history):
                h_item = self.history[r]
                for c, idx in enumerate(h_item['guess']):
                    # NW Anchor with scaled offset
                    self.canvas.create_image(self.start_x+(c*(slot+gap))+(5*scale), ry+(5*scale), image=self.session_icons[idx], anchor="nw")
                self.draw_static_dots(r, h_item['bulls'], h_item['cows'], slot, gap, scale)
            else:
                self.draw_static_dots(r, 0, 0, slot, gap, scale)

        for c, idx in enumerate(self.current_guess):
            self.canvas.create_image(self.start_x+(c*(slot+gap))+(5*scale), self.start_y+(self.row_count*(slot+gap))+(5*scale), image=self.session_icons[idx], anchor="nw")

        btn_y = h - (100 * scale)
        gr = int(GLOW_RADIUS * scale)
        for i in range(ACTIVE_ICONS):
            bx = self.start_x + (i * (slot + gap))
            bid = self.canvas.create_image(bx-gr, btn_y-gr, image=self.glow_icons[i], anchor="nw")
            self.canvas.tag_bind(bid, "<Button-1>", lambda e, idx=i: self.handle_press(idx))

        ctrl_x = self.start_x + grid_w + (140 * scale) 
        self.create_btn(ctrl_x, self.start_y + (30*scale), "RESTART", "#FF5C5C", self.init_game, scale)
        self.create_btn(ctrl_x, self.start_y + (80*scale), "UNDO", "#FFB020", self.undo_guess, scale)

    def create_btn(self, x, y, text, color, cmd, scale):
        bw, bh = 55*scale, 18*scale
        r = self.canvas.create_rectangle(x-bw, y-bh, x+bw, y+bh, fill=color, outline="white", width=max(int(2*scale),1))
        t = self.canvas.create_text(x, y, text=text, fill="#FFFFFF", font=("Arial", int(12*scale), "bold"))
        for item in (r, t): self.canvas.tag_bind(item, "<Button-1>", lambda e: cmd())

    def handle_press(self, index):
        # Remove "index in self.current_guess" to allow picking the same icon twice
        if self.is_animating or len(self.current_guess) >= 4: return
        w, h, slot, gap, scale = self.get_scales()
        tx, ty = self.start_x+(len(self.current_guess)*(slot+gap))+(5*scale), self.start_y+(self.row_count*(slot+gap))+(5*scale)
        sx, sy = self.start_x+(index*(slot+gap))+(5*scale), h-(100*scale)+(5*scale)
        self.animate_move(index, sx, sy, tx, ty)

    def animate_move(self, index, x1, y1, x2, y2):
        self.is_animating = True
        flyer = self.canvas.create_image(x1, y1, image=self.session_icons[index], anchor="nw")
        for i in range(7):
            self.canvas.coords(flyer, x1+(x2-x1)*(i/6), y1+(y2-y1)*(i/6))
            self.canvas.update(); time.sleep(0.01)
        self.canvas.delete(flyer)
        self.current_guess.append(index)
        self.is_animating = False
        self.draw_ui()
        if len(self.current_guess) == 4: self.root.after(100, self.start_result_sequence)

    def start_result_sequence(self):
        self.is_animating = True
        bulls, cows = 0, 0
        s_copy, g_copy = list(self.secret_code), list(self.current_guess)
        for i in range(4):
            if g_copy[i] == s_copy[i]: bulls += 1; s_copy[i] = g_copy[i] = None
        for i in range(4):
            if g_copy[i] is not None and g_copy[i] in s_copy: cows += 1; s_copy[s_copy.index(g_copy[i])] = None
        self.stagger_dots(self.row_count, bulls, cows, 0)

    def stagger_dots(self, row, bulls, cows, dot_idx):
        w, h, slot, gap, scale = self.get_scales()
        if dot_idx < 4:
            fx, fy = self.start_x + (4*(slot+gap)) + (10*scale), self.start_y + (row*(slot+gap)) + (12*scale)
            dx, dy = (dot_idx%2)*(25*scale), (dot_idx//2)*(25*scale)
            color = "#00FF00" if dot_idx < bulls else "#FF0000" if dot_idx < (bulls+cows) else None
            if color:
                dsz = 18*scale
                self.canvas.create_oval(fx+dx, fy+dy, fx+dx+dsz, fy+dy+dsz, fill=color, outline="white", width=1)
                self.canvas.create_oval(fx+dx+(4*scale), fy+dy+(3*scale), fx+dx+(9*scale), fy+dy+(8*scale), fill="white", outline="")
            self.canvas.update()
            self.root.after(100, lambda: self.stagger_dots(row, bulls, cows, dot_idx + 1))
        else:
            self.history.append({'guess': list(self.current_guess), 'bulls': bulls, 'cows': cows})
            self.row_count += 1
            self.current_guess, self.is_animating = [], False
            self.draw_ui(); self.check_game_end(bulls)

    def draw_static_dots(self, row, bulls, cows, slot, gap, scale):
        fx, fy = self.start_x + (4*(slot+gap)) + (10*scale), self.start_y + (row*(slot+gap)) + (12*scale)
        dsz = 18*scale
        for i in range(4):
            dx, dy = (i%2)*(25*scale), (i//2)*(25*scale)
            self.canvas.create_oval(fx+dx, fy+dy, fx+dx+dsz, fy+dy+dsz, outline="#b0d8ff", width=1)
            if i < (bulls + cows):
                color = "#00FF00" if i < bulls else "#FF0000"
                self.canvas.create_oval(fx+dx, fy+dy, fx+dx+dsz, fy+dy+dsz, fill=color, outline="white")
                self.canvas.create_oval(fx+dx+(4*scale), fy+dy+(3*scale), fx+dx+(9*scale), fy+dy+(8*scale), fill="white", outline="")

    def check_game_end(self, bulls):
        if bulls == 4:
            messagebox.showinfo("Win", "Congrats!! You Decoded the Code."); self.init_game()
        elif self.row_count >= ROWS:
            ans = ", ".join([str(x + 1) for x in self.secret_code])
            messagebox.showinfo("Game Over", f"The code was: {ans}"); self.init_game()

    def undo_guess(self):
        if self.current_guess and not self.is_animating: self.current_guess.pop(); self.draw_ui()

if __name__ == "__main__":
    root = tk.Tk(); game = BullsAndCowsPro(root); root.mainloop()