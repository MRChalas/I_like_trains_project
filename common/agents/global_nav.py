import heapq
import numpy as np

FREE = 0
OCCUPIED = -1
FREE_COST = 1
OBST_COST = 100
DIRECTIONS = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
#Directions for 8-connected grid
#DIRECTIONS = np.array([(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)])  # Up, Down, Left, Right, Up-Left, Up-Right, Down-Left, Down-Right


def distance_grid(dir_grid, start_x, start_y, goal_x, goal_y):
    dist_matrix = np.full(dir_grid.shape, np.inf)
    dist_matrix[start_y][start_x] = 0
    needs_visit = [(0, start_y, start_x)]  # (distance, y, x)
    visited = set()

    while needs_visit:
        actual_dist, actual_y, actual_x = heapq.heappop(needs_visit)

        if (actual_y, actual_x) in visited:
            continue

        visited.add((actual_y, actual_x))

        if (actual_y, actual_x) == (goal_y, goal_x):
            break

        for i in range(len(DIRECTIONS)):
            dy, dx = DIRECTIONS[i]
            neig_y = actual_y + dy
            neig_x = actual_x + dx
            if 0 <= neig_x < dir_grid.shape[1] and 0 <= neig_y < dir_grid.shape[0]:
                if (neig_y, neig_x) in visited:
                    continue
                cost = dir_grid[neig_y][neig_x]
                new_dist = actual_dist + cost
                if dist_matrix[neig_y][neig_x] > new_dist:
                    dist_matrix[neig_y][neig_x] = new_dist
                    heapq.heappush(needs_visit, (new_dist, neig_y, neig_x))

    return dist_matrix

def path_find(dist_matrix, goal_x, goal_y, start_x, start_y, grid):
    actual_x = goal_x
    actual_y = goal_y
    actual_dist = dist_matrix[goal_y][goal_x]
    path = np.zeros_like(grid)
    path[actual_y][actual_x] = 1

    while (actual_x != start_x) or (actual_y != start_y):
        print(f"actual_x: {actual_x}, actual_y: {actual_y}, actual_dist: {actual_dist}")
        min_dist = float('inf')
        next_x, next_y = actual_x, actual_y

        for dy, dx in DIRECTIONS:
            neig_y = actual_y + dy
            neig_x = actual_x + dx

            if 0 <= neig_x < dist_matrix.shape[1] and 0 <= neig_y < dist_matrix.shape[0]:
                if dist_matrix[neig_y][neig_x] <= actual_dist and dist_matrix[neig_y][neig_x] < min_dist:
                    min_dist = dist_matrix[neig_y][neig_x]
                    next_x, next_y = neig_x, neig_y

        actual_x, actual_y = next_x, next_y
        path[actual_y][actual_x] = 1
        actual_dist = dist_matrix[actual_y][actual_x]

    return path