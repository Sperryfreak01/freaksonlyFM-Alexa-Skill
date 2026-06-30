.PHONY: install package deploy clean

install:
	pip3 install -r lambda/requirements.txt -t lambda/

package: install
	cd lambda && zip -r ../freaks-only-fm.zip . -x "*.pyc" -x "__pycache__/*"

deploy:
	ask deploy

clean:
	rm -rf lambda/ask_sdk* lambda/boto* lambda/dateutil lambda/urllib3* lambda/six* freaks-only-fm.zip
