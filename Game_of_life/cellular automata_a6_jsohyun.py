import random
import rhinoscriptsyntax as rs
import time
import copy

cols = 7
rows = 7
cell_size = 10  # Define the cell size
# Create a 2D Array and points grid
def make2DArrayGrid(cols, rows):
    grid = []
    for i in range(rows):
        row = []
        for j in range(cols):
            state = random.randint(0, 1)  # Randomly initialize alive (1) or dead (0), which will not appear
            row.append(state)
        grid.append(row)
    return grid

# Count 1st-layer neighbors
def count_neighbors(grid, x, y):
    sum_neighbors = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            col = (x + i)
            row = (y + j)
            if col in range(0, cols) and row in range(0, rows):
                sum_neighbors += grid[row][col]
    sum_neighbors -= grid[y][x]  # Subtract the cell itself from count
    return sum_neighbors

# Count 1st-layer neighbors
def count_far_neighbors(grid, x, y):
    sum_neighbors = 0
    for i in range(-2, 3):
        for j in range(-2, 3):
            if i in [-2, 2] or j in [-2, 2]: #check only edge cases
                col = (x + i)
                row = (y + j)
                if col in range(0, cols) and row in range(0, rows): #fix the bug, mod sometimes doesn't work
                    sum_neighbors += grid[row][col]
#    print(x, y, list, sum_neighbors)
    return sum_neighbors

def pos_far_neighbor(next_grid, grid, x, y):
    pos = []
    for i in range(-2, 3):
        for j in range(-2, 3):
            if i in [-2, 2] or j in [-2, 2]: #check only edge cases
                col = (x + i)
                row = (y + j)
                if col in range(0, cols) and row in range(0, rows):
                    if next_grid[row][col] == 1:
                        pos.append((i, j)) #save the direction
    if grid[y][x] == 0: 
        if (-2, 0) in pos:
            return 90
        elif (2, 0) in pos:
            return -90
        elif (0, -2) in pos:
            return 180
        elif (0, 2) in pos:
            return 0
    return None
        
def check_neighbor(dict, x, y, generation):
    count = 0
    for i in range(-1, 2):
        for j in range(-1, 2):
            if dict.get((x + i, y + j, generation)) == 0:
                count += 1
    return count

def plant_balcony(live_cells, tree_cells, col, row, buffer, z_offset):
    for a in range(-1, 2):
        for b in range(-1, 2):
                i = a + col
                j = b + row
                pt = (i * cell_size, j * cell_size, z_offset) 
                ##################################
                if i in [-1, cols] or j in [-1, rows] and not tree_cells.get((i, j, generation)):
                    if (i + j) % 2 == 0 or generation %2 == 0 : #sparse the density
                        tree_cells[(i, j, generation)] = rs.InsertBlock("big_tree", rs.CreatePoint(pt[0], pt[1], pt[2]), [1, 1, 1])

# Update the grid for the next generation and place blocks at the correct Z-offset
def update_grid(cols, rows, grid, generation):
    next_grid = []
    next_grid = copy.deepcopy(grid)
    # Calculate the Z-offset for the current generation
    z_offset = generation * cell_size *1.3
    
    #To test initial state
    if generation == 0: 
        for row in range(rows):
            for col in range(cols):
                pt = (col * cell_size - 200, row * cell_size, 0)
                if grid[row][col] == 0:
                    dead_cells[(col, row, generation)] = 0
                    rs.InsertBlock("dead", rs.CreatePoint(pt[0], pt[1], pt[2]), [1, 1, 1])
                else:
                    live_cells[(col, row, generation)] = 0
                    rs.InsertBlock("live", rs.CreatePoint(pt[0], pt[1], pt[2]), [1, 1, 1])
