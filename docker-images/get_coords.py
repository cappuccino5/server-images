#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time

import h3
import math
import sys
import json
import random
import argparse

# 最终返回的经纬度在中心点上进行随机偏移0-300m
min_random = 0
max_random = 300
radius = 500  # 半径500m


class Item:
    h3_index = ""
    latitude = 0.0
    longitude = 0.0


class Coordinates:
    def __init__(self, skip_list):
        self.skip_items = []
        self.count = 0
        for skip_h3_index in skip_list:
            self.append_skip_list(skip_h3_index)

    def append_skip_list(self, skip_h3_index):
        center_latitude, center_longitude = h3.h3_to_geo(skip_h3_index)
        new_item = Item()
        new_item.h3_index = skip_h3_index
        new_item.latitude = center_latitude
        new_item.longitude = center_longitude
        self.skip_items.append(new_item)

    # 根据rows和cols生成坐标矩阵，要求：1.横坐标点间隔1440米；纵坐标间隔1000米，2.在确定好的矩阵坐标每个中心坐标点随机0-300偏差；3.坐标矩阵x轴角度15度
    def get_matrix_coordinates(self, latitude, longitude, rows=2, cols=3):
        const_number = 111320
        x_distance = 1380  # 经度 (x 轴) 间隔 1400 米
        y_distance = 1000  # 纬度 (y 轴)

        if rows < 1 or cols < 1:
            raise ValueError("rows and cols need >= 1")
        # if (rows * cols) % 2 == 0:
        #     y_distance = y_distance * 2
        if latitude < -90 or latitude > 90:
            raise ValueError("latitude range : [-90, 90]")
        if longitude < -180 or longitude > 180:
            raise ValueError("longitude range [-180, 180]")

        try:
            matrix_coordinates = []
            for row in range(rows):
                for col in range(cols):
                    center_latitude = latitude + (row - (rows - 1) / 2) * y_distance / const_number
                    center_longitude = longitude + (col - (cols - 1) / 2) * x_distance / (
                            const_number * math.cos(math.radians(latitude)))
                    rot_latitude = (center_latitude - latitude) * math.cos(math.radians(16)) - (
                            center_longitude - longitude) * math.sin(math.radians(16)) + latitude
                    rot_longitude = (center_latitude - latitude) * math.sin(math.radians(2)) + (
                            center_longitude - longitude) * math.cos(math.radians(2)) + longitude

                    offset_index_latitude, offset_index_longitude = self.get_center_coords(rot_latitude,
                                                                                           rot_longitude)
                    check_skip = self.check_skip(rot_latitude, rot_longitude)
                    if check_skip:
                        print("check_skip ", check_skip)
                        continue
                    # 正方形矩阵OK
                    # offset_latitude = latitude + (row - (rows - 1) / 2) * y_distance / const_number
                    # offset_longitude = longitude + (col - (cols - 1) / 2) * x_distance / (
                    #         const_number * math.cos(math.radians(latitude)))
                    #
                    # offset_index_latitude, offset_index_longitude = self.get_center_coords(offset_latitude,
                    #
                    #                                                                                         check_skip = self.check_skip(res_latitude, res_longitude)offset_longitude)

                    random_distance = random.uniform(min_random, max_random)
                    random_bearing = random.uniform(0, 360)
                    res_latitude = offset_index_latitude + math.sin(
                        math.radians(random_bearing)) * random_distance / const_number
                    res_longitude = offset_index_longitude + math.cos(
                        math.radians(random_bearing)) * random_distance / (
                                            const_number * math.cos(math.radians(res_latitude)))

                    check_skip = self.check_skip(res_latitude, res_longitude)
                    if check_skip:
                        continue

                    matrix_coordinates.append(
                        {"latitude": res_latitude, "longitude": res_longitude,
                         "offset_center_latitude": offset_index_latitude,
                         "offset_center_longitude": offset_index_longitude})
                    # if len(matrix_coordinates) >= self.count:
                    #     break
            return matrix_coordinates
        except ValueError as e:
            print(f"error: {e}")
            return []

    def check_skip(self, latitude, longitude):
        #  因为同一位置获取的索引号不一样，所以需要判断距离范围，小于定义的范围则需要跳过
        #  需要跳过的索引号  881fb28105fffff, 47.71687360792071,2.111948816472573 ；测试结果--->  8f1fb281041655a, 47.71592896066951,2.110156714481889
        for skip_value in self.skip_items:
            distance = self.distance(skip_value.latitude, skip_value.longitude, latitude, longitude)
            if distance < radius:
                print(
                    f"get_center_coords skipping  {skip_value.h3_index}, {skip_value.latitude},{skip_value.longitude}--->,{latitude},{longitude}")
                return True
        return False

    def get_center_coords(self, latitude, longitude):
        h3_index = h3.geo_to_h3(latitude, longitude, 14)
        center_latitude, center_longitude = h3.h3_to_geo(h3_index)
        return center_latitude, center_longitude

    def get_coordinates_form_index(self, h3_index, number):
        center_latitude, center_longitude = h3.h3_to_geo(h3_index)
        print(f" request h3_index: {h3_index} get_coordinates_form_index: {center_latitude},{center_longitude}")
        rows, cols = self.get_rows_and_cols(number)
        matrix_coords = self.get_matrix_coordinates(center_latitude, center_longitude, rows, cols)
        return matrix_coords

    def get_coordinates_form_lat_and_long(self, latitude, longitude, number):
        center_latitude, center_longitude = self.get_center_coords(latitude, longitude)
        print(f" request get_coordinates_form_lat_and_long: {center_latitude},{center_longitude}")
        rows, cols = self.get_rows_and_cols(number)
        matrix_coords = self.get_matrix_coordinates(center_latitude, center_longitude, rows, cols)
        return matrix_coords

    def get_rows_and_cols(self, number):
        number = number + len(self.skip_items) + int((number * 0.2))
        self.count = number
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

    def distance(self, lat1, lon1, lat2, lon2):
        origin = (lat1, lon1)
        destination = (lat2, lon2)
        R = 6371000  # 地球半径,单位为米
        phi1 = math.radians(origin[1])
        phi2 = math.radians(destination[1])
        delta_phi = math.radians(destination[1] - origin[1])
        delta_lambda = math.radians(destination[0] - origin[0])

        a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    def test(self, matrix_coordinates):
        for i in range(len(matrix_coordinates)):
            latitude, longitude, = matrix_coordinates[i]["latitude"], matrix_coordinates[i]["longitude"]
            offset_center_latitude, offset_center_longitude = matrix_coordinates[i]["offset_center_latitude"], \
                matrix_coordinates[i]["offset_center_longitude"]
            offset_index_lat_and_long = f"{offset_center_latitude},{offset_center_longitude}"
            center_latitude, center_longitude = self.get_center_coords(latitude, longitude)
            index_lat_and_long = f"{center_latitude},{center_longitude}"

            distance = self.distance(latitude, longitude, offset_center_latitude, offset_center_longitude)
            print(
                f"偏移后的经纬度:{latitude},{longitude} 返回的中心坐标：{offset_index_lat_and_long}，二次获取中心坐标：{index_lat_and_long}， 距离中心点位：{distance}")

        for i in range(len(matrix_coordinates) - 1):
            lat1, lon1 = matrix_coordinates[i]["offset_center_latitude"], \
                matrix_coordinates[i]["offset_center_longitude"]
            lat2, lon2 = matrix_coordinates[i + 1]["offset_center_latitude"], \
                matrix_coordinates[i + 1]["offset_center_longitude"]
            distance = self.distance(lat1, lon1, lat2, lon2)
            print(f"i:{i},j:{i + 1} ->相邻元素中心坐标距离: {distance:.2f}米")


