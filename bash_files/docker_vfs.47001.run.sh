
curl -X POST http://0.0.0.0:47001/run \
  -H "Content-Type: application/json" \
  -d '{"vid_content_meta_url": "/mnt/SHARED/VTR/20211119_cc1/Output/20211119_cc1.vcm.json",
       "src_vid_url":"/mnt/SHARED/VTR/20211119_cc1/Input/20211119_cc1.mp4",
       "infected_picture_url":"./Input/infected_face1.png",
       "rst_vid_url":"/mnt/SHARED/VFS/20211119_cc1/Output/20211119_cc1.vfs.mp4",
       "rst_img_folder_url":"/mnt/SHARED/VFS/20211119_cc1/Details",
       "N": "100"}'
#   -d '{"vid_content_meta_url": "./Input/S#_5_6_7_8/S#_5_6_7_8.vcm.json",
#        "src_vid_url":"./Input/S#_5_6_7_8/S#_5_6_7_8.mp4",
#        "infected_picture_url":"./Input/S#_5_6_7_8/infected_face.png",
#        "rst_vid_url":"./Client/S#_5_6_7_8.vfs.mp4",
#        "rst_img_folder_url":"./Client/Details",
#        "N": "100"}'