# selective, sparse.
    for i in range(cols):
        for j in range(rows):
            neighbors = count_neighbors(grid, i, j)
            far_neighbors = count_far_neighbors(grid, i, j)
            state = grid[j][i]
            buffer = (generation + 1) * 200
            pt = (i * cell_size, j * cell_size, z_offset)  # Adjust Z position based on generation
            pt_plan = (i * cell_size + buffer, j * cell_size, z_offset)
            # Game of Life rules and rendering
            if state == 0 and neighbors == 0 and far_neighbors < 5 :  # A dead cell becomes alive
                next_grid[j][i] = 1
                house = rs.InsertBlock("live", rs.CreatePoint(pt[0], pt[1], pt[2]), [1, 1, 1]) 
                if neighbors < 2: #rotate house.
                    rs.RotateObject(house, (pt[0], pt[1], pt[2]), 90)
                live_cells[(i, j, generation)] = 0
                
            elif state == 1 and neighbors > 3 or neighbors < 2:  # A live cell dies
                next_grid[j][i] = 0
                dead_cells[(i, j, generation)] = 0
                rs.InsertBlock("dead", rs.CreatePoint(pt[0], pt[1], pt[2]), [1, 1, 1])
                
            elif state == 1: # A live cell: 2 or 3 
                live_cells[(i, j, generation)] = 0
                rs.InsertBlock("live", rs.CreatePoint(pt[0], pt[1], pt[2]), [1, 1, 1])
                
            elif state == 0: # A dead cell: other than 3
                dead_cells[(i, j, generation)] = 0
                rs.InsertBlock("dead", rs.CreatePoint(pt[0], pt[1], pt[2]), [1, 1, 1])
    #plant trees, fontains, ladders, big trees.
    for i in range(cols):
        for j in range(rows):
            neighbors = count_neighbors(next_grid, i, j)
            far_neighbors = count_far_neighbors(next_grid, i, j)
            state = next_grid[j][i]
            buffer = generation * 200
            pt = (i * cell_size, j * cell_size, z_offset) 
            ##
#            rs.AddTextDot(neighbors, (pt[0], pt[1], pt[2]))

            #add ladder.
            if state == 0 and neighbors == 0:
                if check_neighbor(ladder_cells, i, j, generation) < 3 and not ladder_cells.get((i, j, generation)):
                    if far_neighbors < 5 and generation != 0:
                        angle = pos_far_neighbor(next_grid, grid, i, j)
                        if angle:
                            ladder = rs.InsertBlock("ladder", rs.CreatePoint(pt[0], pt[1], pt[2]), [1, 1, 1]) 
                            rs.RotateObject(ladder, (pt[0], pt[1], pt[2]), angle)
                            ladder_cells[(i, j, generation)] = 0
                            
            if state == 0 and neighbors != 0: # plant tree in the slab
                #add small trees
                if neighbors > 3: #only if high density of house
                    tree_cells[(i, j, generation)] = 0
                    rs.InsertBlock("tree", rs.CreatePoint(pt[0], pt[1], pt[2]), [1, 1, 1])
                #add fontains
                previous = generation -1
                if not tree_cells.get((i, j, generation)) and not water_cells.get((i, j, generation)) and ladder_cells.get((i, j, previous))!= 0: 
                    if neighbors == 1 and check_neighbor(water_cells, i, j, generation) < 1:
                        water = rs.InsertBlock("water", rs.CreatePoint(pt[0], pt[1], pt[2]), [1, 1, 1])
                        angle = random.choice([0, 90, 180, 360])
                        rs.RotateObject(water, (pt[0], pt[1], pt[2]), angle)
                        water_cells[(i, j, generation)] = 0
                        
      
            #plant big tree!
            if state == 1: 
                if i in [0, cols -1] or j in [0, rows -1]: #go to the balcony
                    if far_neighbors > 5 or neighbors < 3:
                        plant_balcony(live_cells, tree_cells, i, j, buffer, z_offset)
                        
    return next_grid

 
# Initialize grid and dictionaries for live and dead cells
grid = make2DArrayGrid(cols, rows)
live_cells = {}  # Dictionary to track live cells and their objects
dead_cells = {}  # Dictionary to track dead cells and their objects
tree_cells = {}
water_cells = {}
ladder_cells = {}

# Run the simulation for multiple generations
num_generations = 10  # Set the number of generations

for generation in range(num_generations):
    rs.EnableRedraw(False)  # Disable screen redraw for the update phase
    grid = update_grid(cols, rows, grid, generation)  # Update grid to the next generation