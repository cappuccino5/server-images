#!/usr/bin/python3
# -*- coding: utf-8 -*-
import time

import h3
import math
import sys
import json
import random

# 最终返回的经纬度在中心点上进行随机偏移100-800m
min_random = 100
max_random = 800

# 使用111320这个常数来表示地球上1度纬度等于111,320米
# 这个常数是用来换算距离和经纬度的关系。因为纬度度数随着位置的变化而变化,所以需要乘以math.cos(math.radians(center_latitude))来校正经度偏移量。
const_number = 111320

"""
get_matrix_coordinates
根据给定的经纬度坐标,生成与中心坐标点间隔2公里的 rows x cols 的矩阵坐标,同时在返回的坐标上加上1-800米的随机偏移.

参数:
latitude (float): 纬度
longitude (float): 经度
rows (int): 矩阵行数
cols (int): 矩阵列数
resolution (int): H3 索引分辨率,默认为9

返回:
list: rows x cols 矩阵坐标列表
"""


def get_matrix_coordinates(latitude, longitude, rows=2, cols=3, resolution=9):
    if rows < 1 or cols < 1:
        raise ValueError("行数和列数必须大于等于1")

    # 检查纬度和经度是否在合理范围内
    if latitude < -90 or latitude > 90:
        raise ValueError("纬度必须在 [-90, 90] 范围内")
    if longitude < -180 or longitude > 180:
        raise ValueError("经度必须在 [-180, 180] 范围内")

    try:
        # 获取H3索引
        h3_index = h3.geo_to_h3(latitude, longitude, resolution)

        # print(f"h3_index{h3_index} ,纬度: {latitude}, 经度: {longitude}, 精度: {resolution}")
        # 获取中心坐标点
        center_latitude, center_longitude = h3.h3_to_geo(h3_index)
        # print(f"中心纬度: {center_latitude}, 中心经度: {center_longitude}")

        # 计算2公里距离的经纬度偏移量
        distance = 2000  # 2公里
        lat_offset = math.sin(math.radians(90)) * distance / const_number
        lon_offset = math.cos(math.radians(center_longitude)) * distance / (
                const_number * math.cos(math.radians(center_latitude)))

        matrix_coordinates = []
        for row in range(rows):
            for col in range(cols):
                offset_latitude = center_latitude + (row - (rows - 1) / 2) * lat_offset
                offset_longitude = center_longitude + (col - (cols - 1) / 2) * lon_offset
                offset_index = h3.geo_to_h3(offset_latitude, offset_longitude, resolution)
                res_latitude, res_longitude = h3.h3_to_geo(offset_index)

                # 添加每个中心索引坐标随机偏移 0~800
                random_distance = random.uniform(min_random, max_random)
                random_bearing = random.uniform(0, 360)
                res_latitude += math.sin(math.radians(random_bearing)) * random_distance / const_number
                res_longitude += math.cos(math.radians(random_bearing)) * random_distance / (
                        const_number * math.cos(math.radians(res_latitude)))

                matrix_coordinates.append({"latitude": res_latitude, "longitude": res_longitude})
        return matrix_coordinates
    except ValueError as e:
        print(f"错误: {e}")
        return []


def get_rows_and_cols(number):
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


def test(matrix_coordinates):
    for i in range(len(matrix_coordinates) - 1):
        lat1, lon1 = matrix_coordinates[i]["latitude"], matrix_coordinates[i]["longitude"]
        lat2, lon2 = matrix_coordinates[i + 1]["latitude"], matrix_coordinates[i + 1]["longitude"]

        # 转换坐标到H3索引
        origin_h3 = h3.geo_to_h3(lat1, lon1, 9)
        destination_h3 = h3.geo_to_h3(lat2, lon2, 9)

        # 计算两个H3索引之间的距离
        index_distance = h3.h3_distance(origin_h3, destination_h3) * 1000
        # 计算实际的距离
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
        print(f"i:{i},j:{i + 1} ->相邻元素坐标距离: {distance:.2f}米，索引距离: {index_distance:.2f}")


def main():
    if len(sys.argv) < 4:
        print(
            "参数说明: python3 start.py <经度 纬度> （生成的坐标数量：number <10 矩阵为3*4; number > 10 && number < 20 矩阵为4*6 以此推类）;" +
            "\r\n使用示例：python.exe main.py 113.90446771229699 22.578703313545564 8")
        return

    try:
        longitude = float(sys.argv[1])
        latitude = float(sys.argv[2])
        # print(f"输入经度: {longitude},输入纬度{latitude}")
        number = int(sys.argv[3])
        rows, cols = get_rows_and_cols(number)

        matrix_coords = get_matrix_coordinates(latitude, longitude, rows, cols)
        #print("矩阵为： ", rows, "*", cols, "生成的坐标数量：", len(matrix_coords))
        random.shuffle(matrix_coords)
        print(json.dumps(matrix_coords))
    except ValueError as e:
        print(f"错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")


if __name__ == "__main__":
    main()
