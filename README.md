# 常用的服务组件


##  minio：

运行minio

``` docker-compose -f docker-compose-minio.yml  up -d```

命令行执行：

``` docker run  -p 19001:19001 -e  MINIO_ROOT_USER=minio -e MINIO_ROOT_PASSWORD=miniostorage -p 19000:19000  minio/minio server /data --console-address ":19000" --address ":19001"  ```

- 19000端口是web管理平台

- 19001端口是api调用


api调用项目配置:
```
[minio]
endpoint_addr="minio:19001"
bucket="default"
user="minio"
password="miniostorage"
```

参考：

- https://github.com/minio/minio

## nginx
command：``` docker-compose -f docker-compose-nginx.yml up ```

nginx/nginx.conf修改web服务：
- proxy_pass中serverName-web 是web服务，在同一个docker-compose里可以描述为：xxx-web:port


nginx/nginx.conf修改后端服务：

- proxy_pass中serverName 是后端服务，在同一个docker-compose里可以描述为：xxx:port
 
用法参考：
- https://www.nginx.cn/doc/example/fullexample.html
- https://www.nginx.cn/doc/example/fullexample2.html

## storage

command：``` docker-compose -f docker-compose-storage.yml up ```
### redis5

默认没有密码，注意不要对外暴露端口，因为容易被攻击，内网访问即可

### postgres13


###  我的个人博客

docker-compose -f docker-compose-blogs.yml up

配置文件：
- postgresql13/postgresql.conf
- postgresql13/initdb/业务数据库.conf(初始化业务数据库示例)


## docker-images
docker-images 是描述dockerfile生成镜像，有ntp、golang环境、helium_wallet 生成镜像





