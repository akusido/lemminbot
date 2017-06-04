####Postprocess frames into thumbnails with `jpegtran`:

```PowerShell
SET exe="\\path\to\cjpeg\or\mozjpeg"

forfiles *.jpg /C "%exe% -crop "WxHf+X+Y" -outfile '%~ni.thumb.jpg' '%~i'"
```


####Stack processed frames into quads and produce a timelapse with ```ffmpeg```

```shell
cd "//frames/first" && ffmpeg -i "%4d.thumb.jpg" -c copy "../topleft.mpeg"
cd "//frames/second" && ffmpeg -i "%4d.thumb.jpg" -c copy "../topright.mpeg"
cd "//frames/third" && ffmpeg -i "%4d.thumb.jpg" -c copy "../botleft.mpeg"
cd "//frames/fourth" && ffmpeg -i "%4d.thumb.jpg" -c copy "../botright.mpeg"

ffmpeg -i topleft.mpeg -i botleft.mpeg -i topright.mpeg -i botright.mpeg -i sidebar.mp4 -filter_complex \
"[0][1]vstack[lefthalf];[2][3]vstack[righthalf];[lefthalf][righthalf][4]hstack=inputs=3[v]" \
-c:v libx264 %custom_encoding_parameters% output_timelapse.mp4
```

