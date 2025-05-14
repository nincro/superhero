build_pb:
	rm -rf vendor
	mkdir vendor
	python -m grpc_tools.protoc \
    --proto_path=proto \
    --python_out=vendor \
    --grpc_python_out=vendor \
    proto/superhero.proto

freeze:
	pip freeze > requirements.txt

install:
	pip install -r requirements.txt