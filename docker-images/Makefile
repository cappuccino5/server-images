wallet:
	#docker context use default
	docker buildx build -t registry.cn-shenzhen.aliyuncs.com/hujian/helium-wallet --platform linux/amd64 -f Dockerfile_helium_wallet --push .

ntp:
	docker buildx build -t registry.cn-shenzhen.aliyuncs.com/hujian/ntp:1.0.0 --platform linux/amd64 -f Dockerfile_ntp --push .

golang_build:
	docker context use default
	docker buildx build -t registry.cn-shenzhen.aliyuncs.com/hujian/golang-build:latest --platform linux/amd64 -f Dockerfile_golang_build --push .

