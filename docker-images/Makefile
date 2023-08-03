wallet:
	#docker context use default
	docker buildx build -t swr.cn-north-4.myhuaweicloud.com/kelley/helium-wallet --platform linux/amd64 -f Dockerfile_helium_wallet --push .

ntp:
	docker buildx build -t swr.cn-north-4.myhuaweicloud.com/kelley/ntp:1.1 --platform linux/amd64 -f Dockerfile_ntp --push .

golang_build:
	docker context use default
	docker buildx build -t swr.cn-north-4.myhuaweicloud.com/kelley/golang-build:latest --platform linux/amd64 -f Dockerfile_golang_build --push .

