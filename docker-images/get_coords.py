#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time

import h3
import math
import sys
import json
import random

# 最终返回的经纬度在中心点上进行随机偏移0-500m
min_random = 0
max_random = 500


class Coordinates:
    def __init__(self):
        self.latitude = 0
        self.latitude = 0

    # 请问以下代码是否能够根据rows和cols生成坐标矩阵，要求：1.横纵坐标点都必须间隔2000米；2.在确定好的矩阵坐标每个中心坐标点随机100-800偏差；请优化以下代码以满足要求,下面代码测试一个2*2的矩阵，坐标3和坐标1实测是1.5公里，测试结果不满足需求
    import math
    import random

    def get_matrix_coordinates(self, latitude, longitude, rows=2, cols=3):
        const_number = 111320
        if rows < 1 or cols < 1:
            raise ValueError("rows and cols need >= 1")

        # 检查纬度和经度是否在合理范围内
        if latitude < -90 or latitude > 90:
            raise ValueError("latitude range : [-90, 90]")
        if longitude < -180 or longitude > 180:
            raise ValueError("longitude range [-180, 180]")

        try:
            distance = 2000  # 2000 米

            matrix_coordinates = []
            for row in range(rows):
                for col in range(cols):
                    # 计算每个坐标点相对于左上角的偏移量,保证横纵坐标点间隔 2000 米
                    offset_latitude = latitude + (row - (rows - 1) / 2) * distance / const_number
                    offset_longitude = longitude + (col - (cols - 1) / 2) * distance / (
                            const_number * math.cos(math.radians(latitude)))

                    offset_index_latitude, offset_index_longitude = self.get_center_coords(offset_latitude,
                                                                                           offset_longitude)

                    random_distance = random.uniform(min_random, max_random)
                    random_bearing = random.uniform(0, 360)
                    res_latitude = offset_index_latitude + math.sin(
                        math.radians(random_bearing)) * random_distance / const_number
                    res_longitude = offset_index_longitude + math.cos(
                        math.radians(random_bearing)) * random_distance / (
                                            const_number * math.cos(math.radians(res_latitude)))

                    matrix_coordinates.append(
                        {"latitude": res_latitude, "longitude": res_longitude,
                         "offset_center_latitude": offset_index_latitude,
                         "offset_center_longitude": offset_index_longitude})
            return matrix_coordinates
        except ValueError as e:
            print(f"error: {e}")
            return []

    def get_center_coords(self, latitude, longitude):
        h3_index = h3.geo_to_h3(latitude, longitude, 9)
        center_latitude, center_longitude = h3.h3_to_geo(h3_index)
        return center_latitude, center_longitude

    def get_coordinates_form_index(self, h3_index, number):
        center_latitude, center_longitude = h3.h3_to_geo(h3_index)
        # print(f" request get_coordinates_form_index:{center_latitude},{center_longitude}")
        h3_index = h3.geo_to_h3(center_latitude, center_longitude, 9)
        rows, cols = self.get_rows_and_cols(number)
        matrix_coords = self.get_matrix_coordinates(center_latitude, center_longitude, rows, cols)
        # self.test(matrix_coords)
        matrix_coordinates = []
        for row in matrix_coords:
            try:
                lat1, lon1 = row["latitude"], row["longitude"]
                lat_and_long = f"{lat1},{lon1}"
                matrix_coordinates.append({"lat_and_long": lat_and_long})
            except ValueError as e:
                print(f"error: {e}")
                continue
        return matrix_coordinates

    def get_rows_and_cols(self, number):
        if number <= 1:
            rows = 1
            cols = 1
        elif number < 4:
            rows = 2
            cols = 2
        elif number < 6:
            rows = 2
            cols = 3
        elif number < 9:
            rows = 3
            cols = 3
        elif number < 11:
            rows = 3
            cols = 4
        elif number < 15:
            rows = 4
            cols = 4
        else:
            num_diff = number - 11
            rows = 3 + (num_diff // 8) + 1
            cols = 4 + (num_diff // 8) + 1
        return rows, cols

    def test(self, matrix_coordinates):
        for i in range(len(matrix_coordinates)):
            latitude, longitude, = matrix_coordinates[i]["latitude"], matrix_coordinates[i]["longitude"]
            offset_center_latitude, offset_center_longitude = matrix_coordinates[i]["offset_center_latitude"], \
                matrix_coordinates[i]["offset_center_longitude"]
            offset_index_lat_and_long = f"{offset_center_latitude},{offset_center_longitude}"
            center_latitude, center_longitude = self.get_center_coords(latitude, longitude)
            index_lat_and_long = f"{center_latitude},{center_longitude}"

            origin = (latitude, longitude)
            destination = (offset_center_latitude, offset_center_longitude)
            R = 6371000  # 地球半径,单位为米
            phi1 = math.radians(origin[1])
            phi2 = math.radians(destination[1])
            delta_phi = math.radians(destination[1] - origin[1])
            delta_lambda = math.radians(destination[0] - origin[0])

            a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c

            print(
                f"偏移后的经纬度:{latitude},{longitude} 返回的中心坐标：{offset_index_lat_and_long}，二次获取中心坐标：{index_lat_and_long}， 距离中心点位：{distance}")

        for i in range(len(matrix_coordinates) - 1):
            lat1, lon1 = matrix_coordinates[i]["latitude"], matrix_coordinates[i]["longitude"]
            lat2, lon2 = matrix_coordinates[i + 1]["latitude"], matrix_coordinates[i + 1]["longitude"]

            # 转换坐标到H3索引
            origin_h3 = h3.geo_to_h3(lat1, lon1, 9)
            destination_h3 = h3.geo_to_h3(lat2, lon2, 9)

            # 计算两个H3索引之间的距离
            index_distance = h3.h3_distance(origin_h3, destination_h3) * 1000
            # 计算2个坐标中心点位的距离
            origin_center_latitude, origin_center_longitude = h3.h3_to_geo(origin_h3)
            destination_center_latitude, destination_center_longitude = h3.h3_to_geo(destination_h3)
            origin = (origin_center_latitude, origin_center_longitude)
            destination = (destination_center_latitude, destination_center_longitude)
            R = 6371000  # 地球半径,单位为米
            phi1 = math.radians(origin[1])
            phi2 = math.radians(destination[1])
            delta_phi = math.radians(destination[1] - origin[1])
            delta_lambda = math.radians(destination[0] - origin[0])

            a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            distance = R * c
            print(f"i:{i},j:{i + 1} ->相邻元素中心坐标距离: {distance:.2f}米")


def main():
    if len(sys.argv) < 3:
        process_name = str(sys.argv[0])
        print(f"Example usage: {process_name} 8864a4606dfffff 8")
        return

    try:
        h3_index = str(sys.argv[1])
        number = int(sys.argv[2])
        d = Coordinates()
        matrix_coords = d.get_coordinates_form_index(h3_index, number)
        # print(json.dumps(matrix_coords))
        for row in matrix_coords:
            lat_and_long = row["lat_and_long"]
            print(f"{lat_and_long}")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please make sure the input parameters are of the correct type.")
    except Exception as e:
        print(f"Unknown error: {e}")


if __name__ == "__main__":
    main()
