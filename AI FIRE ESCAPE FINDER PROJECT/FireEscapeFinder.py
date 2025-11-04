import tkinter as tk
from tkinter import messagebox
from collections import deque
import random
from queue import PriorityQueue # <-- Import PriorityQueue

# --- Constants ---
GRID_ROWS = 20
GRID_COLS = 20
CELL_SIZE = 30  # In pixels

# Cell types
CELL_EMPTY = 0
CELL_WALL = 1
CELL_FIRE = 2
CELL_START = 3
CELL_END = 4
CELL_PATH = 5
CELL_VISITED = 6 # New cell type for animation

# --- Theme and Colors ---
THEME = {
    "BG_PRIMARY": "#2B2B2B",      # Dark gray for main background
    "BG_SECONDARY": "#3C3C3C",    # Lighter gray for canvas/inputs
    "FG_PRIMARY": "#E0E0E0",      # Light gray for text
    "FG_INACTIVE": "#9E9E9E",    # Dimmer text
    "ACCENT": "#00BCD4",          # Bright Cyan
    "BTN_BG": "#4A4A4A",          # Standard button
    "BTN_FG": "#E0E0E0",
    "BTN_ACTIVE_BG": "#007ACC",   # Bright Blue for active tool
    "GREEN": "#4CAF50",
    "RED": "#F44336",
    "ORANGE": "#FF9800",
}

# Color mapping for cell types in Dark Mode
CELL_COLORS = {
    CELL_EMPTY: THEME["BG_SECONDARY"],
    CELL_WALL: "#616161",       # Mid-gray
    CELL_FIRE: THEME["ORANGE"],
    CELL_START: THEME["GREEN"],
    CELL_END: THEME["RED"],
    CELL_PATH: THEME["ACCENT"],  # Cyan
    CELL_VISITED: "#4A5A6A"     # Dark Slate Blue/Gray
}

