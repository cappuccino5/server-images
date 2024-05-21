#!/bin/bash

function show_help() {
    echo "Usage: $0 [--help|-h] <latitude> <longitude>"
    echo "  --help, -h    Show this help message"
    echo "  longitude     Longitude coordinate (decimal format)"
    echo "  latitude      Latitude coordinate (decimal format)"
    echo ""
    echo "Example:"
    echo "  $0 114.04 22.62"
    exit 0
}

if [ "$#" -ne 2 ] && [ "$1" != "--help" ] && [ "$1" != "-h" ]; then
    echo "Error: Incorrect number of arguments."
    show_help
fi

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
fi

lonData=$1
latData=$2
password=""

# 需要定位的热点数量，根据hotspots_default_asserts标志位统计得出
hotspots_count=0

#hotspots_default_asserts通过命令获取而来，参数："location_asserts"。默认为0表示新设备重来未定位过
# helium-wallet hotspots info 112EvoKhDQRAXeMTpX5uqZRaa9Mt9JMv8Dz814L6CyLN5eNmQwqG
hotspots_default_asserts=0

add_hotspots_count() {
    hotspots_list=$(helium-wallet hotspots list)
    hotspot_keys=$(echo "$hotspots_list" | jq -r '.hotspots[].key')
    for key in $hotspot_keys; do
         hotspot_info=$(helium-wallet hotspots info ${key})
         location_asserts=$(echo "$hotspot_info" | jq -r '.info.iot.location_asserts')
         echo "热点： $key 定位次数 $location_asserts"
         if [ "$location_asserts" == $hotspots_default_asserts ]; then
              ((hotspots_count=hotspots_count+1))
         fi
done
}

add_coordinates(){
  result=$(python3.6 /etc/helium/get_coordinates.py $lonData $latData $hotspots_count)
    IFS='[],' read -ra coordinates <<< "$result"

   local index=0
    hotspots_list=$(helium-wallet hotspots list)
    hotspot_keys=$(echo "$hotspots_list" | jq -r '.hotspots[].key')
    for key in $hotspot_keys; do
         hotspot_info=$(helium-wallet hotspots info ${key})
         location_asserts=$(echo "$hotspot_info" | jq -r '.info.iot.location_asserts')
         echo "热点： $key 定位次数 $location_asserts"
         if [ "$location_asserts" == $hotspots_default_asserts ]; then
          latitude=$(echo "${coordinates[$index*2+1]}" | awk -F':' '{print $2}' | tr -d '",')
          longitude=$(echo "${coordinates[$index*2+2]}" | awk -F':' '{print $2}' | tr -d '",}')
          echo "hotspots_key: $key,Latitude: $latitude, Longitude: $longitude"
          hotspots_asserts "$key" "$latitude" "$longitude"
          ((index=index+1))
         fi
done
}

hotspots_asserts() {
    local key=$1
    local latitude=$2
    local longitude=$3

    if [ -z "$password" ]; then
        echo "Please enter the wallet password:"
        read -s password
        echo ""
    fi

    expect -c "
        set timeout 60
        spawn helium-wallet hotspots assert --commit --lat $latitude --lon $longitude --elevation 20 --gain 1.5 iot $key
        expect \"Wallet Password:\"
        send \"$password\r\"
        expect eof
    "

    if [ $? -eq 0 ]; then
        echo "Executed command: helium-wallet hotspots assert --commit --lat $latitude --lon $longitude --elevation 20 --gain 1.5 iot $key"
    else
        echo "Error executing assert command for key: $key"
        echo "Aborting further execution."
        exit 1
    fi

    # 休眠一段时间，以便等待 assert 命令执行完成
    sleep 10
}

main() {
    add_hotspots_count   # ok
    echo "$hotspots_count"
    if [ "$hotspots_count" == "0" ]; then
        echo "Skipping .... not need coordinates $hotspots_count"
      return
    fi
    echo "开始执行批量定位：需要定位的热点数量 $hotspots_count"
    add_coordinates
}

main
