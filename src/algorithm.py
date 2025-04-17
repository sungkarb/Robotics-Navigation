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
    
    def tsp_bruteforce(self, points: list[tuple[float, float]], start: int = 0) -> tuple[list, float]:
        """
        Finds the best path between a given set of points using bruteforce.
        
        Args:
            points - list of points to be visited in GPS coordinates
            start - starting point
        Returns:
            list of points in the order they should be visited
            float - distance of the path
        """
        tsp_start = time.time()
        n = len(points)
        dist_matrix = np.array([[util.dist_gps(points[i] - points[j]) for j in range(n)] for i in range(n)])
        
        cities = np.arange(n)
        cities = np.delete(cities, start)

        min_distance = np.inf
        best_route = None

        for perm in permutations(cities):
            route = np.concatenate(([start], perm))
            distance = np.sum([dist_matrix[route[i], route[i+1]] for i in range(len(route)-1)])

            if distance < min_distance:
                min_distance = distance
                best_route = route
        tsp_end = time.time()
        print(f"Bruteforce TSP took {round(tsp_end - tsp_start, 3)} seconds")
        return best_route, min_distance

    def find_path(self, start: tuple[float], end: tuple[float], alpha=10000, numpoints=5) -> list[tuple[float]]:
        """
        Finds the best path between start and end which are represented as tuple (x, y) using
        A* algorithm.

        Args:
            start - start point
            end - goal point
            alpha - hyperparameter controlling the degree to which change in elevation affects the path
                    computation
            numpoints - number of points to be returned along the path
        Returns:
            list of points starting from the start to end node
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

def main():
    solver = PathSolver("../datasets/camel_ridge_5.csv")
    pathpoints = solver.find_path([38.395879, -110.779201],[38.398112, -110.783233])
    print(pathpoints)

if __name__ == "__main__":
    main()
