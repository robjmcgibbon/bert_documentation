#! /bin/bash

map_name=gas_map_temp_8192
for map_name in gas_map_temp_8192 gas_map_sigma_8192 gas_map_xray_8192 \
  dm_map_sigma_8192 star_map_sigma_8192
do
  files=""
  for i in $(seq -w 0000 0078)
  do
    files="${files} flamingo_${i}_${map_name}.png"
  done
  fr=4

  # piping the image names directly into `ffmpeg` makes it possible to create
  # more complex videos, like a video where you first zoom in using all frames,
  # and then zoom out again more quickly by only repeating a subset of the
  # frames
  # the exact set of frames really only depends on the order of the file names
  # in the ${files} variable
  cat $files | ffmpeg -y -f png_pipe -framerate $fr -i - \
    -s 600x600 -c:v libx264 -r $fr -pix_fmt yuv420p ${map_name}.mp4

done
