import h3
import sys

from get_coordinates import Coordinates


def get_index():
    if len(sys.argv) < 2:
        print("Usage: python3 get_index.py <h3_index>" + "\nExample: python3 get_index.py 8843a39233fffff")
        return

    try:
        h3_index = sys.argv[1]
        center_latitude, center_longitude = h3.h3_to_geo(h3_index)
        print(f"center_longitude {center_longitude} center_latitude: {center_latitude},")
        d = Coordinates()
        rows, cols = 1, 2
        matrix_coords = d.get_matrix_coordinates(center_latitude, center_longitude, rows, cols)
        print("矩阵为： ", rows, "*", cols, "生成的坐标数量：", len(matrix_coords))
        print(matrix_coords)
    except (IndexError, ValueError):
        print("Error: Invalid input. Please provide a valid H3 index.")


if __name__ == "__main__":
    get_index()
