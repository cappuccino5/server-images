import subprocess
import json
import os
import time
import argparse
import sys
import re
import random
from get_coords import Coordinates


class Location:

    def __init__(self, h3_index, latitude, longitude, skip_list):
        self.coord_generate = Coordinates([])
        self.hotspots_count = 0
        self.h3_index = h3_index
        self.latitude = latitude
        self.longitude = longitude
        self.skip_list = skip_list
        self.hotspot_keys = []

    def trim_string(self, input_string):
        return input_string.strip()

    def find_hotspots_count(self):
        hotspots_list = subprocess.check_output(["helium-wallet", "hotspots", "list"]).decode().strip()
        hotspot_keys_list = json.loads(hotspots_list)["hotspots"]
        hotspots_count = 0
        for key in hotspot_keys_list:
            hotspot_info = subprocess.check_output(["helium-wallet", "hotspots", "info", key["key"]]).decode().strip()
            location_asserts = json.loads(hotspot_info)["info"]["iot"]["location_asserts"]
            print(f"Hotspot: {key['key']} Location Asserts: {location_asserts}")
            if location_asserts == hotspots_default_asserts:
                self.hotspot_keys.append(key["key"])
                hotspots_count += 1

        self.hotspots_count = hotspots_count
        return

    def add_hotspots_count(self, hotspot_keys):
        self.find_hotspots_count()
        for key in hotspot_keys:
            self.hotspot_keys.append(key)
        self.hotspots_count = self.hotspots_count + len(hotspot_keys)
        return

    def add_coordinates(self):
        matrix_coords = []
        if self.latitude > 0 and self.longitude > 0:
            matrix_coords = self.coord_generate.get_coordinates_form_lat_and_long(self.latitude, self.longitude,
                                                                                  self.hotspots_count)
        elif self.h3_index != "":
            matrix_coords = self.coord_generate.get_coordinates_form_index(self.h3_index,
                                                                           self.hotspots_count)
        print(f" get matrix_coords size: {len(matrix_coords)}")
        if len(matrix_coords) < self.hotspots_count:
            print(f" {len(matrix_coords)} matrix_coords required than hotspots_count: {self.hotspots_count}")
            return

        random.shuffle(matrix_coords)
        for i, key in enumerate(self.hotspot_keys):
            latitude = matrix_coords[i]["latitude"]
            longitude = matrix_coords[i]["longitude"]
            print(f"{i} Hotspot Key: {key}, Latitude: {latitude}, Longitude: {longitude}")
            self.hotspots_asserts(key, latitude, longitude)

    def hotspots_asserts(self, key, latitude, longitude):
        password = os.getenv("WALLET_PASSWORD", "")
        if not password:
            password = input("Please enter the wallet password: ")
            os.environ["WALLET_PASSWORD"] = password
            # os.putenv("WALLET_PASSWORD", password)
        try:
            command = f"helium-wallet hotspots update --commit --lat={latitude} --lon={longitude} --elevation={elevation} --gain={gain} iot {key}"
            print(f"Executing command: {command}")
            result = subprocess.run(["expect", "-c", f"""
                        set timeout 60
                        spawn {command}
                        expect "Wallet Password:"
                        send "{password}\\r"
                        expect eof
                    """], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    universal_newlines=True, check=True)
            print(result.stdout)
        except subprocess.CalledProcessError as e:
            print(f"Error executing update command for key: {key}")
            print("Stderr:")
            print(e.stderr)
            print("Aborting further execution.")
            exit(1)
        time.sleep(10)  # Wait for assert command to complete


def main(args):
    global elevation
    global gain
    global hotspots_default_asserts
    hotspots_default_asserts = 0
    latitude = args.latitude
    longitude = args.longitude
    h3_index = args.hex
    elevation = args.elevation
    gain = args.gain
    skip_list = args.skip
    hotspot_keys = args.keys
    if h3_index == "" and latitude <= 0:
        print("latitude or h3_index not is null")
        return
    loc = Location(h3_index, latitude, longitude, skip_list)
    # todo del add_hotspots_count
    loc.add_hotspots_count(hotspot_keys)
    print(f"Starting batch location: Number of hotspots to locate {loc.hotspots_count}, hotspot_keys: {hotspot_keys}")
    if loc.hotspots_count == 0:
        print("Skipping .... no need for coordinates")
        return
    loc.add_coordinates()


def parse_args():
    process_name = str(sys.argv[0])
    parser = argparse.ArgumentParser(description="Helium Get batch coordinates",
                                     epilog=f"""Example usage:
            {process_name} -x 881fb2810dfffff 
            {process_name} -x 881fb2810dfffff  -skip 881fb2810dfffff,881fb28105fffff
            {process_name} -lat 47.7247769110229 -lon 2.108315381765773 
            {process_name} -lat 47.7247769110229 -lon 2.108315381765773 -skip 881fb2810dfffff,881fb28105fffff
            {process_name} -lat 47.7247769110229 -lon 2.108315381765773 -k 112EvoKhDQRAXeMTpX5uqZRaa9Mt9JMv8Dz814L6CyLN5eNmQwqG,122EvoKhDQRAXeMTpX5uqZRaa9Mt9JMv8Dz814L6CyLN5eNmQwqG
            {process_name} -x 881fb2810dfffff  -skip 881fb2810dfffff,881fb28105fffff -k 112EvoKhDQRAXeMTpX5uqZRaa9Mt9JMv8Dz814L6CyLN5eNmQwqG,122EvoKhDQRAXeMTpX5uqZRaa9Mt9JMv8Dz814L6CyLN5eNmQwqG
            """,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    # 定义参数
    parser.add_argument("-k", "--keys", type=str, required=False, default='',
                        help="onboarding keys (optional)")
    parser.add_argument("-lat", "--latitude", type=float, required=False,
                        default=0.0, help="Latitude coordinate (optional)")
    parser.add_argument("-lon", "--longitude", type=float, required=False, default=0.0,
                        help="Longitude coordinate (optional)")
    parser.add_argument("-x", "--hex", type=str, required=False, default='',
                        help="Longitude and latitude index (optional)")
    parser.add_argument("-skip", "--skip", type=str, required=False, default='',
                        help="Comma-separated list of hex values to skip (optional)")

    parser.add_argument("-e", "--elevation", type=int, required=False, default=15,
                        help="elevation     Elevation in meters (optional default: 15)")
    parser.add_argument("-g", "--gain", type=float, required=False, default=1.5,
                        help="gain Antenna gain in dBi (optional default: 1.5)")

    args = parser.parse_args()

    if args.keys:
        args.keys = re.split(r',\s*', args.keys)

    if args.skip:
        args.skip = re.split(r',\s*', args.skip)

    return args


if __name__ == "__main__":
    args = parse_args()
    main(args)
