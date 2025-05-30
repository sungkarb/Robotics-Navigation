import rustworkx as rx
import pandas as pd
import numpy as np
import os, time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from scipy.spatial import KDTree

from itertools import permutations
import utilities as util

class PathSolver:
    def _init_helper(self):
        """
        Sets the main graph structure based on the point cloud using the Rustworkx graph structure
        Uses under the hood KDTree to find neigbouring nodes.
        """
        self.G = rx.PyGraph()
        self.dic = {}
        indx = 0

        for i in range(len(self.df)):
            point = tuple(self.df.iloc[i, :])
            _, neighbours = self.kdtree.query(point[:2], k=5)
            
            if point not in self.dic:
                self.G.add_node(point)
                self.dic[point] = indx
                indx += 1
            
            for neigbour_indx in neighbours:
                neigbour = tuple(self.df.iloc[neigbour_indx, :])
                if neigbour not in self.dic:
                    self.G.add_node(neigbour)
                    self.dic[neigbour] = indx
                    indx += 1
                
                ## Add edges
                self.G.add_edge(self.dic[point], self.dic[neigbour], [point, neigbour])


    def __init__(self, df: pd.DataFrame | str):
        """
        Loads the point cloud from the dataset and defines graph and kdtree structure
        to represent the point cloud efficiently.
        """
        if isinstance(df, str):
            df = pd.read_csv(df)
        
        ## Setup dataframe and kdtree for querying neighbours
        self.df = df
        self.xmean, self.ymean, self.zmean = df.mean()
        self.xstd, self.ystd, self.zstd = df.std()
        self.kdtree = KDTree(df.iloc[:, [0, 1]])

        ## Set the graph object
        self._init_helper()

    def _normalize_point(self, point: tuple[float]) -> tuple[float]:
        """
        Given point represented as a tuple of three floats, convert it to another point with zero mean 
        and unit variance.

        Args:
            point - list of three coordinates (x, y, z)
        Returns:
            transformed list of points with zero mean and unit variance
        """
        x, y, z = point
        x = (x - self.xmean) / self.xstd
        y = (y - self.ymean) / self.ystd
        z = (z - self.zmean) / self.zstd
        return (x, y, z)
    
    @staticmethod
    def tsp_bruteforce(start: tuple[float], points: list[tuple[float]]) -> tuple[list[tuple[float]], float]:
        """
        Finds the best path between a given set of points using bruteforce.
        
        Args:
            points - list of points to be visited in GPS coordinates
            start - starting point (should be distinct from the rest of the points)
        Returns:
            list of points in the order they should be visited, including the start point
            total distance of the path
        """
        points = [start] + points
        best_path = None
        min_dist = float('inf')

        for perm in permutations(points[1:]):
            current_path = [start] + list(perm)
            current_dist = sum(util.dist_gps(current_path[i], current_path[i + 1]) for i in range(len(current_path) - 1))
            if current_dist < min_dist:
                min_dist = current_dist
                best_path = current_path

        return best_path, min_dist

    def find_path(self, start: tuple[float], end: tuple[float], alpha=10000, numpoints=5) -> list[tuple[float]]:
        """
        Finds the best path between start and end which are represented as tuple (x, y, ...) using
        A* algorithm.

        Args:
            start - start point
            end - goal point
            alpha - hyperparameter controlling the degree to which change in elevation affects the path
                    computation
            numpoints - number of points to be returned along the path
        Returns:
            list of points starting from the start to end node in GPS coordinates (including the start point)
        """
        start = start[:2]
        end = end[:2]
        _, df_indx = self.kdtree.query(start)
        point = self.df.iloc[df_indx, :]
        graph_indx = self.dic[tuple(point)] 
    
        def goal_fn(node):
            dist = np.sqrt((node[0] - end[0])**2 + (node[1] - end[1])**2)
            return dist < 0.0001

        def edge_fn(edge):
            p1, p2 = edge
            p1, p2 = self._normalize_point(p1), self._normalize_point(p2)
            x1, y1, z1 = p1
            x2, y2, z2 = p2
            return (x1 - x2)**2 + (y1 - y2)**2 + alpha * (z1 - z2)**2

        def estimate_fn(node):
            node = self._normalize_point(node)
            dist = (node[0] - end[0])**2 + (node[1] - end[1])**2 
            return dist
        
        result_indx = rx.astar_shortest_path(self.G, graph_indx, goal_fn=goal_fn, edge_cost_fn=edge_fn, estimate_cost_fn=estimate_fn)
        result = [self.G[i] for i in result_indx]
        n = len(result)
        short_list = [result[i] for i in range(0, n, int(n / numpoints))]
        return short_list
    
    def find_full_path(self, start: tuple[float], targets: list[tuple[float]], alpha=10000, numpoints=5) -> list[tuple[float]]:
        """
        Finds the best open path from a given start point that visits all points in the list targets.

        Args:
            start - start point
            targets - list of target points to be visited
            alpha - hyperparameter controlling the degree to which change in elevation affects the path
                    computation
            numpoints - number of points to be returned along each edge of the path
        Returns:
            list of points starting from the start to end node in GPS coordinates
        """
        start = start[:2]
        targets = [target[:2] for target in targets]
        ordered_targets, _ = PathSolver.tsp_bruteforce(start, targets)
        path = []
        for i in range(len(ordered_targets) - 1):
            path += self.find_path(ordered_targets[i], ordered_targets[i + 1], alpha, numpoints)
        return path

def main():
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "datasets", "camel_ridge_5.csv"))
    solver = PathSolver(data_path)
    # pathpoints = solver.find_path([38.395879, -110.779201],[38.398112, -110.783233])
    path_points = solver.find_full_path([38.395879, -110.779201], [[38.398112, -110.783233], [38.396112, -110.783233], [38.397112, -110.783233]])
    print(path_points)

if __name__ == "__main__":
    main()
