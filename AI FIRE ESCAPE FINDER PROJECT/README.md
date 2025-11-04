🔥 Fire Escape Path Finder 🧑‍

A desktop application built with Python and Tkinter that visualizes the A* pathfinding algorithm in a simulated fire escape scenario.

Users can interactively build a grid layout with walls, fires, a start point, and an exit. The application will then find and animate the safest (shortest) escape route, navigating around all obstacles.

(Suggestion: Add a screenshot or, even better, a GIF of the application in action here!)

---

✨ Features

Interactive Grid: A 20x20 clickable and draggable grid.

*A Pathfinding:** Implements the A* search algorithm to find the optimal path from start to exit.

Visual Animation: Animates both the algorithm's search (visited nodes) and the final reconstructed path.

Dynamic Obstacles: Place "Walls" (🧱) and "Fire" (🔥) as impassable obstacles.

---

Full Toolset:

Start 🧑‍: Set the starting position.

Exit 🚪: Set the destination.

Wall 🧱: Draw wall obstacles.

Fire 🔥: Draw fire obstacles.

Eraser 🧹: Clear any cell.

Grid Controls:

Find Escape Path: Starts/Stops the pathfinding animation.

Randomize Grid: Automatically populates the grid with all elements.

Clear Path: Removes only the path and visited-node visualization.

Clear Full Grid: Resets the entire grid.

Speed Control: An adjustable slider to control the animation speed.

Dark Mode UI: A clean, custom dark-mode theme.

---

🚀 How to Run

This application uses Python's built-in Tkinter library, so no external packages are required.

Ensure you have Python 3 installed.

Save the code: Save the project code as FireEscapeFinder.py.

Run the application from your terminal:

python FireEscapeFinder.py

---

🛠️ How to Use

Select a Tool: Click one of the tool buttons on the right-hand panel (e.g., "Start 🧑‍", "Wall 🧱").

Build Your Map: Click or click-and-drag on the grid to place your selected items.

You can only have one Start and one Exit. Placing a new one will move the old one.

Find the Path: Once you have a Start and an Exit, click the "Find Escape Path" button.

Watch: The application will first animate the search (blue-gray cells) and then draw the final path (cyan cells) if one is found.

---

Controls:

Use the "Animation Speed" slider to speed up or slow down the visualization.

Use "Clear Path" to try again with a new layout or "Clear Full Grid" to start from scratch.

---

🧠 Algorithm

The pathfinding logic is powered by the A (A-star) search algorithm*.

It uses a Priority Queue to efficiently explore nodes with the lowest "f-cost".

g-cost: The actual cost (number of steps) from the start node.

h-cost (Heuristic): The estimated cost to the end, calculated using the Manhattan distance.

f-cost = g-cost + h-cost

The algorithm treats both Walls and Fire as impassable obstacles (it cannot travel through those cells).