def main():
    process_name = str(sys.argv[0])
    parser = argparse.ArgumentParser(description="Helium Get batch coordinates",
                                     epilog=f"""Example usage:
        {process_name} -x 881fb2810dfffff -n 2
        {process_name} -x 881fb2810dfffff -n 2 -skip 881fb2810dfffff,881fb28105fffff
        {process_name} -lat 47.7247769110229 -lon 2.108315381765773 -n 2""",
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # 定义参数
    parser.add_argument("-lat", "--latitude", type=float, required=False, help="Latitude coordinate (optional)")
    parser.add_argument("-lon", "--longitude", type=float, required=False, default=0.0,
                        help="Longitude coordinate (optional)")
    parser.add_argument("-x", "--hex", type=str, required=False, default='',
                        help="Longitude and latitude index (optional)")
    parser.add_argument("-n", "--number", type=int, required=True,
                        help="The number of locations to be located (required)")
    parser.add_argument("-skip", "--skip", type=str, required=False, default='',
                        help="Comma-separated list of hex values to skip (optional)")

    args = parser.parse_args()
    latitude = args.latitude
    longitude = args.longitude
    h3_index = args.hex
    number = args.number
    skip_list = args.skip.split(',') if args.skip else []

    try:
        matrix_coords = []
        d = Coordinates(skip_list)
        if h3_index != "":
            d.append_skip_list(h3_index)
            matrix_coords = d.get_coordinates_form_index(h3_index, number)
        elif latitude != 0 and longitude != 0:
            matrix_coords = d.get_coordinates_form_lat_and_long(latitude, longitude, number)

        d.test(matrix_coords)
        # 随机排序
        random.shuffle(matrix_coords)
        # print(json.dumps(matrix_coords))
        count = 0

        for row in matrix_coords:
            if count >= d.count:
                break
            lat1, lon1 = row["latitude"], row["longitude"]
            lat_and_long = f"{lat1},{lon1}"
            print(f"{lat_and_long}")
            count = count + 1
        print(f"total_count  {len(matrix_coords)}, return count {count}")
    except ValueError as e:
        print(f"Error: {e}")
        print("Please make sure the input parameters are of the correct type.")
    except Exception as e:
        print(f"Unknown error: {e}")


if __name__ == "__main__":
    main()
