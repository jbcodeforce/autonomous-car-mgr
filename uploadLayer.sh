aws lambda publish-layer-version --layer-name common-python3 \
    --description "A layer for some python lambda" \
    --license-info "MIT" \
    --zip-file fileb://package.zip \
    --compatible-runtimes python3.10 python3.11 \
    --compatible-architectures "arm64" "x86_64"