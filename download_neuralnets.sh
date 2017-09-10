TOP=$(cd $(dirname $0) && pwd -L)

# google inception for deep dream
cd ${TOP}/jarbas_models/tf_inception/
./download.sh

# black and white colorization model
cd ${TOP}/jarbas_models/tf_colorize/models
./download_pre_trained.sh

# download vgg16
cd ${TOP}/jarbas_models/tf_vgg16
./download.sh

# download vgg19
cd ${TOP}/jarbas_models/tf_vgg19
./download.sh