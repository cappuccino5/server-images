#!/bin/bash

function show_help() {
    echo "Usage: $0 [--help|-h] <keys> <longitude> <latitude> [<elevation>] [<gain>]"
    echo "  --help, -h    Show this help message"
    echo "  keys     Comma-separated list of keys: 'use,'"
    echo "  longitude     Longitude coordinate (decimal format)"
    echo "  latitude      Latitude coordinate (decimal format)"
    echo "  elevation     Elevation in meters (default: 20)"
    echo "  gain     Antenna gain in dBi (default: 1.5)"
    echo "Example:"
    echo "  $0 key1,key2,key3 114.04 22.62"
    echo "  $0 key1,key2,key3 114.04 22.62 22"
    echo "  $0 key1,key2,key3 114.04 22.62 22 1.6"
    exit 0
}

if  [[ "$#" -ne 2 && "$#" -ne 4 && "$#" -ne 3 && "$#" -ne 5 ]] && [ "$1" != "--help" ] && [ "$1" != "-h" ]; then
    echo "Error: Incorrect number of arguments."
    show_help
fi

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    show_help
fi

hotspot_keys=$1
lonData=$2
latData=$3
elevation=$4
gain=$5
password=""

# 需要定位的热点数量，根据hotspots_default_asserts标志位统计得出
hotspots_count=0

#hotspots_default_asserts通过命令获取而来，参数："location_asserts"。默认为0表示新设备重来未定位过
# helium-wallet hotspots info 112EvoKhDQRAXeMTpX5uqZRaa9Mt9JMv8Dz814L6CyLN5eNmQwqG
hotspots_default_asserts=0

# todo 记得同步修改
if [ -z "$4" ]; then
        elevation=15
    else
        elevation=$4
    fi

    if [ -z "$5" ]; then
        gain=1.5
    else
        gain=$5
 fi

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

add_hotspots_countV2() {
     local keys=$1
     local hotspots_list
     local hotspots_keys=()
    IFS=',' read -ra hotspots_list <<< "$keys"
    for key in "${hotspots_list[@]}"; do
         echo "查询热点状态：$key"
         hotspot_info=$(helium-wallet hotspots info ${key})
         info_item=$(echo "$hotspot_info" | jq -r '.info')
         if [ "$info_item" == "{}" ] ; then
             hotspots_keys+=("$key")
             echo "热点： $key 定位次数 无 $info_item"
             ((hotspots_count=hotspots_count+1))
             continue
         fi
         location_asserts=$(echo "$hotspot_info" | jq -r '.info.iot.location_asserts')
         echo "热点： $key 定位次数 $location_asserts"
         if [ "$location_asserts" == $hotspots_default_asserts ] || [ "$location_asserts" == nil ]; then
              hotspots_keys+=("$key")
              ((hotspots_count=hotspots_count+1))
              continue
         fi
    done
#    echo "需要定位的有效热点keys：${hotspots_keys[@]}"
}

add_coordinatesV2(){
  result=$(python3.6 /etc/helium/get_coordinates.py $lonData $latData $hotspots_count)
    IFS='[],' read -ra coordinates <<< "$result"

   local index=0
   local keys=$1
   local hotspots_list
    IFS=',' read -ra hotspots_list <<< "$keys"
    for key in "${hotspots_list[@]}"; do
         hotspot_info=$(helium-wallet hotspots info ${key})
         info_item=$(echo "$hotspot_info" | jq -r '.info')
         if [ "$info_item" == "{}" ] ; then
          ((hotspots_count=hotspots_count+1))
          latitude=$(echo "${coordinates[$index*2+1]}" | awk -F':' '{print $2}' | tr -d '",')
          longitude=$(echo "${coordinates[$index*2+2]}" | awk -F':' '{print $2}' | tr -d '",}')
          echo "hotspots_key: $key,Latitude: $latitude, Longitude: $longitude"
          hotspots_asserts "$key" "$latitude" "$longitude"
          ((index=index+1))
          continue
         fi
         location_asserts=$(echo "$hotspot_info" | jq -r '.info.iot.location_asserts')
         if [ "$location_asserts" == $hotspots_default_asserts ]; then
          latitude=$(echo "${coordinates[$index*2+1]}" | awk -F':' '{print $2}' | tr -d '",')
          longitude=$(echo "${coordinates[$index*2+2]}" | awk -F':' '{print $2}' | tr -d '",}')
          echo "hotspots_key: $key,Latitude: $latitude, Longitude: $longitude"
          hotspots_asserts "$key" "$latitude" "$longitude"
          ((index=index+1))
          continue
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
          echo "hotspot_key: $key,Latitude: $latitude, Longitude: $longitude"
          hotspots_asserts "$key" "$latitude" "$longitude"
          ((index=index+1))
         fi
done
}

trim_string() {
    local input_string="$1"
    local trimmed_string
    trimmed_string=$(echo "$input_string" | sed -e 's/^\s*//g' -e 's/\s*$//g' -e 's/\s\s*/ /g')
    echo "$trimmed_string"
}

hotspots_asserts() {
    local key=$1
    local latitude=$2
    local longitude=$3

   lon=$(trim_string "$longitude")
   lat=$(trim_string "$latitude")

    if [ -z "$password" ]; then
        echo "Please enter the wallet password:"
        read -s password
        echo ""
    fi

    expect -c "
        set timeout 60
        spawn helium-wallet hotspots assert --commit --lat=$lat --lon=$lon --elevation=$elevation --gain=$gain iot $key
        expect \"Wallet Password:\"
        send \"$password\r\"
        expect eof
    "

    if [ $? -eq 0 ]; then
        echo "Executed command: helium-wallet hotspots assert --commit --lat=$lat --lon=$lon --elevation=$elevation --gain=$gain iot $key"
    else
        echo "Error executing assert command for key: $key"
        echo "Aborting further execution."
        exit 1
    fi

    # 休眠一段时间，以便等待 assert 命令执行完成
    sleep 10
}

main() {
    add_hotspots_countV2 "$hotspot_keys"
    echo "开始执行批量定位：需要定位的热点数量 $hotspots_count"
    if [ "$hotspots_count" == "0" ]; then
        echo "Skipping .... not need coordinates $hotspots_count"
      return
    fi
    add_coordinatesV2 "$hotspot_keys"
}

main