# --- Main Application Class ---
class FireEscapeFinder(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title("Fire Escape Path Finder")
        self.master.resizable(False, False)
        self.master.configure(bg=THEME["BG_PRIMARY"]) # Set main window background

        # --- Instance Variables ---
        self.grid_data = [[CELL_EMPTY for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.start_pos = None
        self.end_pos = None
        self.current_tool = "start" # Replaces tool_var
        self.tool_buttons = {}      # To store tool buttons for styling
        
        # --- A* Algorithm Variables ---
        # We replace the BFS queue with a PriorityQueue
        self.open_set = PriorityQueue()
        self.parent = {}
        self.g_cost = {} # Cost from start to a node
        self.open_set_hash = set() # To check if a node is in the priority queue
        
        self.animation_running = False
        self.animation_speed = tk.IntVar(value=50) # Default step delay in ms

        # --- Create UI ---
        self.setup_ui()
        self.draw_grid()
        self.select_tool("start") # Set initial tool state

    def setup_ui(self):
        """Initializes the main UI layout with dark theme."""
        
        # --- Control Frame (Right Side) ---
        control_frame = tk.Frame(self.master, padx=15, pady=10, bg=THEME["BG_PRIMARY"])
        control_frame.pack(side=tk.RIGHT, fill=tk.Y)

        tk.Label(control_frame, text="Tools", font=("Arial", 14, "bold"), 
                 bg=THEME["BG_PRIMARY"], fg=THEME["FG_PRIMARY"]).pack(anchor="w")

        # --- Tool Buttons (Replaces RadioButtons) ---
        tool_frame = tk.Frame(control_frame, bg=THEME["BG_PRIMARY"])
        tool_frame.pack(fill="x", pady=5)
        
        # Define tools: (Display Text, tool_id)
        tools = [
            ("Start 🧑‍", "start"), ("Exit 🚪", "end"),
            ("Wall 🧱", "wall"), ("Fire 🔥", "fire"),
            ("Eraser 🧹", "empty")
        ]
        
        for i, (text, tool_id) in enumerate(tools):
            btn = tk.Button(tool_frame, text=text, 
                            command=lambda t=tool_id: self.select_tool(t),
                            bg=THEME["BTN_BG"], fg=THEME["BTN_FG"], 
                            activebackground=THEME["BTN_ACTIVE_BG"], 
                            activeforeground=THEME["FG_PRIMARY"],
                            relief="flat", width=12, font=("Arial", 10))
            btn.grid(row=i // 2, column=i % 2, padx=2, pady=3, sticky="ew")
            self.tool_buttons[tool_id] = btn

        # Label to show current tool
        self.selected_tool_label = tk.Label(control_frame, text="Selected: Start 🧑‍", 
                                            bg=THEME["BG_PRIMARY"], fg=THEME["ACCENT"], 
                                            font=("Arial", 10, "italic"))
        self.selected_tool_label.pack(anchor="w", pady=(5,0))


        tk.Frame(control_frame, height=2, bg=THEME["ACCENT"], relief="sunken").pack(fill="x", pady=15)

        # --- Action Buttons ---
        self.find_path_button = tk.Button(control_frame, text="Find Escape Path", 
                                          command=self.start_pathfinding_animation, 
                                          bg=THEME["GREEN"], fg="white", 
                                          font=("Arial", 10, "bold"), relief="flat", height=2)
        self.find_path_button.pack(fill="x", pady=5)
        
        # Button sub-frame
        action_frame = tk.Frame(control_frame, bg=THEME["BG_PRIMARY"])
        action_frame.pack(fill="x", pady=2)
        
        tk.Button(action_frame, text="Randomize Grid", command=self.randomize_grid,
                  bg=THEME["BTN_BG"], fg=THEME["BTN_FG"], relief="flat").pack(side=tk.LEFT, fill="x", expand=True, padx=(0,2))
        
        tk.Button(action_frame, text="Clear Path", command=self.clear_path,
                  bg=THEME["BTN_BG"], fg=THEME["BTN_FG"], relief="flat").pack(side=tk.LEFT, fill="x", expand=True, padx=(2,0))
        
        tk.Button(control_frame, text="Clear Full Grid", command=self.clear_grid,
                  bg=THEME["RED"], fg="white", relief="flat").pack(fill="x", pady=2)


        tk.Frame(control_frame, height=2, bg=THEME["ACCENT"], relief="sunken").pack(fill="x", pady=15)

        # --- Animation Speed Control ---
        tk.Label(control_frame, text="Animation Speed (ms):", font=("Arial", 10, "bold"),
                 bg=THEME["BG_PRIMARY"], fg=THEME["FG_PRIMARY"]).pack(anchor="w")
        
        speed_slider = tk.Scale(control_frame, from_=0, to=200, orient=tk.HORIZONTAL, 
                                variable=self.animation_speed, showvalue=1,
                                bg=THEME["BG_PRIMARY"], fg=THEME["FG_PRIMARY"],
                                troughcolor=THEME["BG_SECONDARY"], 
                                highlightthickness=0, bd=0, activebackground=THEME["BTN_BG"])
        speed_slider.set(50)
        speed_slider.pack(fill="x", anchor="w")

        # --- Canvas (Left Side) ---
        self.canvas = tk.Canvas(self.master,
                                width=GRID_COLS * CELL_SIZE,
                                height=GRID_ROWS * CELL_SIZE,
                                bg=THEME["BG_SECONDARY"],
                                borderwidth=0,
                                highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.handle_grid_click)
        self.canvas.bind("<B1-Motion>", self.handle_grid_click) # For dragging

    def select_tool(self, tool_name):
        """Sets the active tool and updates button styles."""
        self.current_tool = tool_name
        
        tool_text = "Unknown"
        
        # Reset all button styles
        for tool_id, button in self.tool_buttons.items():
            button.config(bg=THEME["BTN_BG"], fg=THEME["BTN_FG"])
            if tool_id == tool_name:
                tool_text = button.cget("text") # Get the button's text
        
        # Highlight the active button
        if tool_name in self.tool_buttons:
            self.tool_buttons[tool_name].config(bg=THEME["BTN_ACTIVE_BG"], fg=THEME["FG_PRIMARY"])
        
        # Update the label
        self.selected_tool_label.config(text=f"Selected: {tool_text}")

    def draw_grid(self):
        """Redraws the entire grid on the canvas based on grid_data."""
        self.canvas.delete("all")
        grid_outline_color = THEME["BG_PRIMARY"] # Grid lines
        
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x1 = col * CELL_SIZE
                y1 = row * CELL_SIZE
                x2 = x1 + CELL_SIZE
                y2 = y1 + CELL_SIZE

                cell_type = self.grid_data[row][col]
                color = CELL_COLORS.get(cell_type, THEME["BG_SECONDARY"]) 

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=grid_outline_color, width=1)

    def draw_cell(self, row, col, cell_type):
        """Draws or updates a single cell (more efficient for animation)."""
        x1 = col * CELL_SIZE
        y1 = row * CELL_SIZE
        x2 = x1 + CELL_SIZE
        y2 = y1 + CELL_SIZE
        
        color = CELL_COLORS.get(cell_type, THEME["BG_SECONDARY"])
        grid_outline_color = THEME["BG_PRIMARY"]
        
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline=grid_outline_color, width=1)

    def handle_grid_click(self, event):
        """Handles click-and-drag events on the canvas grid."""
        if self.animation_running:
            return # Don't allow edits while animating
            
        try:
            col = event.x // CELL_SIZE
            row = event.y // CELL_SIZE

            # Ensure click is within bounds
            if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
                self.set_cell(row, col)
        except Exception:
            pass # Ignore clicks outside the grid area

    def set_cell(self, row, col):
        """Sets the type of a single cell based on the selected tool."""
        # Clear any existing path, as it's now invalid
        self.clear_path(redraw=False)

        tool = self.current_tool # Use the instance variable
        current_cell_type = self.grid_data[row][col]

        # Prevent overwriting start/end with wall/fire
        if current_cell_type in (CELL_START, CELL_END) and tool in ("wall", "fire"):
            return

        new_type = CELL_EMPTY
        if tool == "start":
            # Remove old start if it exists
            if self.start_pos:
                r, c = self.start_pos
                self.grid_data[r][c] = CELL_EMPTY
                self.draw_cell(r, c, CELL_EMPTY)
            # Set new start
            self.start_pos = (row, col)
            new_type = CELL_START

        elif tool == "end":
            # Remove old end if it exists
            if self.end_pos:
                r, c = self.end_pos
                self.grid_data[r][c] = CELL_EMPTY
                self.draw_cell(r, c, CELL_EMPTY)
            # Set new end
            self.end_pos = (row, col)
            new_type = CELL_END

        elif tool == "wall":
            new_type = CELL_WALL
        elif tool == "fire":
            new_type = CELL_FIRE
        elif tool == "empty":
            # If we are erasing the start or end, update their positions
            if (row, col) == self.start_pos:
                self.start_pos = None
            if (row, col) == self.end_pos:
                self.end_pos = None
            new_type = CELL_EMPTY

        self.grid_data[row][col] = new_type
        self.draw_cell(row, col, new_type) # Update just one cell

    def clear_grid(self):
        """Resets the entire grid to empty."""
        if self.animation_running:
            return
            
        self.grid_data = [[CELL_EMPTY for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.start_pos = None
        self.end_pos = None
        self.draw_grid()

    def clear_path(self, redraw=True):
        """Removes only the path (CELL_PATH and CELL_VISITED) from the grid."""
        if self.animation_running:
            self.animation_running = False # Stop any running animation
            
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid_data[r][c] in (CELL_PATH, CELL_VISITED):
                    self.grid_data[r][c] = CELL_EMPTY
        
        self.find_path_button.config(text="Find Escape Path", state=tk.NORMAL)
        
        if redraw:
            self.draw_grid()

    def randomize_grid(self):
        """Randomly places start, end, walls, and fire."""
        if self.animation_running:
            return
            
        self.clear_grid()
        
        # Place Start
        start_r, start_c = random.randint(0, GRID_ROWS-1), random.randint(0, GRID_COLS-1)
        self.set_cell(start_r, start_c) # Use set_cell to handle logic
        
        # Place End (ensure it's not the same as start)
        self.current_tool = "end"
        end_r, end_c = start_r, start_c
        while (end_r, end_c) == self.start_pos:
            end_r, end_c = random.randint(0, GRID_ROWS-1), random.randint(0, GRID_COLS-1)
        self.set_cell(end_r, end_c)
        
        # Place Obstacles
        wall_percent = 0.20 # 20% walls
        fire_percent = 0.05 # 5% fire
        
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if (r,c) == self.start_pos or (r,c) == self.end_pos:
                    continue
                
                rand = random.random()
                if rand < fire_percent:
                    self.current_tool = "fire"
                    self.set_cell(r, c)
                elif rand < fire_percent + wall_percent:
                    self.current_tool = "wall"
                    self.set_cell(r, c)
                    
        self.select_tool("start") # Reset tool to start
        self.draw_grid()

    def calculate_heuristic(self, pos1, pos2):
        """Calculates the Manhattan distance heuristic for A*."""
        r1, c1 = pos1
        r2, c2 = pos2
        return abs(r1 - r2) + abs(c1 - c2)

    def start_pathfinding_animation(self):
        """Prepares and starts the step-by-step A* animation."""
        # 1. Validation
        if self.animation_running:
            self.animation_running = False
            self.find_path_button.config(text="Find Escape Path", state=tk.NORMAL)
            return
            
        if not self.start_pos:
            messagebox.showwarning("Error", "Please set a Start Point (🧑‍).")
            return
        if not self.end_pos:
            messagebox.showwarning("Error", "Please set an Exit Point (🚪).")
            return

        # 2. Clear old path
        self.clear_path(redraw=True) # Redraw to clear any old path

        # 3. A* Setup
        self.open_set = PriorityQueue()
        self.parent = {self.start_pos: None}
        
        # Initialize g_cost for all nodes to infinity
        self.g_cost = {}
        # g_cost for start node is 0
        self.g_cost[self.start_pos] = 0
        
        # Calculate f_cost for start node
        h_cost = self.calculate_heuristic(self.start_pos, self.end_pos)
        f_cost = self.g_cost[self.start_pos] + h_cost
        
        # Add start node to the priority queue
        # Items are (f_cost, h_cost, position)
        # We add h_cost as a tie-breaker
        self.open_set.put((f_cost, h_cost, self.start_pos))
        self.open_set_hash = {self.start_pos}
        
        self.animation_running = True
        self.find_path_button.config(text="Stop Animation", state=tk.NORMAL)
        
        # 4. Start the animation loop
        self.animate_astar_step()

    def animate_astar_step(self):
        """Performs one step of the A* algorithm and schedules the next."""
        if not self.animation_running:
            self.find_path_button.config(text="Find Escape Path", state=tk.NORMAL)
            return # Animation was stopped
            
        if self.open_set.empty():
            # Queue is empty, but path not found
            self.animation_running = False
            self.find_path_button.config(text="Find Escape Path", state=tk.NORMAL)
            messagebox.showinfo("No Path", "No valid escape path could be found!")
            return

        # Get the node with the lowest f_cost
        # current_data is (f_cost, h_cost, position)
        current_data = self.open_set.get()
        current_pos = current_data[2]
        self.open_set_hash.remove(current_pos)

        current_r, current_c = current_pos
        
        # --- Goal Check ---
        if current_pos == self.end_pos:
            self.animation_running = False
            self.find_path_button.config(text="Find Escape Path", state=tk.NORMAL)
            self.reconstruct_path_animation() # Start drawing the final path
            return

        # --- Explore Neighbors ---
        # (Up, Down, Left, Right)
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]: 
            nr, nc = current_r + dr, current_c + dc
            neighbor_pos = (nr, nc)

            # Check if neighbor is valid
            if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                cell_type = self.grid_data[nr][nc]
                is_obstacle = cell_type in (CELL_WALL, CELL_FIRE)
                
                if is_obstacle:
                    continue

                # Calculate temporary g_cost
                # Cost to move from one cell to another is 1
                temp_g_cost = self.g_cost[current_pos] + 1
                
                # Check if this path to the neighbor is better
                if temp_g_cost < self.g_cost.get(neighbor_pos, float('inf')):
                    # This is a better path, update costs and parent
                    self.parent[neighbor_pos] = current_pos
                    self.g_cost[neighbor_pos] = temp_g_cost
                    
                    h_cost = self.calculate_heuristic(neighbor_pos, self.end_pos)
                    f_cost = temp_g_cost + h_cost
                    
                    # Add to open set if it's not already there
                    if neighbor_pos not in self.open_set_hash:
                        self.open_set.put((f_cost, h_cost, neighbor_pos))
                        self.open_set_hash.add(neighbor_pos)
                        
                        # Animate the "visited" (open set) cell
                        if neighbor_pos != self.end_pos:
                            self.grid_data[nr][nc] = CELL_VISITED
                            self.draw_cell(nr, nc, CELL_VISITED)

        # Schedule the next step
        self.master.after(self.animation_speed.get(), self.animate_astar_step)
        
    def reconstruct_path_animation(self):
        """Animates the drawing of the final path from end to start."""
        path = []
        curr = self.end_pos
        while curr != self.start_pos:
            if curr not in self.parent: # Should not happen if path found
                break
            path.append(curr)
            curr = self.parent[curr]
        
        if not path:
            return

        # Start a separate animation to draw the path
        def draw_next_path_segment(path_index):
            if path_index < 0:
                return # Done
                
            r, c = path[path_index]
            if (r, c) != self.end_pos:
                self.grid_data[r][c] = CELL_PATH
                self.draw_cell(r, c, CELL_PATH)
            
            # Schedule the next segment
            self.master.after(max(10, self.animation_speed.get() // 2), 
                              lambda: draw_next_path_segment(path_index - 1))

        # Start drawing from the cell *before* the end
        draw_next_path_segment(len(path) - 1)


# --- Main execution ---
if __name__ == "__main__":
    root = tk.Tk()
    
    # Configure modal dialogs for dark theme (a bit of a hack for tkinter)
    root.tk_setPalette(background=THEME["BG_PRIMARY"], foreground=THEME["FG_PRIMARY"],
                      activeBackground=THEME["BTN_ACTIVE_BG"], activeForeground=THEME["FG_PRIMARY"])
    
    app = FireEscapeFinder(root)
    root.mainloop()


