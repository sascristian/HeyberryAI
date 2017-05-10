# mycroft---astronomy-picture-of-teh-day

save and display astronomy picture of the day

# not fully compatible with msm because of opencv

# usage

      astronomy picture of the day

      
# API

      add a NASAAPI section to you config file, [NASA API](https://api.nasa.gov/index.html#apply-for-an-api-key)
      or use DEMO_KEY for limited rates

# requires

- open-cv

            sudo apt-get install python-opencv

https://medium.com/@manuganji/installation-of-opencv-numpy-scipy-inside-a-virtualenv-bf4d82220313

(pip install doesnt work in my system)


# config file

add:
- "NASAAPI" : "api key to id pic contents"
- "save_path" "home/user/save_pics_here"
- "txt_path" : "home/user/save_apod_description.txt_here"
