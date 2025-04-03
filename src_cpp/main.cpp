#include <iostream>
#include <fstream>
#include <string>
#include <cmath>
using namespace std;

/**
 * Reads csv file containing points
 * 
 * @param file_path - path to the file containing the point cloud
 * @param points - 2D matrix to which we want to save our points
 * @return 0 if operation was successful and -1 if file wasn't found
 */
int read_points_from_csv(string file_path, vector<vector<double>> &points)
{
    ifstream file = ifstream(file_path);
    if (!file.is_open())
    {
        cout << "File " + file_path << " doesn't exist" << endl;
        return -1;
    }

    // Count number of colums
    string line;
    getline(file, line);
    int num_columns = 0;
    for (int i = 0; i < line.size(); i++)
    {
        if (line[i] == ',')
            num_columns += 1;
    }

    // Create all necessary columns 
    for (int i = 0; i < num_columns; i++)
    {
        points.push_back(vector<double>());
    }

    // Add all points to the vector
    cout << "Got to this pint" << endl;
    while (getline(file, line))
    {
        char buffer[1024];
        strcpy(buffer, line.c_str());
        if (buffer[strlen(buffer) - 1] == '\n')
            buffer[strlen(buffer) - 1] = '\0';
        
        char *token = strtok(buffer, ",");
        int i = 0;
        while (token != NULL)
        {
            double val = stod(token);
            points[i].push_back(val);
            i += 1;
            token = strtok(NULL, ",");
        }
    }
    file.close();
    
    cout << "Successfully stored points from " + file_path << endl;
    return 0;
}

/**
 * Fills a grid out of the points in the shape (a x b x 3)
 * 
 * Example:
 * ```
 * [[0, 0, 0.00], 
 *  [0, 1, 0.01],
 *  [1, 0, 0.1],  
 *  [1, 1, 0.11]]
 * ```
 * becomes
 * ```
 * [[[0, 0, 0.00], [0, 1, 0.01]],
 *  [[1, 0, 0.1], [1, 1, 0.11]]]
 * ```
 * @param points - 2D array of shape (n x 3) where each point is (lat, lon, alt)
 * @param M - grid matrix which we want to fill
 * @param a - height of the grid matrix
 * @param b - width of the grid matrix
 */
void fill_grid(vector<vector<double>> &points, vector<vector<vector<double>>> M)
{
    // Find min, max latitude and longtitude
    double xmin = *min_element(points[0].begin(), points[0].end());
    double xmax = *max_element(points[0].begin(), points[0].end());
    double ymin = *min_element(points[1].begin(), points[1].end());
    double ymax = *max_element(points[1].begin(), points[1].end());  

    // Fill the provided matrix
    int a = M.size(), b = M[0].size();
    int skipped = 0;
    for (int i = 0; i < points[0].size(); i++)
    {
        double x = points[i][0], y = points[i][1], z = points[i][2];

        // Compute indices
        int indx1 = floor((x - xmin) * (a - 1) / (xmax - xmin));
        int indx2 = floor((y - ymin) * (b - 1) / (ymax - ymin));

        if (M[indx1][indx2][0] == 0.0)
        {
            M[indx1][indx2][0] = x;
            M[indx1][indx2][1] = y;
            M[indx1][indx2][2] = z;
        }
        else
        {
            skipped += 1;
        }
    }

    cout << "Skipped " << skipped << " points due to collision" << endl;
}


int main()
{
    string folder = "../datasets";
    string file_name = "grid_test.csv";
    string path = folder + "/" + file_name;

    // Get points from the file
    vector<vector<double>> points = vector<vector<double>>();
    read_points_from_csv(path, points);

    int a = 10;
    int b = 10;



    return 0;
}